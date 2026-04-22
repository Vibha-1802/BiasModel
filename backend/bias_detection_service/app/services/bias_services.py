from __future__ import annotations

import math
from io import StringIO
from itertools import combinations

import numpy as np
import pandas as pd
from fastapi import HTTPException
import httpx
from scipy.stats import chi2_contingency, pointbiserialr

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_FILE_SIZE_MB = 10

FAVORABLE_LABEL_HINTS = {
    "1", "true", "yes", "y", "approved", "approve", "accepted",
    "selected", "shortlisted", "hired", "admitted", "granted",
    "pass", "positive", "favorable", "good",
}

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _f(val) -> float:
    """Convert any pandas/numpy scalar to Python float.
    pandas 3.x stubs type .skew()/.kurtosis() as the broad Scalar union (which
    includes complex), so float() raises a pyright error. This helper isolates
    the single suppression and is safe at runtime because numeric Series always
    produce real-valued moments."""
    return float(val)  # type: ignore[arg-type]


def clean_nan(obj):
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nan(v) for v in obj]
    if isinstance(obj, (float, np.floating)):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return float(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    return obj


def is_binary_series(series: pd.Series) -> bool:
    unique_vals = set(series.dropna().unique().tolist())
    if len(unique_vals) != 2:
        return False
    # Check numeric/boolean true binary
    if unique_vals.issubset({0, 1, 0.0, 1.0, False, True}):
        return True
    
    # Check common string binary pairs
    lower_vals = {str(v).strip().lower() for v in unique_vals}
    valid_string_pairs = [
        {"y", "n"}, {"yes", "no"}, {"true", "false"}, {"t", "f"}, 
        {"pass", "fail"}, {"approve", "reject"}, {"approved", "rejected"}
    ]
    return lower_vals in valid_string_pairs


def is_categorical(series: pd.Series) -> bool:
    return (
        pd.api.types.is_object_dtype(series)
        or isinstance(series.dtype, pd.CategoricalDtype)
        or pd.api.types.is_bool_dtype(series)
    )


# ---------------------------------------------------------------------------
# Target / label inference
# ---------------------------------------------------------------------------


def infer_target_type(series: pd.Series) -> str:
    n_unique = series.dropna().nunique()
    if n_unique == 2:
        return "binary"
    # Numeric with many unique values → continuous; few unique values → ordinal/multiclass
    if pd.api.types.is_numeric_dtype(series):
        return "continuous" if n_unique > 20 else "multiclass"
    return "multiclass" if n_unique > 2 else "continuous"


def infer_positive_class_label(series: pd.Series):
    non_null = series.dropna()
    if non_null.empty:
        return None
    lowered_map = {str(val).strip().lower(): val for val in non_null.unique()}
    for hint in FAVORABLE_LABEL_HINTS:
        if hint in lowered_map:
            return lowered_map[hint]
    if is_binary_series(non_null):
        return 1
    counts = non_null.value_counts()
    return counts.idxmin() if len(counts) == 2 else counts.idxmax()


def to_binary_indicator(series: pd.Series, positive_label) -> pd.Series | None:
    if positive_label is None:
        return None
    return (series == positive_label).astype(int)

# ---------------------------------------------------------------------------
# Binning helpers
# ---------------------------------------------------------------------------

def qcut_series(series: pd.Series, q: int = 4) -> pd.Series | None:
    clean = series.dropna()
    if clean.empty or clean.nunique() < 2:
        return None
    try:
        return pd.qcut(clean, q=min(q, clean.nunique()), duplicates="drop")
    except ValueError:
        return None


def build_quantile_bins(series: pd.Series) -> dict:
    quantile_bins = qcut_series(series, q=4)
    if quantile_bins is None:
        return {}
    counts = quantile_bins.value_counts().sort_index()
    return {str(interval): int(count) for interval, count in counts.items()}


def _group_series_for_protected(df: pd.DataFrame, col: str) -> pd.Series:
    """
    Return the grouping series for a protected attribute column.
    Numerical columns are binned into quartiles to avoid one-group-per-value explosion.
    """
    series = df[col]
    if pd.api.types.is_numeric_dtype(series) and not is_binary_series(series):
        binned = qcut_series(series, q=4)
        if binned is not None:
            return binned.astype(str)
    return series

# ---------------------------------------------------------------------------
# Association / correlation
# ---------------------------------------------------------------------------

def cramers_v(confusion_matrix: pd.DataFrame) -> float | None:
    if confusion_matrix.empty or min(confusion_matrix.shape) < 2:
        return None
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    r, k = confusion_matrix.shape
    denom = n * min(k - 1, r - 1)
    if denom <= 0:
        return None
    return float(np.sqrt(chi2 / denom))


def compute_association(left: pd.Series, right: pd.Series) -> dict | None:
    aligned = pd.concat([left, right], axis=1).dropna()
    if aligned.empty:
        return None

    x, y = aligned.iloc[:, 0], aligned.iloc[:, 1]

    x_is_cat = is_categorical(x)
    y_is_cat = is_categorical(y)
    x_is_binary = is_binary_series(x) if (pd.api.types.is_numeric_dtype(x) or pd.api.types.is_bool_dtype(x)) else x.nunique() == 2
    y_is_binary = is_binary_series(y) if (pd.api.types.is_numeric_dtype(y) or pd.api.types.is_bool_dtype(y)) else y.nunique() == 2

    try:
        # Continuous numeric vs binary (point-biserial)
        if pd.api.types.is_numeric_dtype(x) and not x_is_binary and y_is_binary:
            encoded = to_binary_indicator(y, infer_positive_class_label(y))
            if encoded is None:
                return None
            corr, p = pointbiserialr(x, encoded)
            return {"method": "point_biserial", "value": float(corr), "p_value": float(p)}

        if pd.api.types.is_numeric_dtype(y) and not y_is_binary and x_is_binary:
            encoded = to_binary_indicator(x, infer_positive_class_label(x))
            if encoded is None:
                return None
            corr, p = pointbiserialr(y, encoded)
            return {"method": "point_biserial", "value": float(corr), "p_value": float(p)}

        # Both categorical → Cramér's V
        if x_is_cat and y_is_cat:
            ct = pd.crosstab(x, y)
            if ct.empty or min(ct.shape) < 2:
                return None
            _, p, _, _ = chi2_contingency(ct)
            v = cramers_v(ct)
            if v is None:
                return None
            return {"method": "cramers_v", "value": v, "p_value": float(p)}

        # Categorical vs numeric → if numeric is binary use it as-is, otherwise bin then Cramér's V.
        # Binning a binary series (e.g. shortlisted 0/1) with qcut always collapses into 1 bin,
        # making crosstab have shape (n,1) and returning None. Treat binary numerics as categorical.
        if x_is_cat and pd.api.types.is_numeric_dtype(y):
            if y_is_binary:
                ct = pd.crosstab(x, y.astype(str))
            else:
                y_binned = qcut_series(y, q=10)
                if y_binned is None:
                    return None
                ct = pd.crosstab(x.loc[y_binned.index], y_binned)
            if ct.empty or min(ct.shape) < 2:
                return None
            _, p, _, _ = chi2_contingency(ct)
            v = cramers_v(ct)
            if v is None:
                return None
            method = "cramers_v" if y_is_binary else "cramers_v_binned"
            return {"method": method, "value": v, "p_value": float(p)}

        if y_is_cat and pd.api.types.is_numeric_dtype(x):
            if x_is_binary:
                ct = pd.crosstab(x.astype(str), y)
            else:
                x_binned = qcut_series(x, q=10)
                if x_binned is None:
                    return None
                ct = pd.crosstab(x_binned, y.loc[x_binned.index])
            if ct.empty or min(ct.shape) < 2:
                return None
            _, p, _, _ = chi2_contingency(ct)
            v = cramers_v(ct)
            if v is None:
                return None
            method = "cramers_v" if x_is_binary else "cramers_v_binned"
            return {"method": method, "value": v, "p_value": float(p)}

    except Exception:
        return None

    return None

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

async def process_dataset(file):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    contents = await file.read()

    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large. Max allowed is {MAX_FILE_SIZE_MB} MB")

    try:
        df = pd.read_csv(StringIO(contents.decode("utf-8")))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV format")

    if df.empty:
        raise HTTPException(status_code=400, detail="CSV has no data")

    return {
        "filename": file.filename,
        "rows": len(df),
        "columns": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
    }


async def analyze_dataset(file):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV allowed")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large. Max allowed is {MAX_FILE_SIZE_MB} MB")

    try:
        df = pd.read_csv(StringIO(contents.decode("utf-8")))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV format")

    if df.empty:
        raise HTTPException(status_code=400, detail="CSV has no data")

    total_rows = len(df)
    column_names = list(df.columns)
    
    # ── CATEGORY 1.5: Schema Inference via LLM ──────────────────────────────
    target_column = None
    protected_columns = []
    dataset_domain = "unknown"
    has_model_predictions = False

    try:
        sample_data = df.head(3).to_dict(orient="records")
        # Ensure values are JSON serializable
        safe_sample = [clean_nan(row) for row in sample_data]
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://localhost:8001/infer_schema", 
                json={
                    "columns": column_names,
                    "sample_data": safe_sample
                },
                timeout=30.0
            )
            if resp.status_code == 200:
                schema = resp.json()
                print(f"LLM Response Schema: {schema}")
                target_column = schema.get("target_column")
                protected_columns = schema.get("protected_columns", [])
                dataset_domain = schema.get("dataset_domain", "unknown")
                has_model_predictions = schema.get("has_model_predictions", False)
                
                # Validate the LLM output against actual columns
                if target_column not in column_names:
                    print(f"Target column '{target_column}' not in {column_names}")
                    target_column = None
                protected_columns = [col for col in protected_columns if col in column_names]
            else:
                print(f"LLM API Error: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"LLM Schema inference failed with exception: {e}")
        
    # Fallback if LLM fails or doesn't find target
    if not target_column:
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]) and is_binary_series(df[col]):
                target_column = col
                break
        if not target_column and not df.empty:
            target_column = df.columns[-1]

    # ── CATEGORY 1: Dataset fundamentals ────────────────────────────────────
    column_dtypes = {
        col: "numerical" if pd.api.types.is_numeric_dtype(df[col]) else "categorical"
        for col in df.columns
    }
    missing_values = {
        col: {
            "count": int(df[col].isnull().sum()),
            "percentage": float(df[col].isnull().mean() * 100),
        }
        for col in df.columns
    }
    duplicate_count = int(df.duplicated().sum())

    # ── CATEGORY 2: Target analysis ─────────────────────────────────────────
    target_type = None
    class_distribution: dict = {}
    positive_class_label = None
    imbalance_ratio = None
    base_rate = None

    if target_column:
        target_series = df[target_column]
        target_type = infer_target_type(target_series)

        if target_type in ("binary", "multiclass"):
            counts = target_series.value_counts()
            total = counts.sum()
            for cls, count in counts.items():
                class_distribution[str(cls)] = {
                    "count": int(count),
                    "percentage": float(count / total * 100),
                }
            majority, minority = int(counts.max()), int(counts.min())
            imbalance_ratio = float(majority / minority) if minority > 0 else None
            positive_class_label = infer_positive_class_label(target_series)
            if positive_class_label is not None and positive_class_label in counts.index:
                base_rate = float(counts[positive_class_label] / total)

    # ── CATEGORY 3: Numerical summary ───────────────────────────────────────
    numerical_summary: dict = {}
    for col in df.select_dtypes(include="number").columns:
        series = df[col].dropna()
        if series.empty:
            continue
        numerical_summary[col] = {
            "min": float(series.min()),
            "max": float(series.max()),
            "mean": float(series.mean()),
            "median": float(series.median()),
            "std": float(series.std()),
            "percentiles": {
                "25": float(series.quantile(0.25)),
                "50": float(series.quantile(0.50)),
                "75": float(series.quantile(0.75)),
                "90": float(series.quantile(0.90)),
                "95": float(series.quantile(0.95)),
            },
            "suggested_bins": build_quantile_bins(series),
        }

    # ── CATEGORY 4: Group outcome stats ─────────────────────────────────────
    # Numerical protected attributes are binned into quartiles so we never produce
    # one-group-per-unique-value (which would create hundreds of tiny groups for
    # float columns like age and break the LLM context).
    group_outcome_stats: dict = {}
    preliminary_bias_signals: dict = {}

    if target_column and target_type == "binary":
        target_indicator = to_binary_indicator(df[target_column], positive_class_label)

        for col in protected_columns:
            group_series = _group_series_for_protected(df, col)
            working = pd.DataFrame({
                col: group_series,
                "__t__": target_indicator,
            }).dropna(subset=[col, "__t__"])
            grouped = working.groupby(col)["__t__"].agg(["count", "sum", "mean"])

            col_stats: dict = {}
            rates: list[float] = []

            for grp, row in grouped.iterrows():
                count = int(row["count"])
                positive = int(row["sum"])
                rate = float(row["mean"]) if count > 0 else 0.0
                col_stats[str(grp)] = {
                    "count": count,
                    "positive_count": positive,
                    "positive_rate": rate,
                }
                rates.append(rate)

            group_outcome_stats[col] = col_stats

            if rates:
                max_r, min_r = max(rates), min(rates)
                most_favored = max(col_stats, key=lambda k: col_stats[k]["positive_rate"])
                least_favored = min(col_stats, key=lambda k: col_stats[k]["positive_rate"])
                preliminary_bias_signals[col] = {
                    "statistical_parity_difference": float(min_r - max_r),
                    "disparate_impact_ratio": float(min_r / max_r) if max_r > 0 else None,
                    "most_favored_group": most_favored,
                    "least_favored_group": least_favored,
                    "rate_spread": float(max_r - min_r),
                }

    # ── CATEGORY 5: Correlations ─────────────────────────────────────────────
    # Compute once and reuse in statistical_tests (avoids duplicate computation).
    feature_target_correlation: dict = {}
    protected_feature_correlations: dict = {}

    if target_column:
        for col in df.columns:
            if col == target_column:
                continue
            assoc = compute_association(df[col], df[target_column])
            if assoc:
                feature_target_correlation[col] = assoc

    for protected in protected_columns:
        protected_feature_correlations[protected] = {}
        for col in df.columns:
            if col == protected:
                continue
            assoc = compute_association(df[protected], df[col])
            if assoc:
                protected_feature_correlations[protected][col] = assoc

    # ── CATEGORY 6: Statistical tests ────────────────────────────────────────
    # Reuse already-computed associations from feature_target_correlation.
    statistical_tests: dict = {}

    for col, assoc in feature_target_correlation.items():
        method = assoc["method"]
        if method.startswith("cramers_v"):
            statistical_tests[f"{col}_vs_target"] = {
                "test": "chi_square",
                "statistic": float(assoc["value"]),
                "p_value": float(assoc["p_value"]),
                "significant": bool(assoc["p_value"] < 0.05),
                "effect_size": float(assoc["value"]),
            }
        else:
            statistical_tests[f"{col}_vs_target"] = {
                "test": "point_biserial",
                "statistic": float(assoc["value"]),
                "p_value": float(assoc["p_value"]),
                "significant": bool(assoc["p_value"] < 0.05),
            }

    # ── CATEGORY 7: Feature stats ─────────────────────────────────────────────
    feature_stats: dict = {}

    for col in df.columns:
        series = df[col]
        missing_count = int(series.isnull().sum())

        if pd.api.types.is_numeric_dtype(series):
            clean = series.dropna()
            if clean.empty:
                continue
            q1, q3 = float(clean.quantile(0.25)), float(clean.quantile(0.75))
            iqr = q3 - q1
            outliers = clean[(clean < q1 - 1.5 * iqr) | (clean > q3 + 1.5 * iqr)]
            feature_stats[col] = {
                "dtype": "numerical",
                "min": float(clean.min()),
                "max": float(clean.max()),
                "mean": float(clean.mean()),
                "median": float(clean.median()),
                "std": float(clean.std()),
                "percentiles": {"25": q1, "50": float(clean.quantile(0.5)), "75": q3},
                "skewness": _f(clean.skew()),
                "kurtosis": _f(clean.kurtosis()),
                "outlier_count": int(len(outliers)),
                "missing_count": missing_count,
            }
        else:
            # dropna=True so NaN is never sent as a category key to the LLM
            counts = series.value_counts(dropna=True)
            total = counts.sum()
            feature_stats[col] = {
                "dtype": "categorical",
                "n_unique": int(series.nunique(dropna=True)),
                "value_counts": {str(k): int(v) for k, v in counts.items()},
                "value_percentages": {str(k): float(v / total * 100) for k, v in counts.items()},
                "missing_count": missing_count,
            }

    # ── CATEGORY 8: Intersectional groups ────────────────────────────────────
    # All pairs of protected columns, not just the first two.
    intersectional_groups: list = []

    if target_column and target_type == "binary" and len(protected_columns) >= 2:
        target_indicator = to_binary_indicator(df[target_column], positive_class_label)

        for col1, col2 in combinations(protected_columns, 2):
            g1 = _group_series_for_protected(df, col1)
            g2 = _group_series_for_protected(df, col2)

            working = pd.DataFrame({
                col1: g1,
                col2: g2,
                "__t__": target_indicator,
            }).dropna(subset=[col1, col2, "__t__"])

            grouped = working.groupby([col1, col2])["__t__"].agg(["count", "sum", "mean"])

            group_data: dict = {}
            rates: list[float] = []
            sizes: list[int] = []

            # reset_index() turns the MultiIndex into regular columns, avoiding
            # subscript access on a Hashable index (pyright limitation with iterrows).
            for _, row in grouped.reset_index().iterrows():
                count = int(row["count"])
                positive = int(row["sum"])
                rate = float(row["mean"]) if count > 0 else 0.0
                group_key = f"{row[col1]}|{row[col2]}"
                group_data[group_key] = {
                    "count": count,
                    "positive_count": positive,
                    "positive_rate": rate,
                }
                rates.append(rate)
                sizes.append(count)

            if group_data:
                intersectional_groups.append({
                    "attributes": [col1, col2],
                    "groups": group_data,
                    "min_group_size": int(min(sizes)),
                    "max_rate_disparity": float(max(rates) - min(rates)),
                })

    # ── CATEGORY 9: Missingness by group ─────────────────────────────────────
    missingness_by_group: dict = {}

    for col in df.columns:
        if df[col].isnull().sum() == 0:
            continue
        missingness_by_group[col] = {}
        for protected in protected_columns:
            group_series = _group_series_for_protected(df, protected)
            missingness_by_group[col][protected] = {
                str(grp): {"missing_rate": float(sub.isnull().mean())}
                for grp, sub in df.groupby(group_series)[col]
            }

    # ── CATEGORY 10: Schema inference ────────────────────────────────────────
    schema_inference = {
        "detected_domain": dataset_domain,
        "likely_model_task": (
            "binary_classification" if target_type == "binary"
            else "multiclass_classification" if target_type == "multiclass"
            else "regression" if target_type == "continuous"
            else "unknown"
        ),
        "has_model_predictions": has_model_predictions,
    }

    # ── Final result ──────────────────────────────────────────────────────────
    result = {
        "dataset_fundamentals": {
            "total_rows": total_rows,
            "total_columns": len(column_names),
            "column_names": column_names,
            "column_dtypes": column_dtypes,
            "missing_values": missing_values,
            "duplicate_rows": {
                "count": duplicate_count,
                "percentage": float(duplicate_count / total_rows * 100),
            },
        },
        "target_analysis": {
            "target_column": target_column,
            "target_type": target_type,
            "class_distribution": class_distribution,
            "positive_class_label": str(positive_class_label) if positive_class_label is not None else None,
            "class_imbalance_ratio": imbalance_ratio,
            "base_rate": base_rate,
        },
        "group_outcome_stats": group_outcome_stats,
        "preliminary_bias_signals": preliminary_bias_signals,
        "feature_stats": feature_stats,
        "intersectional_groups": intersectional_groups,
        "schema_inference": schema_inference,
        "numerical_summary": numerical_summary,
        "feature_target_correlation": feature_target_correlation,
        "protected_feature_correlations": protected_feature_correlations,
        "statistical_tests": statistical_tests,
        "missingness_by_group": missingness_by_group,
    }

    return clean_nan(result)

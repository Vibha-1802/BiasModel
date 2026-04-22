import pandas as pd
from io import StringIO
from fastapi import HTTPException

MAX_FILE_SIZE_MB = 10  

import math
import numpy as np

def clean_nan(obj):
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan(v) for v in obj]
    elif isinstance(obj, (float, np.float32, np.float64)):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    else:
        return obj
    
async def process_dataset(file):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    contents = await file.read()

    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max allowed is {MAX_FILE_SIZE_MB} MB"
        )

    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        df = pd.read_csv(StringIO(contents.decode("utf-8")))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV format")

    if df.empty:
        raise HTTPException(status_code=400, detail="CSV has no data")

    null_counts = df.isnull().sum().to_dict()

    return {
        "filename": file.filename,
        "rows": len(df),
        "columns": list(df.columns),
        "missing_values": null_counts
    }

import pandas as pd
import numpy as np
from io import StringIO
from fastapi import HTTPException
from scipy.stats import chi2_contingency, pointbiserialr

TARGET_KEYWORDS = ["label", "target", "outcome", "approved", "hired"]
PROTECTED_CANDIDATES = ["gender", "sex", "race", "ethnicity"]


def detect_target_column(columns):
    for col in columns:
        for keyword in TARGET_KEYWORDS:
            if keyword in col.lower():
                return col
    return None


def cramers_v(confusion_matrix):
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    r, k = confusion_matrix.shape
    return np.sqrt(chi2 / (n * (min(k - 1, r - 1))))


async def analyze_dataset(file):

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV allowed")

    contents = await file.read()
    df = pd.read_csv(StringIO(contents.decode("utf-8")))

    total_rows = len(df)
    column_names = list(df.columns)
    protected_cols = [
    col for col in df.columns
    if any(pc in col.lower() for pc in PROTECTED_CANDIDATES)
]

    # ---------------- CATEGORY 1 ----------------
    column_dtypes = {
        col: "numerical" if pd.api.types.is_numeric_dtype(df[col]) else "categorical"
        for col in df.columns
    }

    missing_values = {
        col: {
            "count": int(df[col].isnull().sum()),
            "percentage": float(df[col].isnull().mean() * 100)
        }
        for col in df.columns
    }

    duplicate_count = df.duplicated().sum()

    # ---------------- CATEGORY 2 ----------------
    target_column = detect_target_column(column_names)
    target_type = None
    class_distribution = {}
    positive_class_label = None
    imbalance_ratio = None
    base_rate = None

    if target_column:
        target_series = df[target_column]
        unique_vals = target_series.dropna().unique()

        if len(unique_vals) == 2:
            target_type = "binary"
        elif len(unique_vals) > 2:
            target_type = "multiclass"
        else:
            target_type = "continuous"

        if target_type in ["binary", "multiclass"]:
            counts = target_series.value_counts()
            total = counts.sum()

            for cls, count in counts.items():
                class_distribution[str(cls)] = {
                    "count": int(count),
                    "percentage": float(count / total * 100)
                }

            majority = counts.max()
            minority = counts.min()

            imbalance_ratio = float(majority / minority) if minority > 0 else None
            positive_class_label = counts.idxmax()
            base_rate = float(majority / total)

    # ---------------- CATEGORY 3 ----------------
    numerical_summary = {}

    for col in df.select_dtypes(include="number").columns:
        series = df[col].dropna()
        if len(series) == 0:
            continue

        numerical_summary[col] = {
            "min": float(series.min()),
            "max": float(series.max()),
            "mean": float(series.mean()),
            "median": float(series.median()),
            "std": float(series.std()),
            "percentiles": {
                "25": float(series.quantile(0.25)),
                "50": float(series.quantile(0.5)),
                "75": float(series.quantile(0.75)),
                "90": float(series.quantile(0.9)),
                "95": float(series.quantile(0.95))
            },
            "suggested_bins": {
                "<25": int((series < 25).sum()),
                "25-40": int(((series >= 25) & (series < 40)).sum()),
                "40-60": int(((series >= 40) & (series < 60)).sum()),
                ">60": int((series >= 60).sum())
            }
        }

    # ---------------- CATEGORY 4 ----------------
    group_outcome_stats = {}
    preliminary_bias_signals = {}

    if target_column and target_type == "binary":
        for col in column_names:
            if any(pc in col.lower() for pc in PROTECTED_CANDIDATES):

                grouped = df.groupby(col)[target_column]
                group_outcome_stats[col] = {}

                rates = []

                for group, values in grouped:
                    count = len(values)
                    positive = (values == positive_class_label).sum()
                    rate = positive / count if count > 0 else 0

                    group_outcome_stats[col][str(group)] = {
                        "count": int(count),
                        "positive_rate": float(rate)
                    }

                    rates.append(rate)

                if rates:
                    max_r, min_r = max(rates), min(rates)

                    preliminary_bias_signals[col] = {
                        "statistical_parity_difference": float(max_r - min_r),
                        "disparate_impact_ratio": float(min_r / max_r) if max_r > 0 else None
                    }

    # ---------------- CATEGORY 5 ----------------
    feature_target_correlation = {}
    protected_feature_correlations = {}

    if target_column:

        for col in df.columns:
            if col == target_column:
                continue

            try:
                if df[col].dtype == "object":
                    contingency = pd.crosstab(df[col], df[target_column])
                    stat, p, _, _ = chi2_contingency(contingency)

                    feature_target_correlation[col] = {
                        "method": "cramers_v",
                        "value": float(cramers_v(contingency)),
                        "p_value": float(p)
                    }
                else:
                    if target_type == "binary":
                        corr, p = pointbiserialr(df[col].fillna(0), df[target_column])
                        feature_target_correlation[col] = {
                            "method": "point_biserial",
                            "value": float(corr),
                            "p_value": float(p)
                        }
            except:
                continue


    # Protected vs feature (proxy detection)
    for protected in protected_cols:
        protected_feature_correlations[protected] = {}

        for col in df.columns:
            if col == protected:
                continue

            try:
                contingency = pd.crosstab(df[protected], df[col])
                stat, p, _, _ = chi2_contingency(contingency)

                protected_feature_correlations[protected][col] = {
                    "method": "cramers_v",
                    "value": float(cramers_v(contingency)),
                    "p_value": float(p)
                }
            except:
                continue

    # ---------------- CATEGORY 6 ----------------
    statistical_tests = {}

    if target_column:

        for col in df.columns:
            if col == target_column:
                continue

            try:
                if df[col].dtype == "object":

                    contingency = pd.crosstab(df[col], df[target_column])
                    stat, p, _, _ = chi2_contingency(contingency)

                    statistical_tests[f"{col}_vs_target"] = {
                        "test": "chi_square",
                        "statistic": float(stat),
                        "p_value": float(p),
                        "significant": bool(p < 0.05),
                        "effect_size": float(cramers_v(contingency))
                    }

                else:
                    if target_type == "binary":
                        corr, p = pointbiserialr(df[col].fillna(0), df[target_column])

                        statistical_tests[f"{col}_vs_target"] = {
                            "test": "point_biserial",
                            "statistic": float(corr),
                            "p_value": float(p),
                            "significant": bool(p < 0.05)
                        }

            except:
                continue


    # ---------------- CATEGORY 7 ----------------
    feature_stats = {}

    for col in df.columns:
        series = df[col]
        missing_count = int(series.isnull().sum())

        if pd.api.types.is_numeric_dtype(series):
            clean = series.dropna()

            q1 = clean.quantile(0.25)
            q3 = clean.quantile(0.75)
            iqr = q3 - q1

            outliers = clean[
                (clean < (q1 - 1.5 * iqr)) |
                (clean > (q3 + 1.5 * iqr))
            ]

            feature_stats[col] = {
                "dtype": "numerical",
                "min": float(clean.min()),
                "max": float(clean.max()),
                "mean": float(clean.mean()),
                "median": float(clean.median()),
                "std": float(clean.std()),
                "percentiles": {
                    "25": float(q1),
                    "50": float(clean.quantile(0.5)),
                    "75": float(q3)
                },
                "skewness": float(clean.skew()),
                "kurtosis": float(clean.kurtosis()),
                "outlier_count": int(len(outliers)),
                "missing_count": missing_count
            }

        else:
            counts = series.value_counts()
            total = counts.sum()

            feature_stats[col] = {
                "dtype": "categorical",
                "n_unique": int(series.nunique()),
                "value_counts": counts.to_dict(),
                "value_percentages": {
                    str(k): float(v / total * 100) for k, v in counts.items()
                },
                "missing_count": missing_count
            }

    # ---------------- CATEGORY 7 ----------------
    feature_stats = {}

    for col in df.columns:
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            clean = series.dropna()
            feature_stats[col] = {
                "dtype": "numerical",
                "mean": float(clean.mean()),
                "std": float(clean.std()),
                "skewness": float(clean.skew())
            }
        else:
            feature_stats[col] = {
                "dtype": "categorical",
                "n_unique": int(series.nunique())
            }

    # ---------------- CATEGORY 8 ----------------
    intersectional_groups = []

    protected_cols = [
        col for col in df.columns
        if any(pc in col.lower() for pc in PROTECTED_CANDIDATES)
    ]

    if target_column and len(protected_cols) >= 2:
        col1, col2 = protected_cols[:2]
        grouped = df.groupby([col1, col2])[target_column]

        group_data = {}

        for keys, values in grouped:
            count = len(values)
            positive = (values == positive_class_label).sum()
            rate = positive / count if count > 0 else 0

            group_data[str(keys)] = {
                "count": int(count),
                "positive_rate": float(rate)
            }

        intersectional_groups.append({
            "attributes": [col1, col2],
            "groups": group_data
        })

    # ---------------- CATEGORY 9 ----------------
    missingness_by_group = {}

    for col in df.columns:
        if df[col].isnull().sum() == 0:
            continue

        missingness_by_group[col] = {}

        for protected in protected_cols:
            grouped = df.groupby(protected)[col]

            missingness_by_group[col][protected] = {}

            for group, values in grouped:
                missingness_by_group[col][protected][str(group)] = {
                    "missing_rate": float(values.isnull().mean())
                }

    # ---------------- CATEGORY 10 ----------------
    schema_inference = {
        "detected_domain": "unknown",
        "likely_model_task": "binary_classification" if target_type == "binary" else "regression"
    }

    # ---------------- FINAL ----------------
    result= {
        "dataset_fundamentals": {
            "total_rows": total_rows,
            "total_columns": len(column_names),
            "column_names": column_names,
            "column_dtypes": column_dtypes,
            "missing_values": missing_values,
            "duplicate_rows": {
                "count": int(duplicate_count),
                "percentage": float(duplicate_count / total_rows * 100)
            }
        },
        "target_analysis": {
            "target_column": target_column,
            "target_type": target_type,
            "class_distribution": class_distribution,
            "positive_class_label": str(positive_class_label) if positive_class_label else None,
            "class_imbalance_ratio": imbalance_ratio,
            "base_rate": base_rate
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
        "feature_stats": feature_stats,
        "missingness_by_group": missingness_by_group
    }

    return clean_nan(result)
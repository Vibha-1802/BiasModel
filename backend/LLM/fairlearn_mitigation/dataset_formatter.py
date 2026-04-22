from __future__ import annotations

from itertools import combinations
from typing import Any


TARGET_KEYWORDS = ["label", "target", "outcome", "approved", "hired", "decision", "shortlisted", "selected", "admitted", "granted", "accepted", "rejected", "churned", "defaulted", "readmitted"]
PROTECTED_KEYWORDS = [
    "gender",
    "sex",
    "race",
    "ethnicity",
    "age",
    "nationality",
    "religion",
    "disability",
    "marital",
    "income",
    "zip",
    "zipcode",
]
FAVORABLE_LABEL_HINTS = {
    "1",
    "true",
    "yes",
    "approved",
    "approve",
    "accepted",
    "selected",
    "shortlisted",
    "hired",
    "admitted",
    "granted",
    "pass",
    "positive",
    "favorable",
    "good",
}
DOMAIN_KEYWORDS = {
    "credit_scoring": ["loan", "credit", "approved", "approval", "interest", "default"],
    "hiring": ["hire", "hired", "candidate", "resume", "job", "interview", "employment", "shortlist", "shortlisted", "screening", "applicant", "recruited", "attrition"],
    "healthcare": ["patient", "diagnosis", "hospital", "treatment", "medical", "health"],
    "criminal_justice": ["recidivism", "arrest", "crime", "offense", "sentence", "parole"],
    "housing": ["mortgage", "housing", "rent", "tenant", "property", "home"],
}
PREDICTION_KEYWORDS = ["prediction", "predicted", "y_pred", "model_output"]
PROBABILITY_KEYWORDS = ["prob", "probability", "score", "confidence"]


def _to_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_fraction(value: Any) -> float | None:
    number = _to_float(value)
    if number is None:
        return None
    if number > 1:
        return number / 100.0
    if number < 0:
        return None
    return number


def _safe_div(numerator: float, denominator: float) -> float | None:
    if denominator in (0, None):
        return None
    return float(numerator / denominator)


def _pick_target_column(payload: dict[str, Any]) -> str | None:
    target = payload.get("target_analysis", {}).get("target_column")
    if target:
        return str(target)

    for col in payload.get("dataset_fundamentals", {}).get("column_names", []):
        lowered = str(col).lower()
        if any(keyword in lowered for keyword in TARGET_KEYWORDS):
            return str(col)
    return None


def _pick_positive_label(class_distribution: dict[str, Any], fallback: Any) -> Any:
    if fallback is not None:
        fallback_text = str(fallback).strip().lower()
        if fallback_text:
            return fallback

    for label in class_distribution:
        if str(label).strip().lower() in FAVORABLE_LABEL_HINTS:
            return label

    if "1" in class_distribution:
        return "1"
    if 1 in class_distribution:
        return 1

    counts: list[tuple[Any, int]] = []
    for label, stats in class_distribution.items():
        if isinstance(stats, dict):
            counts.append((label, int(stats.get("count", 0) or 0)))
    if not counts:
        return None

    # Fall back to the minority class for binary labels when no favorable hint exists.
    return min(counts, key=lambda item: item[1])[0]


def _protected_columns(payload: dict[str, Any]) -> list[str]:
    columns = payload.get("dataset_fundamentals", {}).get("column_names", [])
    group_cols = list(payload.get("group_outcome_stats", {}).keys())

    detected = []
    seen = set()
    for col in [*group_cols, *columns]:
        lowered = str(col).lower()
        if any(keyword in lowered for keyword in PROTECTED_KEYWORDS) and col not in seen:
            detected.append(str(col))
            seen.add(col)
    return detected


def _build_dataset_fundamentals(payload: dict[str, Any]) -> dict[str, Any]:
    source = payload.get("dataset_fundamentals", {})
    return {
        "total_rows": int(source.get("total_rows", 0) or 0),
        "total_columns": int(source.get("total_columns", 0) or 0),
        "column_names": source.get("column_names", []),
        "column_dtypes": source.get("column_dtypes", {}),
        "missing_values": {
            col: {
                "count": int((stats or {}).get("count", 0) or 0),
                "percentage": _normalize_fraction((stats or {}).get("percentage", 0)) or 0.0,
            }
            for col, stats in (source.get("missing_values", {}) or {}).items()
        },
        "duplicate_rows": {
            "count": int((source.get("duplicate_rows", {}) or {}).get("count", 0) or 0),
            "percentage": _normalize_fraction(
                (source.get("duplicate_rows", {}) or {}).get("percentage", 0)
            )
            or 0.0,
        },
        "dataset_size_mb": _to_float(source.get("dataset_size_mb")),
    }


def _build_target_analysis(payload: dict[str, Any], total_rows: int) -> dict[str, Any]:
    source = payload.get("target_analysis", {})
    class_distribution = source.get("class_distribution", {}) or {}
    normalized_distribution: dict[str, dict[str, Any]] = {}

    for label, stats in class_distribution.items():
        count = int((stats or {}).get("count", 0) or 0)
        percentage = _normalize_fraction((stats or {}).get("percentage"))
        if percentage is None and total_rows:
            percentage = count / total_rows
        normalized_distribution[str(label)] = {
            "count": count,
            "percentage": percentage or 0.0,
        }

    positive_class_label = _pick_positive_label(
        normalized_distribution,
        source.get("positive_class_label"),
    )

    majority = max((entry["count"] for entry in normalized_distribution.values()), default=0)
    minority = min((entry["count"] for entry in normalized_distribution.values()), default=0)
    imbalance_ratio = _to_float(source.get("class_imbalance_ratio"))
    if imbalance_ratio is None and minority:
        imbalance_ratio = majority / minority

    base_rate = _to_float(source.get("base_rate"))
    if positive_class_label is not None and str(positive_class_label) in normalized_distribution:
        positive_count = normalized_distribution[str(positive_class_label)]["count"]
        base_rate = _safe_div(positive_count, sum(item["count"] for item in normalized_distribution.values()))

    return {
        "target_column": source.get("target_column") or _pick_target_column(payload),
        "target_type": source.get("target_type"),
        "class_distribution": normalized_distribution,
        "positive_class_label": positive_class_label,
        "class_imbalance_ratio": imbalance_ratio,
        "base_rate": base_rate,
    }


def _build_protected_attribute_candidates(payload: dict[str, Any]) -> list[dict[str, Any]]:
    fundamentals = payload.get("dataset_fundamentals", {})
    feature_stats = payload.get("feature_stats", {}) or {}
    numerical_summary = payload.get("numerical_summary", {}) or {}
    columns = fundamentals.get("column_names", []) or []
    dtypes = fundamentals.get("column_dtypes", {}) or {}

    candidates = []
    for col in columns:
        lowered = str(col).lower()
        stats = feature_stats.get(col, {}) or {}
        dtype = dtypes.get(col, stats.get("dtype"))

        is_name_match = any(keyword in lowered for keyword in PROTECTED_KEYWORDS)
        if not is_name_match:
            continue

        # Low cardinality is recorded as supplemental signal, not a standalone qualifier.
        is_low_cardinality = stats.get("dtype") == "categorical" and int(stats.get("n_unique", 999)) <= 10
        reason = "name_match_low_cardinality" if is_low_cardinality else "name_match"
        candidate: dict[str, Any] = {
            "column": col,
            "detection_reason": reason,
            "dtype": dtype or stats.get("dtype") or "categorical",
        }

        if candidate["dtype"] == "numerical":
            numeric_stats = numerical_summary.get(col, stats)
            candidate.update(
                {
                    "min": _to_float(numeric_stats.get("min")),
                    "max": _to_float(numeric_stats.get("max")),
                    "mean": _to_float(numeric_stats.get("mean")),
                    "median": _to_float(numeric_stats.get("median")),
                    "std": _to_float(numeric_stats.get("std")),
                    "percentiles": numeric_stats.get("percentiles", {}),
                    "suggested_bins": numeric_stats.get("suggested_bins", {}),
                }
            )
        else:
            value_counts = stats.get("value_counts", {}) or {}
            value_percentages = {
                str(key): _normalize_fraction(value) or 0.0
                for key, value in (stats.get("value_percentages", {}) or {}).items()
            }
            candidate.update(
                {
                    "unique_values": list(value_counts.keys()),
                    "value_counts": value_counts,
                    "value_percentages": value_percentages,
                    "n_unique": int(stats.get("n_unique", len(value_counts)) or 0),
                }
            )

        candidates.append(candidate)
    return candidates


def _build_group_outcome_stats(payload: dict[str, Any]) -> dict[str, Any]:
    source = payload.get("group_outcome_stats", {}) or {}
    output: dict[str, Any] = {}

    for attribute, groups in source.items():
        output[attribute] = {}
        for group_name, stats in (groups or {}).items():
            count = int((stats or {}).get("count", 0) or 0)
            positive_count = (stats or {}).get("positive_count")
            if positive_count is None:
                rate = _normalize_fraction((stats or {}).get("positive_rate")) or 0.0
                positive_count = round(rate * count)
            positive_rate = _normalize_fraction((stats or {}).get("positive_rate"))
            if positive_rate is None:
                positive_rate = _safe_div(int(positive_count), count) or 0.0

            output[attribute][str(group_name)] = {
                "count": count,
                "positive_count": int(positive_count),
                "positive_rate": positive_rate,
            }
    return output


def _build_preliminary_bias_signals(group_outcome_stats: dict[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {}

    for attribute, groups in group_outcome_stats.items():
        rates = {
            group_name: _normalize_fraction(stats.get("positive_rate")) or 0.0
            for group_name, stats in groups.items()
        }
        if not rates:
            continue

        most_favored_group = max(rates, key=rates.get)
        least_favored_group = min(rates, key=rates.get)
        max_rate = rates[most_favored_group]
        min_rate = rates[least_favored_group]

        output[attribute] = {
            # Signed: negative means the least-favored group is disadvantaged (standard Fairlearn convention).
            "statistical_parity_difference": rates[least_favored_group] - rates[most_favored_group],
            "disparate_impact_ratio": _safe_div(min_rate, max_rate),
            "most_favored_group": most_favored_group,
            "least_favored_group": least_favored_group,
            "rate_spread": max_rate - min_rate,  # unsigned magnitude for readability
        }
    return output


def _build_cross_correlation(payload: dict[str, Any], protected_cols: list[str]) -> dict[str, Any]:
    source = payload.get("protected_feature_correlations", {}) or {}
    output: dict[str, Any] = {}

    for left, right in combinations(protected_cols, 2):
        pair_key = f"{left}__{right}"
        direct = (source.get(left, {}) or {}).get(right)
        reverse = (source.get(right, {}) or {}).get(left)
        stats = direct or reverse
        if not stats:
            continue
        output[pair_key] = {
            "method": stats.get("method", "cramers_v"),
            "value": _to_float(stats.get("value")),
            "p_value": _to_float(stats.get("p_value")),
        }
    return output


def _build_feature_stats(payload: dict[str, Any], fundamentals: dict[str, Any], target_column: str | None) -> dict[str, Any]:
    source = payload.get("feature_stats", {}) or {}
    missing = fundamentals.get("missing_values", {}) or {}
    output: dict[str, Any] = {}

    for col, stats in source.items():
        if col == target_column:
            continue

        dtype = stats.get("dtype")
        if dtype == "numerical":
            output[col] = {
                "dtype": "numerical",
                "min": _to_float(stats.get("min")),
                "max": _to_float(stats.get("max")),
                "mean": _to_float(stats.get("mean")),
                "median": _to_float(stats.get("median")),
                "std": _to_float(stats.get("std")),
                "percentiles": stats.get("percentiles", {}),
                "skewness": _to_float(stats.get("skewness")),
                "kurtosis": _to_float(stats.get("kurtosis")),
                "outlier_count": int(stats.get("outlier_count", 0) or 0),
                "missing_count": int((missing.get(col, {}) or {}).get("count", stats.get("missing_count", 0)) or 0),
            }
        else:
            value_counts = stats.get("value_counts", {}) or {}
            output[col] = {
                "dtype": "categorical",
                "n_unique": int(stats.get("n_unique", len(value_counts)) or 0),
                "value_counts": value_counts,
                "value_percentages": {
                    str(key): _normalize_fraction(value) or 0.0
                    for key, value in (stats.get("value_percentages", {}) or {}).items()
                },
                "missing_count": int((missing.get(col, {}) or {}).get("count", stats.get("missing_count", 0)) or 0),
            }
    return output


def _build_intersectional_groups(
    payload: dict[str, Any],
    total_rows: int,
) -> list[dict[str, Any]]:
    source = payload.get("intersectional_groups", []) or []
    output = []

    for entry in source:
        groups = entry.get("groups", {}) or {}
        rates = []
        sizes = []
        normalized_groups: dict[str, Any] = {}

        for group_name, stats in groups.items():
            count = int((stats or {}).get("count", 0) or 0)
            rate = _normalize_fraction((stats or {}).get("positive_rate")) or 0.0
            normalized_groups[str(group_name)] = {
                "count": count,
                "positive_rate": rate,
                "representation": _safe_div(count, total_rows) or 0.0,
            }
            rates.append(rate)
            sizes.append(count)

        output.append(
            {
                "attributes": entry.get("attributes", []),
                "groups": normalized_groups,
                "min_group_size": min(sizes) if sizes else 0,
                "max_rate_disparity": (max(rates) - min(rates)) if rates else 0.0,
            }
        )
    return output


def _infer_domain(columns: list[str]) -> tuple[str, list[str]]:
    lowered_columns = [str(col).lower() for col in columns]
    for domain, keywords in DOMAIN_KEYWORDS.items():
        matched = [keyword for keyword in keywords if any(keyword in col for col in lowered_columns)]
        if matched:
            signals = [f"column names containing: {', '.join(sorted(set(matched)))}"]
            return domain, signals
    return "unknown", []


def _build_schema_inference(payload: dict[str, Any], target_analysis: dict[str, Any]) -> dict[str, Any]:
    fundamentals = payload.get("dataset_fundamentals", {}) or {}
    columns = fundamentals.get("column_names", []) or []
    domain, signals = _infer_domain(columns)

    prediction_column = next(
        (col for col in columns if any(keyword in str(col).lower() for keyword in PREDICTION_KEYWORDS)),
        None,
    )
    probability_column = next(
        (col for col in columns if any(keyword in str(col).lower() for keyword in PROBABILITY_KEYWORDS)),
        None,
    )

    target_type = target_analysis.get("target_type")
    likely_model_task = "unknown"
    if target_type == "continuous":
        likely_model_task = "regression"
    elif target_type == "binary":
        likely_model_task = "binary_classification"
    elif target_type == "multiclass":
        likely_model_task = "multiclass_classification"

    return {
        "detected_domain": domain,
        "detection_signals": signals,
        "likely_model_task": likely_model_task,
        "has_model_predictions": prediction_column is not None,
        "prediction_column": prediction_column,
        "has_probability_scores": probability_column is not None,
        "probability_column": probability_column,
    }


def format_bias_analysis_payload(analysis_data: dict[str, Any]) -> dict[str, Any]:
    fundamentals = _build_dataset_fundamentals(analysis_data)
    total_rows = fundamentals["total_rows"]
    target_analysis = _build_target_analysis(analysis_data, total_rows)
    protected_candidates = _build_protected_attribute_candidates(analysis_data)
    group_outcome_stats = _build_group_outcome_stats(analysis_data)
    preliminary_bias_signals = _build_preliminary_bias_signals(group_outcome_stats)
    protected_cols = [candidate["column"] for candidate in protected_candidates]

    return {
        "dataset_fundamentals": fundamentals,
        "target_analysis": target_analysis,
        "protected_attribute_candidates": protected_candidates,
        "group_outcome_stats": group_outcome_stats,
        "preliminary_bias_signals": preliminary_bias_signals,
        "feature_target_correlation": analysis_data.get("feature_target_correlation", {}) or {},
        "protected_feature_correlations": analysis_data.get("protected_feature_correlations", {}) or {},
        "protected_attribute_cross_correlation": _build_cross_correlation(analysis_data, protected_cols),
        "statistical_tests": analysis_data.get("statistical_tests", {}) or {},
        "feature_stats": _build_feature_stats(
            analysis_data,
            fundamentals,
            target_analysis.get("target_column"),
        ),
        "intersectional_groups": _build_intersectional_groups(analysis_data, total_rows),
        "missingness_by_group": analysis_data.get("missingness_by_group", {}) or {},
        "schema_inference": _build_schema_inference(analysis_data, target_analysis),
    }

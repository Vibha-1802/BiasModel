from typing import Any

import httpx
import pandas as pd
from io import StringIO
from fastapi import HTTPException
from app.services.bias_services import process_dataset, analyze_dataset

# Import FairLearn engine (optional - will be imported lazily if needed)
try:
    from app.services.fairlearn_mitigation import BiasMitigationEngine
    FAIRLEARN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  FairLearn not available: {e}")
    FAIRLEARN_AVAILABLE = False
    BiasMitigationEngine = None

# Import AIF360 engine
try:
    from app.services.aif_mitigation import AIFMitigationEngine
    AIF360_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  AIF360 not available: {e}")
    AIF360_AVAILABLE = False
    AIFMitigationEngine = None

def _compare_mitigation_results(fairlearn_res, aif_res):
    f_metrics = fairlearn_res.get("phase_4_report", {}).get("summary", {})
    a_metrics = aif_res.get("phase_4_report", {}).get("summary", {})
    
    f_improved = f_metrics.get("total_metrics_improved", 0)
    a_improved = a_metrics.get("total_metrics_improved", 0)
    f_passed = f_metrics.get("total_metrics_passed", 0)
    a_passed = a_metrics.get("total_metrics_passed", 0)
    
    if a_passed > f_passed:
        return "aif_mitigation"
    elif a_passed == f_passed and a_improved > f_improved:
        return "aif_mitigation"
    return "fairlearn_mitigation"


LLM_SERVICE_URL = "http://localhost:8001/analyze"

DETECTION_METRIC_CATALOG = {
    "statistical_parity_difference": {
        "description": "Difference in success rates between groups.",
        "supported_now": True,
    },
    "disparate_impact_ratio": {
        "description": "Ratio of success rates between groups (80% rule).",
        "supported_now": True,
    },
    "equal_opportunity_difference": {
        "description": "Difference in true positive rates across groups.",
        "supported_now": False,
    },
    "average_odds_difference": {
        "description": "Average difference in false positive and true positive rates.",
        "supported_now": False,
    },
    "predictive_parity_difference": {
        "description": "Difference in precision (PPV) across groups.",
        "supported_now": False,
    },
    "theil_index": {
        "description": "Measures individual and group-level inequality.",
        "supported_now": False,
    },
    "generalized_entropy_index": {
        "description": "Flexible measure of redundancy and inequality.",
        "supported_now": False,
    },
    "kl_divergence": {
        "description": "Divergence between group and population distributions.",
        "supported_now": False,
    },
    "jensen_shannon_divergence": {
        "description": "Symmetric KL variant for representation analysis.",
        "supported_now": False,
    },
}

MITIGATION_CATALOG = {
    "pre_processing": {
        "reweighing": {
            "description": "Assigns weights to samples to neutralize bias.",
            "supported_now": True,
        },
        "disparate_impact_remover": {
            "description": "Edits feature values to increase group similarity.",
            "supported_now": False,
        },
        "learning_fair_representations": {
            "description": "Learns latent representation that hides sensitive information.",
            "supported_now": False,
        },
        "optimized_preprocessing": {
            "description": "Data transformation under fairness constraints.",
            "supported_now": False,
        },
        "fair_data_adaptation": {
            "description": "Adjusts distributions while preserving utility.",
            "supported_now": False,
        },
    },
    "in_processing": {
        "adversarial_debiasing": {"description": "Prevents model from learning protected traits.", "supported_now": False},
        "prejudice_remover": {"description": "Adds fairness penalty to objective.", "supported_now": False},
        "meta_fair_classifier": {"description": "Optimizes for target fairness metric.", "supported_now": False},
        "exponentiated_gradient_reduction": {"description": "Error minimization under fairness constraints.", "supported_now": False},
        "grid_search_reduction": {"description": "Grid search under fairness constraints.", "supported_now": False},
        "gerry_fair_classifier": {"description": "Targets intersectional fairness.", "supported_now": False},
    },
    "post_processing": {
        "equalized_odds_postprocessing": {"description": "Adjusts thresholds to equalize error rates.", "supported_now": False},
        "calibrated_equalized_odds": {"description": "Equalizes odds with calibration.", "supported_now": False},
        "reject_option_classification": {"description": "Reclassifies boundary samples to improve fairness.", "supported_now": False},
        "threshold_optimizer": {"description": "Optimizes group-specific thresholds for target metric.", "supported_now": False},
    },
}


def _to_json_safe(value):
    """Convert nested objects to JSON-serializable Python primitives."""
    if isinstance(value, dict):
        return {str(k): _to_json_safe(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_to_json_safe(v) for v in value]

    if isinstance(value, pd.Series):
        return [_to_json_safe(v) for v in value.tolist()]

    if isinstance(value, pd.Index):
        return [_to_json_safe(v) for v in value.tolist()]

    if isinstance(value, pd.DataFrame):
        return _to_json_safe(value.to_dict(orient="records"))

    # NumPy arrays and similar list-like objects
    if hasattr(value, "tolist") and not isinstance(value, (str, bytes, bytearray)):
        try:
            return _to_json_safe(value.tolist())
        except Exception:
            pass

    # NumPy scalars (e.g., np.bool_, np.int64, np.float64)
    if hasattr(value, "item") and not isinstance(value, (str, bytes, bytearray)):
        try:
            return _to_json_safe(value.item())
        except Exception:
            pass

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    # Non-serializable objects (e.g., model instances)
    return f"<{type(value).__name__}>"


def _compact_phase2_results(phase2: dict) -> dict:
    """Drop heavy internals from mitigation output and keep useful summary fields."""
    result = {
        "phase": phase2.get("phase"),
        "mitigation_method": phase2.get("mitigation_method"),
        "attributes_mitigated": phase2.get("attributes_mitigated", []),
        "successful_attributes": phase2.get("successful_attributes", []),
        "failed_attributes": phase2.get("failed_attributes", []),
        "mitigation_results": {},
    }

    for attr, details in (phase2.get("mitigation_results") or {}).items():
        if not isinstance(details, dict):
            result["mitigation_results"][attr] = {"success": False, "error": "Invalid mitigation result"}
            continue

        compact = {
            "success": bool(details.get("success", False)),
            "weights_summary": details.get("weights_summary"),
            "accuracy_before": details.get("accuracy_before"),
            "accuracy_after": details.get("accuracy_after"),
            "accuracy_delta": details.get("accuracy_delta"),
            "confusion_matrix_before": details.get("confusion_matrix_before"),
            "confusion_matrix_after": details.get("confusion_matrix_after"),
        }

        if details.get("error"):
            compact["error"] = str(details.get("error"))

        # Keep a tiny prediction summary rather than full arrays.
        y_pred = details.get("y_pred")
        if y_pred is not None:
            try:
                pred_list = y_pred.tolist() if hasattr(y_pred, "tolist") else list(y_pred)
                n = len(pred_list)
                positives = sum(1 for x in pred_list if int(x) == 1)
                compact["prediction_summary"] = {
                    "count": n,
                    "positive_count": positives,
                    "positive_rate": (positives / n) if n else 0.0,
                }
            except Exception:
                compact["prediction_summary"] = {"count": None}

        result["mitigation_results"][attr] = compact

    return result


def _compact_phase4_report(phase4: dict) -> dict:
    """Return a concise phase-4 report without duplicating phase 1/3 trees."""
    compact_improvements = {}

    for attr, details in (phase4.get("improvements") or {}).items():
        if not isinstance(details, dict):
            continue
        compact_improvements[attr] = {
            "metrics_passed": details.get("metrics_passed", 0),
            "metrics_improved": details.get("metrics_improved", 0),
            "metrics": details.get("metrics", {}),
        }

    return {
        "summary": phase4.get("summary", {}),
        "improvements": compact_improvements,
    }


def _select_failing_attributes(baseline: dict) -> list[str]:
    """Select attributes with at least one failing fairness metric."""
    failing = []
    for attr, metrics in (baseline.get("bias_metrics") or {}).items():
        if not isinstance(metrics, dict):
            continue
        has_fail = any(
            isinstance(metric_data, dict) and (not bool(metric_data.get("passed", False)))
            for metric_data in metrics.values()
        )
        if has_fail:
            failing.append(attr)
    return failing


def _build_summary_response(stats: dict) -> dict:
    """Return lightweight response for default mode."""
    opt_algo = stats.get("optimal_mitigation", {}).get("selected_algorithm", "fairlearn_mitigation")
    fair = (stats.get(opt_algo) or stats.get("fairlearn_mitigation") or {}) if isinstance(stats, dict) else {}
    phase1 = fair.get("phase_1_baseline", {}) if isinstance(fair, dict) else {}
    phase2 = fair.get("phase_2_mitigation", {}) if isinstance(fair, dict) else {}
    phase3 = fair.get("phase_3_post_mitigation", {}) if isinstance(fair, dict) else {}
    phase4 = fair.get("phase_4_report", {}) if isinstance(fair, dict) else {}

    return {
        "dataset_summary": {
            "rows": stats.get("dataset_fundamentals", {}).get("total_rows"),
            "columns": stats.get("dataset_fundamentals", {}).get("total_columns"),
            "target_column": stats.get("target_analysis", {}).get("target_column"),
        },
        "dataset_fundamentals": stats.get("dataset_fundamentals", {}),
        "numerical_summary": stats.get("numerical_summary", {}),
        "feature_stats": stats.get("feature_stats", {}),
        "bias_plan": {
            "dataset_domain": stats.get("bias_plan", {}).get("dataset_domain"),
            "protected_attributes": stats.get("bias_plan", {}).get("protected_attributes", []),
            "bias_types_detected": stats.get("bias_plan", {}).get("bias_types_detected", []),
            "reasoning": stats.get("bias_plan", {}).get("reasoning"),
            "recommended_detection_metrics": stats.get("bias_plan", {}).get("recommended_detection_metrics", []),
            "recommended_mitigation": stats.get("bias_plan", {}).get("recommended_mitigation", {}),
        },
        "fairness_taxonomy": _build_fairness_taxonomy(stats.get("bias_plan", {})),
        "optimal_mitigation_metadata": {
             "selected_algorithm": opt_algo
        },
        "optimal_mitigation": {
            "phase_1_status": phase1.get("overall_status"),
            "phase_2_method": phase2.get("mitigation_method"),
            "phase_2_successful_attributes": phase2.get("successful_attributes", []),
            "phase_2_failed_attributes": phase2.get("failed_attributes", []),
            "phase_3_status": phase3.get("overall_status"),
            "phase_4_summary": phase4.get("summary", {}),
            "mitigated_dataset_csv": stats.get("optimal_mitigation", {}).get("mitigated_dataset_csv"),
        },
        "reporting_pack": stats.get("reporting_pack", {}),
    }


def _build_fairness_taxonomy(bias_plan: dict) -> dict:
    """Curate detection/mitigation taxonomy and map current recommendations to support status."""
    rec_metrics = list((bias_plan or {}).get("recommended_detection_metrics", []) or [])
    rec_mitigation = (bias_plan or {}).get("recommended_mitigation", {}) or {}

    metric_recommendations = []
    for metric in rec_metrics:
        meta = DETECTION_METRIC_CATALOG.get(metric, {"description": "Unknown metric", "supported_now": False})
        metric_recommendations.append(
            {
                "name": metric,
                "description": meta["description"],
                "supported_now": meta["supported_now"],
            }
        )

    mitigation_recommendations = {}
    for stage in ["pre_processing", "in_processing", "post_processing"]:
        mitigation_recommendations[stage] = []
        for algo in rec_mitigation.get(stage, []) or []:
            meta = MITIGATION_CATALOG.get(stage, {}).get(algo, {"description": "Unknown algorithm", "supported_now": False})
            mitigation_recommendations[stage].append(
                {
                    "name": algo,
                    "description": meta["description"],
                    "supported_now": meta["supported_now"],
                }
            )

    return {
        "detection_metrics_catalog": DETECTION_METRIC_CATALOG,
        "mitigation_algorithms_catalog": MITIGATION_CATALOG,
        "recommended_detection_metrics": metric_recommendations,
        "recommended_mitigation": mitigation_recommendations,
    }


def _build_visualization_pack(stats: dict, best_algo: str = "fairlearn_mitigation") -> dict:
    """Curated, chart-friendly payload for dashboards and reports."""
    fair = (stats.get(best_algo) or {}) if isinstance(stats, dict) else {}
    phase1 = fair.get("phase_1_baseline", {}) if isinstance(fair, dict) else {}
    phase2 = fair.get("phase_2_mitigation", {}) if isinstance(fair, dict) else {}
    phase3 = fair.get("phase_3_post_mitigation", {}) if isinstance(fair, dict) else {}

    baseline_metrics = phase1.get("bias_metrics", {}) if isinstance(phase1, dict) else {}
    post_metrics = phase3.get("bias_metrics", {}) if isinstance(phase3, dict) else {}
    phase2_results = phase2.get("mitigation_results", {}) if isinstance(phase2, dict) else {}

    metric_keys = [
        "statistical_parity_difference",
        "disparate_impact_ratio",
        "equalized_odds_difference",
    ]

    bias_matrix = []
    for attr, before in baseline_metrics.items():
        after = post_metrics.get(attr, {}) if isinstance(post_metrics, dict) else {}
        row = {"attribute": attr}
        for mk in metric_keys:
            b = (before.get(mk) or {}) if isinstance(before, dict) else {}
            a = (after.get(mk) or {}) if isinstance(after, dict) else {}
            b_val = b.get("value")
            a_val = a.get("value")
            row[f"{mk}_before"] = b_val
            row[f"{mk}_after"] = a_val
            row[f"{mk}_delta"] = (a_val - b_val) if isinstance(a_val, (int, float)) and isinstance(b_val, (int, float)) else None
            row[f"{mk}_passed_before"] = b.get("passed")
            row[f"{mk}_passed_after"] = a.get("passed")
        bias_matrix.append(row)

    performance_matrix = []
    for attr, details in (phase2_results or {}).items():
        if not isinstance(details, dict):
            continue
        performance_matrix.append({
            "attribute": attr,
            "success": details.get("success"),
            "accuracy_before": details.get("accuracy_before"),
            "accuracy_after": details.get("accuracy_after"),
            "accuracy_delta": details.get("accuracy_delta"),
            "confusion_matrix_before": details.get("confusion_matrix_before"),
            "confusion_matrix_after": details.get("confusion_matrix_after"),
            "weights_summary": details.get("weights_summary"),
        })

    return {
        "overview": {
            "dataset_rows": stats.get("dataset_fundamentals", {}).get("total_rows"),
            "dataset_columns": stats.get("dataset_fundamentals", {}).get("total_columns"),
            "target_column": stats.get("target_analysis", {}).get("target_column"),
            "protected_attributes": stats.get("bias_plan", {}).get("protected_attributes", []),
            "mitigated_attributes": phase2.get("successful_attributes", []),
        },
        "bias_matrix": bias_matrix,
        "performance_matrix": performance_matrix,
        "status": {
            "baseline": phase1.get("overall_status"),
            "post_mitigation": phase3.get("overall_status"),
            "effectiveness": (fair.get("phase_4_report", {}) or {}).get("summary", {}).get("mitigation_effectiveness"),
        },
    }

async def upload_dataset_controller(file):
    try:
        return await process_dataset(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def analyze_dataset_controller(file, include_full: bool = False):
    try:
        # 1. Compute statistical analysis
        stats = await analyze_dataset(file)
        
        # 2. Call LLM service for bias reasoning
        bias_plan = None
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    LLM_SERVICE_URL,
                    json={"analysis_data": stats},
                    timeout=60.0
                )
                if response.status_code == 200:
                    bias_plan = response.json()
                    stats["bias_plan"] = bias_plan
                else:
                    stats["bias_plan"] = {
                        "error": f"LLM service returned status code {response.status_code}",
                        "details": response.text
                    }
            except Exception as llm_err:
                stats["bias_plan"] = {
                    "error": "Failed to connect to LLM service",
                    "details": str(llm_err)
                }
        
        # 3. Apply FairLearn and AIF360 mitigation if available and bias_plan is valid
        if bias_plan and isinstance(bias_plan, dict) and not bias_plan.get("error"):
            try:
                # The file stream was already consumed by analyze_dataset; rewind before reading again.
                await file.seek(0)
                contents = await file.read()
                df = pd.read_csv(StringIO(contents.decode("utf-8")))
                
                # Inject target variable if missing from LLM response
                if "target_variable" not in bias_plan:
                    bias_plan["target_variable"] = stats.get("target_analysis", {}).get("target_column")
                
                fairlearn_results = None
                aif_results = None
                
                # Run FairLearn
                if FAIRLEARN_AVAILABLE and BiasMitigationEngine is not None:
                    try:
                        engine = BiasMitigationEngine(df, bias_plan)
                        baseline_eval = engine.evaluate_baseline_bias()
                        failing_attributes = _select_failing_attributes(baseline_eval)
                        mitigation_res = engine.apply_reweighing(target_attributes=failing_attributes)
                        mitigated_eval = engine.evaluate_mitigated_bias(mitigation_res.get("mitigation_results", {}), baseline_eval)
                        mitigation_rep = engine.generate_mitigation_report(baseline_eval, mitigated_eval)
                        
                        fairlearn_results = {
                            "phase_1_baseline": baseline_eval,
                            "phase_2_mitigation": _compact_phase2_results(mitigation_res),
                            "phase_3_post_mitigation": mitigated_eval,
                            "phase_4_report": _compact_phase4_report(mitigation_rep),
                        }
                        stats["fairlearn_mitigation"] = fairlearn_results
                    except Exception as mitigation_err:
                        stats["fairlearn_mitigation"] = {"error": f"FairLearn mitigation failed: {str(mitigation_err)}"}
                
                # Run AIF360
                if AIF360_AVAILABLE and AIFMitigationEngine is not None:
                    try:
                        engine = AIFMitigationEngine(df, bias_plan)
                        baseline_eval = engine.evaluate_baseline_bias()
                        failing_attributes = _select_failing_attributes(baseline_eval)
                        mitigation_res = engine.apply_reweighing(target_attributes=failing_attributes)
                        mitigated_eval = engine.evaluate_mitigated_bias(mitigation_res.get("mitigation_results", {}), baseline_eval)
                        mitigation_rep = engine.generate_mitigation_report(baseline_eval, mitigated_eval)
                        
                        aif_results = {
                            "phase_1_baseline": baseline_eval,
                            "phase_2_mitigation": _compact_phase2_results(mitigation_res),
                            "phase_3_post_mitigation": mitigated_eval,
                            "phase_4_report": _compact_phase4_report(mitigation_rep),
                        }
                        stats["aif_mitigation"] = aif_results
                    except Exception as mitigation_err:
                        stats["aif_mitigation"] = {"error": f"AIF360 mitigation failed: {str(mitigation_err)}"}
                
                # Compare and build reporting pack
                if fairlearn_results and not stats["fairlearn_mitigation"].get("error") and aif_results and not stats["aif_mitigation"].get("error"):
                    best_algo = _compare_mitigation_results(fairlearn_results, aif_results)
                    stats["optimal_mitigation"] = {
                        "selected_algorithm": best_algo,
                        "data": stats[best_algo]
                    }
                    stats["reporting_pack"] = _build_visualization_pack(stats, best_algo=best_algo)
                elif fairlearn_results and not stats["fairlearn_mitigation"].get("error"):
                    stats["optimal_mitigation"] = {"selected_algorithm": "fairlearn_mitigation", "data": stats["fairlearn_mitigation"]}
                    stats["reporting_pack"] = _build_visualization_pack(stats, best_algo="fairlearn_mitigation")
                elif aif_results and not stats["aif_mitigation"].get("error"):
                    stats["optimal_mitigation"] = {"selected_algorithm": "aif_mitigation", "data": stats["aif_mitigation"]}
                    stats["reporting_pack"] = _build_visualization_pack(stats, best_algo="aif_mitigation")
                else:
                    stats["reporting_pack"] = _build_visualization_pack(stats)
                    
                # Generate and append mitigated dataset CSV
                if "optimal_mitigation" in stats and stats["optimal_mitigation"].get("selected_algorithm"):
                    best_algo = stats["optimal_mitigation"]["selected_algorithm"]
                    try:
                        mitigated_df = None
                        if best_algo == "fairlearn_mitigation" and FAIRLEARN_AVAILABLE and BiasMitigationEngine is not None:
                            engine = BiasMitigationEngine(df, bias_plan)
                            baseline_eval = stats["fairlearn_mitigation"]["phase_1_baseline"]
                            failing_attributes = _select_failing_attributes(baseline_eval)
                            mitigated_df = engine.export_mitigated_dataset(target_attributes=failing_attributes)
                        elif best_algo == "aif_mitigation" and AIF360_AVAILABLE and AIFMitigationEngine is not None:
                            engine = AIFMitigationEngine(df, bias_plan)
                            baseline_eval = stats["aif_mitigation"]["phase_1_baseline"]
                            failing_attributes = _select_failing_attributes(baseline_eval)
                            mitigated_df = engine.export_mitigated_dataset(target_attributes=failing_attributes)
                            
                        if mitigated_df is not None:
                            csv_buffer = StringIO()
                            mitigated_df.to_csv(csv_buffer, index=False)
                            stats["optimal_mitigation"]["mitigated_dataset_csv"] = csv_buffer.getvalue()
                    except Exception as export_err:
                        print(f"Failed to export mitigated dataset: {export_err}")
                        stats["optimal_mitigation"]["mitigated_dataset_export_error"] = str(export_err)
                    
            except Exception as e:
                 print(f"Dataset reading failed during mitigation setup: {str(e)}")
                 
        if not FAIRLEARN_AVAILABLE and not AIF360_AVAILABLE:
            stats["mitigation_status"] = {
                "warning": "No mitigation engines available.",
                "info": "Install FairLearn or AIF360."
            }
        
        payload = stats if include_full else _build_summary_response(stats)
        return _to_json_safe(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
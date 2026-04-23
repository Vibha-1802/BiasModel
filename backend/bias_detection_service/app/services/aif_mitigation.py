import pandas as pd
import numpy as np
from aif360.datasets import BinaryLabelDataset
from aif360.algorithms.preprocessing import Reweighing
from fairlearn.metrics import (
    demographic_parity_difference,
    demographic_parity_ratio,
    equalized_odds_difference,
)
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from typing import Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')

class AIFMitigationEngine:
    """
    Implements AIF360-based bias evaluation and mitigation.
    Matches the Phase 1..4 structure of BiasMitigationEngine for compatibility.
    """
    
    def __init__(self, df: pd.DataFrame, bias_plan: Dict[str, Any]):
        self.df = df.copy()
        self.bias_plan = bias_plan
        self.protected_attributes = bias_plan.get("protected_attributes", [])
        self.target_col = bias_plan.get("target_variable")
        self.positive_label = str(bias_plan.get("positive_outcome_label", "1"))
        self.recommended_metrics = bias_plan.get("recommended_detection_metrics", [])
        
        if not self.target_col or self.target_col not in self.df.columns:
            raise ValueError(f"Target column '{self.target_col}' not found in dataset")
        if not self.protected_attributes:
            raise ValueError("No protected attributes specified in bias_plan")

    def _normalize_target(self, series: pd.Series) -> pd.Series:
        s = series.copy()
        if pd.api.types.is_numeric_dtype(s):
            unique_vals = s.dropna().unique()
            if set(unique_vals).issubset({0, 1, 0.0, 1.0}):
                return s.fillna(0).astype(int)
        
        s_str = s.astype(str)
        if self.positive_label in s_str.values:
            return (s_str == self.positive_label).astype(int)
            
        factorized, _ = pd.factorize(s)
        return pd.Series(factorized, index=s.index)

    def _normalize_sensitive_feature(self, series: pd.Series) -> pd.Series:
        s = series.copy()
        if pd.api.types.is_numeric_dtype(s):
            if s.dropna().nunique() > 10:
                try:
                    s = pd.qcut(s, q=5, duplicates="drop")
                except Exception:
                    pass
        s = s.astype("object").where(~s.isna(), "missing")
        return s.astype(str)
        
    def _to_aif_dataset(self, df_subset: pd.DataFrame, target_col: str, protected_attr: str) -> BinaryLabelDataset:
        # AIF360 needs numeric categories for protected attributes.
        df_copy = df_subset.copy()
        
        df_copy[target_col] = self._normalize_target(df_copy[target_col])
        attr_vals = self._normalize_sensitive_feature(df_copy[protected_attr])
        
        # We will binarize the sensitive attribute into 1 (privileged) and 0 (unprivileged).
        # We use the most frequent class as "1" for the sake of this transformation,
        # or we dynamically identify it if we have more context. Here we fallback to freq.
        most_freq = attr_vals.value_counts().idxmax()
        df_copy[protected_attr] = (attr_vals == most_freq).astype(int)
        
        # BinaryLabelDataset configuration
        return BinaryLabelDataset(
            df=df_copy,
            label_names=[target_col],
            protected_attribute_names=[protected_attr],
            favorable_label=1,
            unfavorable_label=0
        )

    # ========== PHASE 1: EVALUATE BASELINE BIAS ==========
    def evaluate_baseline_bias(self) -> Dict[str, Any]:
        y = self._normalize_target(self.df[self.target_col])
        evaluation = {}
        
        for attr in self.protected_attributes:
            if attr not in self.df.columns:
                continue
                
            sensitive_features = self._normalize_sensitive_feature(self.df[attr])
            attr_metrics = {}
            
            # Metric 1: Statistical Parity Difference
            spd = demographic_parity_difference(y_true=y, y_pred=y, sensitive_features=sensitive_features)
            attr_metrics["statistical_parity_difference"] = {
                "value": float(spd), "threshold": 0.10, "passed": abs(spd) < 0.10,
                "interpretation": self._interpret_spd(spd)
            }
            
            # Metric 2: Disparate Impact Ratio
            dpr = demographic_parity_ratio(y_true=y, y_pred=y, sensitive_features=sensitive_features)
            attr_metrics["disparate_impact_ratio"] = {
                "value": float(dpr) if dpr is not None else None,
                "threshold": 0.80, "passed": (dpr >= 0.80) if dpr is not None else False,
                "interpretation": self._interpret_dpr(dpr)
            }
            
            # Metric 3: Equalized Odds
            eod = equalized_odds_difference(y_true=y, y_pred=y, sensitive_features=sensitive_features)
            attr_metrics["equalized_odds_difference"] = {
                "value": float(eod), "threshold": 0.10, "passed": abs(eod) < 0.10,
                "interpretation": self._interpret_eod(eod)
            }
            
            evaluation[attr] = attr_metrics
        
        overall_status = self._determine_overall_status(evaluation)
        return {
            "phase": "baseline_evaluation",
            "bias_metrics": evaluation,
            "overall_status": overall_status
        }
        
    # ========== PHASE 2: APPLY MITIGATION ==========
    def apply_reweighing(self, test_size: float = 0.2, random_state: int = 42, target_attributes: list[str] = None) -> Dict[str, Any]:
        X = self.df.drop(columns=[self.target_col])
        y = self._normalize_target(self.df[self.target_col])
        
        stratify_target = y if y.nunique() > 1 else None
        train_idx, test_idx = train_test_split(
            self.df.index, test_size=test_size, random_state=random_state, stratify=stratify_target
        )
        
        train_df = self.df.loc[train_idx]
        test_df = self.df.loc[test_idx]
        
        mitigation_results = {}
        attributes_to_mitigate = target_attributes if target_attributes else self.protected_attributes
        X_train_encoded_base = pd.get_dummies(train_df.drop(columns=[self.target_col] + self.protected_attributes), drop_first=True).fillna(0)
        X_test_encoded_base = pd.get_dummies(test_df.drop(columns=[self.target_col] + self.protected_attributes), drop_first=True).fillna(0)
        X_test_encoded_base = X_test_encoded_base.reindex(columns=X_train_encoded_base.columns, fill_value=0)
        y_train = self._normalize_target(train_df[self.target_col])
        y_test = self._normalize_target(test_df[self.target_col])
        
        for attr in attributes_to_mitigate:
            if attr not in self.df.columns:
                continue
                
            attr_train_norm = self._normalize_sensitive_feature(train_df[attr])
            attr_test_norm = self._normalize_sensitive_feature(test_df[attr])
            most_freq = attr_train_norm.value_counts().idxmax()
            
            aif_train_df = train_df[[attr, self.target_col]].copy()
            aif_train_dataset = self._to_aif_dataset(aif_train_df, self.target_col, attr)
            
            try:
                # AIF360 Reweighing
                privileged_groups = [{attr: 1}]
                unprivileged_groups = [{attr: 0}]
                
                RW = Reweighing(unprivileged_groups=unprivileged_groups, privileged_groups=privileged_groups)
                RW.fit(aif_train_dataset)
                dataset_transf_train = RW.transform(aif_train_dataset)
                sample_weights = dataset_transf_train.instance_weights
                
                weight_stats = {
                    "min": float(np.min(sample_weights)),
                    "max": float(np.max(sample_weights)),
                    "mean": float(np.mean(sample_weights)),
                    "std": float(np.std(sample_weights))
                }
                
                X_train_encoded = X_train_encoded_base.copy()
                X_train_encoded[attr + "_p"] = (attr_train_norm == most_freq).astype(int)
                X_test_encoded = X_test_encoded_base.copy()
                X_test_encoded[attr + "_p"] = (attr_test_norm == most_freq).astype(int)

                # Baseline model
                baseline_model = LogisticRegression(max_iter=1000, random_state=random_state, solver='lbfgs')
                baseline_model.fit(X_train_encoded, y_train)
                baseline_pred = pd.Series(baseline_model.predict(X_test_encoded)).astype(int)

                # Mitigated model
                model = LogisticRegression(max_iter=1000, random_state=random_state, solver='lbfgs')
                model.fit(X_train_encoded, y_train, sample_weight=sample_weights)
                y_pred = pd.Series(model.predict(X_test_encoded)).astype(int)

                baseline_acc = float(accuracy_score(y_test, baseline_pred))
                mitigated_acc = float(accuracy_score(y_test, y_pred))
                
                mitigation_results[attr] = {
                    "model": model, "y_pred": y_pred, "A_test": attr_test_norm, "y_test": y_test,
                    "weights_summary": weight_stats,
                    "accuracy_before": baseline_acc, "accuracy_after": mitigated_acc,
                    "accuracy_delta": mitigated_acc - baseline_acc,
                    "confusion_matrix_before": confusion_matrix(y_test, baseline_pred, labels=[0, 1]).tolist(),
                    "confusion_matrix_after": confusion_matrix(y_test, y_pred, labels=[0, 1]).tolist(),
                    "success": True
                }
            except Exception as e:
                mitigation_results[attr] = {"error": str(e), "success": False}
                
        return {
            "phase": "mitigation_applied", "mitigation_method": "aif360_reweighing",
            "attributes_mitigated": list(mitigation_results.keys()),
            "successful_attributes": [k for k, v in mitigation_results.items() if v.get("success")],
            "failed_attributes": [k for k, v in mitigation_results.items() if not v.get("success")],
            "mitigation_results": mitigation_results
        }

    # ========== PHASE 3: RE-EVALUATE AFTER MITIGATION ==========
    def evaluate_mitigated_bias(self, mitigation_results: Dict[str, Any], baseline_evaluation: Dict[str, Any] = None) -> Dict[str, Any]:
        evaluation_after = {}
        for attr, results in mitigation_results.items():
            if not results.get("success", False):
                continue
            
            y_test = results["y_test"]
            y_pred = results["y_pred"]
            A_test = results["A_test"]
            
            attr_metrics = {}
            spd = demographic_parity_difference(y_true=y_test, y_pred=y_pred, sensitive_features=A_test)
            attr_metrics["statistical_parity_difference"] = {
                "value": float(spd), "threshold": 0.10, "passed": abs(spd) < 0.10, "interpretation": self._interpret_spd(spd)
            }
            dpr = demographic_parity_ratio(y_true=y_test, y_pred=y_pred, sensitive_features=A_test)
            attr_metrics["disparate_impact_ratio"] = {
                "value": float(dpr) if dpr is not None else None, "threshold": 0.80, "passed": (dpr >= 0.80) if dpr is not None else False, "interpretation": self._interpret_dpr(dpr)
            }
            eod = equalized_odds_difference(y_true=y_test, y_pred=y_pred, sensitive_features=A_test)
            attr_metrics["equalized_odds_difference"] = {
                "value": float(eod), "threshold": 0.10, "passed": abs(eod) < 0.10, "interpretation": self._interpret_eod(eod)
            }
            evaluation_after[attr] = attr_metrics
            
        if baseline_evaluation and "bias_metrics" in baseline_evaluation:
            for attr, baseline_metrics in baseline_evaluation["bias_metrics"].items():
                if attr not in evaluation_after:
                    evaluation_after[attr] = baseline_metrics
                    
        return {
            "phase": "post_mitigation_evaluation", "bias_metrics": evaluation_after,
            "overall_status": self._determine_overall_status(evaluation_after)
        }

    # ========== PHASE 4: GENERATE REPORT ==========
    def generate_mitigation_report(self, baseline: Dict, mitigated: Dict) -> Dict[str, Any]:
        report = {"baseline": baseline, "after_mitigation": mitigated, "improvements": {}, "summary": {}}
        baseline_metrics = baseline.get("bias_metrics", {})
        mitigated_metrics = mitigated.get("bias_metrics", {})
        total_metrics_improved = 0
        total_metrics_passed = 0
        
        for attr in baseline_metrics:
            if attr not in mitigated_metrics:
                mitigated_metrics[attr] = baseline_metrics[attr]
            improvement = {}
            attr_improvements = 0
            attr_passed = 0
            
            # SPD
            spd_before = baseline_metrics[attr].get("statistical_parity_difference", {}).get("value")
            spd_after = mitigated_metrics[attr].get("statistical_parity_difference", {}).get("value")
            if spd_before is not None and spd_after is not None:
                improvement["statistical_parity_difference"] = {"before": float(spd_before), "after": float(spd_after), "difference": float(spd_after - spd_before)}
                if spd_before != 0:
                    improvement["statistical_parity_difference"]["percent_improvement"] = float((abs(spd_before) - abs(spd_after)) / abs(spd_before) * 100)
                if mitigated_metrics[attr].get("statistical_parity_difference", {}).get("passed"): attr_passed += 1
                if abs(spd_after) < abs(spd_before): attr_improvements += 1
                    
            # DPR
            dpr_before = baseline_metrics[attr].get("disparate_impact_ratio", {}).get("value")
            dpr_after = mitigated_metrics[attr].get("disparate_impact_ratio", {}).get("value")
            if dpr_before is not None and dpr_after is not None:
                improvement["disparate_impact_ratio"] = {"before": float(dpr_before), "after": float(dpr_after), "difference": float(dpr_after - dpr_before)}
                if mitigated_metrics[attr].get("disparate_impact_ratio", {}).get("passed"): attr_passed += 1
                if abs(dpr_after - 0.80) < abs(dpr_before - 0.80): attr_improvements += 1
                    
            # EOD
            eod_before = baseline_metrics[attr].get("equalized_odds_difference", {}).get("value")
            eod_after = mitigated_metrics[attr].get("equalized_odds_difference", {}).get("value")
            if eod_before is not None and eod_after is not None:
                improvement["equalized_odds_difference"] = {"before": float(eod_before), "after": float(eod_after), "difference": float(eod_after - eod_before)}
                if eod_before != 0:
                    improvement["equalized_odds_difference"]["percent_improvement"] = float((abs(eod_before) - abs(eod_after)) / abs(eod_before) * 100)
                if mitigated_metrics[attr].get("equalized_odds_difference", {}).get("passed"): attr_passed += 1
                if abs(eod_after) < abs(eod_before): attr_improvements += 1
                    
            report["improvements"][attr] = {"metrics": improvement, "metrics_passed": attr_passed, "metrics_improved": attr_improvements}
            total_metrics_improved += attr_improvements
            total_metrics_passed += attr_passed
            
        report["summary"] = {
            "total_protected_attributes": len(baseline_metrics),
            "total_metrics_passed": total_metrics_passed,
            "total_metrics_improved": total_metrics_improved,
            "mitigation_effectiveness": self._assess_effectiveness(baseline, mitigated)
        }
        return report

    def _interpret_spd(self, value): return "✅ PASS" if abs(value) < 0.10 else ("⚠️ WARNING" if abs(value) < 0.15 else "❌ FAIL")
    def _interpret_dpr(self, value): return "⚠️ N/A" if value is None else ("✅ PASS (80% rule)" if value >= 0.80 else ("⚠️ WARNING" if value >= 0.70 else "❌ FAIL"))
    def _interpret_eod(self, value): return "✅ PASS" if abs(value) < 0.10 else "❌ FAIL"
    def _determine_overall_status(self, evaluation: Dict):
        if not evaluation: return "UNKNOWN"
        passed = sum(1 for a in evaluation.values() for m in a.values() if m.get("passed", False))
        total = sum(len(a) for a in evaluation.values())
        return "✅ PASSED: All bias metrics acceptable" if passed == total else ("⚠️ PARTIAL: Some bias metrics improved" if passed >= total * 0.5 else "❌ FAILED: Most bias metrics still high")
    def _assess_effectiveness(self, baseline: Dict, mitigated: Dict):
        b = baseline.get("overall_status", "")
        m = mitigated.get("overall_status", "")
        return "🎯 HIGHLY EFFECTIVE - Bias resolved" if "PASSED" in m and "PASSED" not in b else ("✅ MODERATELY EFFECTIVE - Some improvement" if "PARTIAL" in m or "⚠️" in m else "⚠️ LIMITED EFFECTIVENESS - May need additional mitigation")

    def export_mitigated_dataset(self, target_attributes: list[str] = None) -> pd.DataFrame:
        """
        Computes reweighing weights for the entire dataset using AIF360 and returns 
        a copy of the dataset with the new weight columns appended.
        """
        from aif360.algorithms.preprocessing import Reweighing
        
        export_df = self.df.copy()
        attributes_to_mitigate = target_attributes if target_attributes is not None else self.protected_attributes
        
        for attr in attributes_to_mitigate:
            if attr not in export_df.columns:
                continue
                
            aif_df = export_df[[attr, self.target_col]].copy()
            aif_dataset = self._to_aif_dataset(aif_df, self.target_col, attr)
            
            try:
                privileged_groups = [{attr: 1}]
                unprivileged_groups = [{attr: 0}]
                
                RW = Reweighing(unprivileged_groups=unprivileged_groups, privileged_groups=privileged_groups)
                RW.fit(aif_dataset)
                dataset_transf = RW.transform(aif_dataset)
                export_df[f"sample_weight_{attr}"] = dataset_transf.instance_weights
            except Exception as e:
                print(f"Failed to export AIF360 weights for {attr}: {e}")
                
        return export_df

import pandas as pd
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


class BiasMitigationEngine:
    """
    Implements fairlearn-based bias evaluation and mitigation
    based on LLM recommendations.
    
    Flow:
    1. Evaluate baseline bias (BEFORE mitigation)
    2. Apply reweighing mitigation
    3. Re-evaluate bias (AFTER mitigation)
    4. Generate comparison report
    """
    
    def __init__(self, df: pd.DataFrame, bias_plan: Dict[str, Any]):
        """
        Initialize the mitigation engine.
        
        Args:
            df: Dataset with all features and target
            bias_plan: LLM response with bias plan
                {
                    "protected_attributes": ["age", "gender"],
                    "target_variable": "readmitted_30d",
                    "positive_outcome_label": "1",
                    "recommended_detection_metrics": ["statistical_parity_difference"],
                    "recommended_mitigation": {
                        "pre_processing": ["reweighing"]
                    }
                }
        """
        self.df = df
        self.bias_plan = bias_plan
        self.protected_attributes = bias_plan.get("protected_attributes", [])
        self.target_col = bias_plan.get("target_variable")
        self.positive_label = bias_plan.get("positive_outcome_label", "1")
        self.recommended_metrics = bias_plan.get("recommended_detection_metrics", [])
        self.mitigation_methods = bias_plan.get("recommended_mitigation", {})
        
        # Validate
        if not self.target_col or self.target_col not in self.df.columns:
            raise ValueError(f"Target column '{self.target_col}' not found in dataset")
        
        if not self.protected_attributes:
            raise ValueError("No protected attributes specified in bias_plan")

    def _normalize_target(self, series: pd.Series) -> pd.Series:
        """Robustly normalize target column to 0/1 integers."""
        s = series.copy()
        if pd.api.types.is_numeric_dtype(s):
            unique_vals = s.dropna().unique()
            if set(unique_vals).issubset({0, 1, 0.0, 1.0}):
                return s.fillna(0).astype(int)
        
        s_str = s.astype(str)
        if self.positive_label is not None and str(self.positive_label) in s_str.values:
            return (s_str == str(self.positive_label)).astype(int)
            
        factorized, _ = pd.factorize(s)
        return pd.Series(factorized, index=s.index)

    def _normalize_sensitive_feature(self, series: pd.Series) -> pd.Series:
        """Normalize sensitive feature for fairlearn constraints.

        - Fill missing values
        - Bin high-cardinality numeric attributes to stable groups
        - Cast to string labels
        """
        s = series.copy()
        if pd.api.types.is_numeric_dtype(s):
            non_null_unique = s.dropna().nunique()
            if non_null_unique > 10:
                try:
                    s = pd.qcut(s, q=5, duplicates="drop")
                except Exception:
                    pass
        s = s.astype("object").where(~s.isna(), "missing")
        return s.astype(str)

    def _compute_reweighing_weights(self, y: pd.Series, a: pd.Series) -> pd.Series:
        """Compute Kamiran-Calders style reweighing weights.

        w(a, y) = P(A=a) * P(Y=y) / P(A=a, Y=y)
        """
        a_norm = self._normalize_sensitive_feature(a)
        y_norm = y.astype(int)
        n = len(y_norm)

        p_a = a_norm.value_counts(dropna=False) / n
        p_y = y_norm.value_counts(dropna=False) / n
        p_ay = (
            pd.crosstab(a_norm, y_norm, dropna=False)
            .div(n)
            .stack()
            .to_dict()
        )

        def _weight(row_a, row_y):
            joint = p_ay.get((row_a, row_y), 0.0)
            if joint <= 0:
                return 1.0
            return float((p_a[row_a] * p_y[row_y]) / joint)

        weights = [_weight(row_a, row_y) for row_a, row_y in zip(a_norm.tolist(), y_norm.tolist())]
        return pd.Series(weights, index=y.index)
    
    # ========== PHASE 1: EVALUATE BASELINE BIAS ==========
    
    def evaluate_baseline_bias(self) -> Dict[str, Any]:
        """
        PHASE 1: Evaluate bias BEFORE mitigation.
        
        Calculates fairness metrics for each protected attribute:
        - Statistical Parity Difference
        - Disparate Impact Ratio
        - Equalized Odds Difference
        
        Returns:
            {
                "phase": "baseline_evaluation",
                "bias_metrics": {
                    "age": {
                        "statistical_parity_difference": {...},
                        "disparate_impact_ratio": {...},
                        "equalized_odds_difference": {...}
                    }
                },
                "overall_status": "PASSED" | "FAILED"
            }
        """
        print("=" * 60)
        print("PHASE 1: EVALUATING BASELINE BIAS")
        print("=" * 60)
        
        y = self._normalize_target(self.df[self.target_col])
        evaluation = {}
        
        for attr in self.protected_attributes:
            if attr not in self.df.columns:
                print(f"⚠️  Protected attribute '{attr}' not found, skipping...")
                continue
            
            print(f"\n📊 Analyzing: {attr}")
            sensitive_features = self._normalize_sensitive_feature(self.df[attr])
            attr_metrics = {}
            
            # Metric 1: Statistical Parity Difference
            if "statistical_parity_difference" in self.recommended_metrics or True:
                spd = demographic_parity_difference(
                    y_true=y,
                    y_pred=y,  # Using actual labels as baseline
                    sensitive_features=sensitive_features
                )
                attr_metrics["statistical_parity_difference"] = {
                    "value": float(spd),
                    "threshold": 0.10,
                    "passed": abs(spd) < 0.10,
                    "interpretation": self._interpret_spd(spd)
                }
                print(f"  Statistical Parity Difference: {spd:.4f} {attr_metrics['statistical_parity_difference']['interpretation']}")
            
            # Metric 2: Disparate Impact Ratio
            if "disparate_impact_ratio" in self.recommended_metrics or True:
                dpr = demographic_parity_ratio(
                    y_true=y,
                    y_pred=y,
                    sensitive_features=sensitive_features
                )
                attr_metrics["disparate_impact_ratio"] = {
                    "value": float(dpr) if dpr is not None else None,
                    "threshold": 0.80,
                    "passed": (dpr >= 0.80) if dpr is not None else False,
                    "interpretation": self._interpret_dpr(dpr)
                }
                print(f"  Disparate Impact Ratio: {dpr:.4f} {attr_metrics['disparate_impact_ratio']['interpretation']}")
            
            # Metric 3: Equalized Odds Difference
            eod = equalized_odds_difference(
                y_true=y,
                y_pred=y,
                sensitive_features=sensitive_features
            )
            attr_metrics["equalized_odds_difference"] = {
                "value": float(eod),
                "threshold": 0.10,
                "passed": abs(eod) < 0.10,
                "interpretation": self._interpret_eod(eod)
            }
            print(f"  Equalized Odds Difference: {eod:.4f} {attr_metrics['equalized_odds_difference']['interpretation']}")
            
            evaluation[attr] = attr_metrics
        
        overall_status = self._determine_overall_status(evaluation)
        print(f"\n📌 Overall Status: {overall_status}")
        
        return {
            "phase": "baseline_evaluation",
            "bias_metrics": evaluation,
            "overall_status": overall_status
        }
    
    # ========== PHASE 2: APPLY MITIGATION ==========
    
    def apply_reweighing(
        self,
        test_size: float = 0.2,
        random_state: int = 42,
        target_attributes: list[str] | None = None,
    ) -> Dict[str, Any]:
        """
        PHASE 2: Apply Fairlearn in-processing mitigation.
        
        Steps:
        1. Split data into train/test
          2. For each protected attribute:
              a. Initialize ExponentiatedGradient with DemographicParity
              b. Fit mitigator on training data
              c. Predict on test data
        
        Returns:
            {
                "phase": "mitigation_applied",
                "mitigation_method": "exponentiated_gradient_demographic_parity",
                "attributes_mitigated": ["age", "gender"],
                "mitigation_results": {
                    "age": {
                        "model": LogisticRegression object,
                        "y_pred": array,
                        "A_test": array,
                        "y_test": array,
                        "weights_summary": {...}
                    }
                }
            }
        """
        print("\n" + "=" * 60)
        print("PHASE 2: APPLYING REWEIGHING MITIGATION")
        print("=" * 60)
        
        # Prepare data
        X = self.df.drop(columns=[self.target_col])
        y = self._normalize_target(self.df[self.target_col])
        
        print(f"\n📂 Data split: {test_size*100:.0f}% test, {(1-test_size)*100:.0f}% train")
        
        stratify_target = y if y.nunique() > 1 else None
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
            stratify=stratify_target,
        )
        
        print(f"  Train set: {len(X_train)} samples")
        print(f"  Test set:  {len(X_test)} samples")
        
        mitigation_results = {}
        
        # Apply reweighing mitigation only to requested attributes (or all protected attributes).
        attributes_to_mitigate = list(self.protected_attributes) if target_attributes is None else list(target_attributes)

        # Apply reweighing mitigation for each protected attribute
        for attr in attributes_to_mitigate:
            if attr not in self.df.columns:
                print(f"⚠️  Protected attribute '{attr}' not found, skipping mitigation...")
                continue
            
            print(f"\n🔧 Applying mitigation for: {attr}")
            
            # Get sensitive features for train/test
            A_train = self._normalize_sensitive_feature(X_train[attr])
            A_test = self._normalize_sensitive_feature(X_test[attr])
            
            try:
                print(f"  ✓ Preparing features...")
                X_train_features = X_train.drop(columns=[attr])
                X_test_features = X_test.drop(columns=[attr])

                # Ensure model input is numeric and aligned
                X_train_encoded = pd.get_dummies(X_train_features, drop_first=True)
                X_test_encoded = pd.get_dummies(X_test_features, drop_first=True)
                X_test_encoded = X_test_encoded.reindex(columns=X_train_encoded.columns, fill_value=0)
                X_train_encoded = X_train_encoded.fillna(0)
                X_test_encoded = X_test_encoded.fillna(0)

                # Step 1: Compute reweighing weights
                print(f"  ✓ Computing reweighing weights...")
                sample_weights = self._compute_reweighing_weights(y_train, A_train)
                weight_stats = {
                    "min": float(sample_weights.min()),
                    "max": float(sample_weights.max()),
                    "mean": float(sample_weights.mean()),
                    "std": float(sample_weights.std()),
                }

                # Step 2a: Train baseline classifier (no mitigation)
                print(f"  ✓ Training baseline classifier...")
                baseline_model = LogisticRegression(
                    max_iter=1000,
                    random_state=random_state,
                    solver='lbfgs'
                )
                baseline_model.fit(X_train_encoded, y_train)
                baseline_pred = pd.Series(baseline_model.predict(X_test_encoded)).astype(int)

                # Step 2b: Train weighted classifier
                print(f"  ✓ Training weighted classifier...")
                model = LogisticRegression(
                    max_iter=1000,
                    random_state=random_state,
                    solver='lbfgs'
                )
                model.fit(X_train_encoded, y_train, sample_weight=sample_weights)

                # Step 3: Make predictions
                print(f"  ✓ Making predictions on test set...")
                y_pred = pd.Series(model.predict(X_test_encoded)).astype(int)

                baseline_acc = float(accuracy_score(y_test, baseline_pred))
                mitigated_acc = float(accuracy_score(y_test, y_pred))
                baseline_cm = confusion_matrix(y_test, baseline_pred, labels=[0, 1]).tolist()
                mitigated_cm = confusion_matrix(y_test, y_pred, labels=[0, 1]).tolist()
                
                # Store results
                mitigation_results[attr] = {
                    "model": model,
                    "y_pred": y_pred,
                    "A_test": A_test,
                    "y_test": y_test,
                    "weights_summary": weight_stats,
                    "accuracy_before": baseline_acc,
                    "accuracy_after": mitigated_acc,
                    "accuracy_delta": mitigated_acc - baseline_acc,
                    "confusion_matrix_before": baseline_cm,
                    "confusion_matrix_after": mitigated_cm,
                    "success": True
                }
                
                print(f"  ✅ Mitigation successful for {attr}")
                
            except Exception as e:
                print(f"  ❌ Error during reweighing: {str(e)}")
                mitigation_results[attr] = {
                    "error": str(e),
                    "success": False
                }
        
        return {
            "phase": "mitigation_applied",
            "mitigation_method": "reweighing_weighted_logistic_regression",
            "attributes_mitigated": list(mitigation_results.keys()),
            "successful_attributes": [k for k, v in mitigation_results.items() if v.get("success")],
            "failed_attributes": [k for k, v in mitigation_results.items() if not v.get("success")],
            "mitigation_results": mitigation_results
        }
    
    # ========== PHASE 3: RE-EVALUATE AFTER MITIGATION ==========
    
    def evaluate_mitigated_bias(self, mitigation_results: Dict[str, Any], baseline_evaluation: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        PHASE 3: Re-evaluate bias AFTER applying mitigation.
        
        Uses same metrics as Phase 1 but on mitigated predictions.
        If baseline_evaluation is provided, attributes that were not mitigated
        will simply inherit their baseline metrics to prevent nulls.
        
        Returns:
            {
                "phase": "post_mitigation_evaluation",
                "bias_metrics": {
                    "age": {
                        "statistical_parity_difference": {...},
                        "disparate_impact_ratio": {...},
                        "equalized_odds_difference": {...}
                    }
                },
                "overall_status": "PASSED" | "FAILED"
            }
        """
        print("\n" + "=" * 60)
        print("PHASE 3: RE-EVALUATING BIAS AFTER MITIGATION")
        print("=" * 60)
        
        evaluation_after = {}
        
        for attr, results in mitigation_results.items():
            if not results.get("success", False):
                print(f"\n⚠️  Skipping {attr} (mitigation failed)")
                continue
            
            print(f"\n📊 Analyzing: {attr}")
            
            y_test = results["y_test"]
            y_pred = results["y_pred"]
            A_test = self._normalize_sensitive_feature(results["A_test"])
            
            attr_metrics = {}
            
            # Metric 1: Statistical Parity Difference (After)
            spd_after = demographic_parity_difference(
                y_true=y_test,
                y_pred=y_pred,
                sensitive_features=A_test
            )
            attr_metrics["statistical_parity_difference"] = {
                "value": float(spd_after),
                "threshold": 0.10,
                "passed": abs(spd_after) < 0.10,
                "interpretation": self._interpret_spd(spd_after)
            }
            print(f"  Statistical Parity Difference: {spd_after:.4f} {attr_metrics['statistical_parity_difference']['interpretation']}")
            
            # Metric 2: Disparate Impact Ratio (After)
            dpr_after = demographic_parity_ratio(
                y_true=y_test,
                y_pred=y_pred,
                sensitive_features=A_test
            )
            attr_metrics["disparate_impact_ratio"] = {
                "value": float(dpr_after) if dpr_after is not None else None,
                "threshold": 0.80,
                "passed": (dpr_after >= 0.80) if dpr_after is not None else False,
                "interpretation": self._interpret_dpr(dpr_after)
            }
            print(f"  Disparate Impact Ratio: {dpr_after:.4f} {attr_metrics['disparate_impact_ratio']['interpretation']}")
            
            # Metric 3: Equalized Odds Difference (After)
            eod_after = equalized_odds_difference(
                y_true=y_test,
                y_pred=y_pred,
                sensitive_features=A_test
            )
            attr_metrics["equalized_odds_difference"] = {
                "value": float(eod_after),
                "threshold": 0.10,
                "passed": abs(eod_after) < 0.10,
                "interpretation": self._interpret_eod(eod_after)
            }
            print(f"  Equalized Odds Difference: {eod_after:.4f} {attr_metrics['equalized_odds_difference']['interpretation']}")
            
            evaluation_after[attr] = attr_metrics
            
        # Fallback to baseline metrics for unmitigated attributes
        if baseline_evaluation and "bias_metrics" in baseline_evaluation:
            for attr, baseline_metrics in baseline_evaluation["bias_metrics"].items():
                if attr not in evaluation_after:
                    print(f"\n📌 {attr} was not mitigated; carrying over baseline metrics.")
                    evaluation_after[attr] = baseline_metrics
        
        overall_status = self._determine_overall_status(evaluation_after)
        print(f"\n📌 Overall Status: {overall_status}")
        
        return {
            "phase": "post_mitigation_evaluation",
            "bias_metrics": evaluation_after,
            "overall_status": overall_status
        }
    
    # ========== PHASE 4: GENERATE REPORT ==========
    
    def generate_mitigation_report(self, baseline: Dict, mitigated: Dict) -> Dict[str, Any]:
        """
        PHASE 4: Generate comprehensive before/after comparison report.
        
        Shows:
        - Baseline metrics
        - Mitigated metrics
        - % improvement for each metric
        - Recommendations
        """
        print("\n" + "=" * 60)
        print("PHASE 4: GENERATING MITIGATION REPORT")
        print("=" * 60)
        
        report = {
            "baseline": baseline,
            "after_mitigation": mitigated,
            "improvements": {},
            "summary": {}
        }
        
        baseline_metrics = baseline.get("bias_metrics", {})
        mitigated_metrics = mitigated.get("bias_metrics", {})
        
        total_metrics_improved = 0
        total_metrics_passed = 0
        
        for attr in baseline_metrics:
            if attr not in mitigated_metrics:
                # If it's completely missing, we treat after as before to avoid nulls
                mitigated_metrics[attr] = baseline_metrics[attr]
            
            print(f"\n📈 {attr} - Before/After Comparison:")
            
            improvement = {}
            attr_improvements = 0
            attr_passed = 0
            
            # Statistical Parity Difference
            spd_before = baseline_metrics[attr].get("statistical_parity_difference", {}).get("value")
            spd_after = mitigated_metrics[attr].get("statistical_parity_difference", {}).get("value")
            
            if spd_before is not None and spd_after is not None:
                spd_improvement = {
                    "before": float(spd_before),
                    "after": float(spd_after),
                    "difference": float(spd_after - spd_before),
                }
                
                # Calculate % improvement (reduction in absolute bias)
                if spd_before != 0:
                    spd_improvement["percent_improvement"] = float(
                        (abs(spd_before) - abs(spd_after)) / abs(spd_before) * 100
                    )
                
                improvement["statistical_parity_difference"] = spd_improvement
                
                print(f"  SPD: {spd_before:.4f} → {spd_after:.4f} ({spd_improvement.get('percent_improvement', 0):.1f}% improvement)")
                
                if mitigated_metrics[attr].get("statistical_parity_difference", {}).get("passed"):
                    attr_passed += 1
                
                if abs(spd_after) < abs(spd_before):
                    attr_improvements += 1
            
            # Disparate Impact Ratio
            dpr_before = baseline_metrics[attr].get("disparate_impact_ratio", {}).get("value")
            dpr_after = mitigated_metrics[attr].get("disparate_impact_ratio", {}).get("value")
            
            if dpr_before is not None and dpr_after is not None:
                improvement["disparate_impact_ratio"] = {
                    "before": float(dpr_before),
                    "after": float(dpr_after),
                    "difference": float(dpr_after - dpr_before),
                }
                
                print(f"  DPR: {dpr_before:.4f} → {dpr_after:.4f} (moved {'toward' if dpr_after > dpr_before else 'away from'} 0.80 threshold)")
                
                if mitigated_metrics[attr].get("disparate_impact_ratio", {}).get("passed"):
                    attr_passed += 1
                
                if abs(dpr_after - 0.80) < abs(dpr_before - 0.80):
                    attr_improvements += 1
            
            # Equalized Odds
            eod_before = baseline_metrics[attr].get("equalized_odds_difference", {}).get("value")
            eod_after = mitigated_metrics[attr].get("equalized_odds_difference", {}).get("value")
            
            if eod_before is not None and eod_after is not None:
                eod_improvement = {
                    "before": float(eod_before),
                    "after": float(eod_after),
                    "difference": float(eod_after - eod_before),
                }
                
                if eod_before != 0:
                    eod_improvement["percent_improvement"] = float(
                        (abs(eod_before) - abs(eod_after)) / abs(eod_before) * 100
                    )
                
                improvement["equalized_odds_difference"] = eod_improvement
                
                print(f"  EOD: {eod_before:.4f} → {eod_after:.4f} ({eod_improvement.get('percent_improvement', 0):.1f}% improvement)")
                
                if mitigated_metrics[attr].get("equalized_odds_difference", {}).get("passed"):
                    attr_passed += 1
                
                if abs(eod_after) < abs(eod_before):
                    attr_improvements += 1
            
            report["improvements"][attr] = {
                "metrics": improvement,
                "metrics_passed": attr_passed,
                "metrics_improved": attr_improvements
            }
            
            total_metrics_improved += attr_improvements
            total_metrics_passed += attr_passed
        
        # Summary
        report["summary"] = {
            "total_protected_attributes": len(baseline_metrics),
            "total_metrics_passed": total_metrics_passed,
            "total_metrics_improved": total_metrics_improved,
            "mitigation_effectiveness": self._assess_effectiveness(baseline, mitigated)
        }
        
        print(f"\n✅ Report generated successfully")
        print(f"  Metrics passed: {total_metrics_passed}")
        print(f"  Metrics improved: {total_metrics_improved}")
        
        return report
    
    # ========== INTERPRETATION HELPERS ==========
    
    def _interpret_spd(self, value: float) -> str:
        """Interpret Statistical Parity Difference"""
        if abs(value) < 0.10:
            return "✅ PASS"
        elif abs(value) < 0.15:
            return "⚠️ WARNING"
        else:
            return "❌ FAIL"
    
    def _interpret_dpr(self, value: Optional[float]) -> str:
        """Interpret Disparate Impact Ratio"""
        if value is None:
            return "⚠️ N/A"
        if value >= 0.80:
            return "✅ PASS (80% rule)"
        elif value >= 0.70:
            return "⚠️ WARNING"
        else:
            return "❌ FAIL"
    
    def _interpret_eod(self, value: float) -> str:
        """Interpret Equalized Odds Difference"""
        if abs(value) < 0.10:
            return "✅ PASS"
        else:
            return "❌ FAIL"
    
    def _determine_overall_status(self, evaluation: Dict) -> str:
        """Determine if all metrics pass"""
        if not evaluation:
            return "UNKNOWN"
        
        passed = 0
        total = 0
        
        for attr_metrics in evaluation.values():
            for metric_data in attr_metrics.values():
                total += 1
                if metric_data.get("passed", False):
                    passed += 1
        
        if total == 0:
            return "UNKNOWN"
        
        if passed == total:
            return "✅ PASSED: All bias metrics acceptable"
        elif passed >= total * 0.5:
            return "⚠️ PARTIAL: Some bias metrics improved"
        else:
            return "❌ FAILED: Most bias metrics still high"
    
    def _assess_effectiveness(self, baseline: Dict, mitigated: Dict) -> str:
        """Assess overall mitigation effectiveness"""
        baseline_status = baseline.get("overall_status", "")
        mitigated_status = mitigated.get("overall_status", "")
        
        if "PASSED" in mitigated_status and "PASSED" not in baseline_status:
            return "🎯 HIGHLY EFFECTIVE - Bias resolved"
        elif "PARTIAL" in mitigated_status or "⚠️" in mitigated_status:
            return "✅ MODERATELY EFFECTIVE - Some improvement"
        else:
            return "⚠️ LIMITED EFFECTIVENESS - May need additional mitigation"

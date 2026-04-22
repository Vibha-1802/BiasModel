import pandas as pd
import numpy as np
from fairlearn.metrics import (
    demographic_parity_difference,
    demographic_parity_ratio,
    equalized_odds_difference,
)
from fairlearn.preprocessing import Reweigher
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from typing import Dict, Any, List

class BiasMitigationEngine:
    """
    Implements fairlearn-based bias evaluation and mitigation
    based on LLM recommendations
    """
    
    def __init__(self, df: pd.DataFrame, bias_plan: Dict[str, Any]):
        """
        Args:
            df: Dataset
            bias_plan: LLM response with bias recommendations
        """
        self.df = df
        self.bias_plan = bias_plan
        self.protected_attributes = bias_plan.get("protected_attributes", [])
        self.target_col = bias_plan.get("target_variable")
        self.positive_label = bias_plan.get("positive_outcome_label")
        self.recommended_metrics = bias_plan.get("recommended_detection_metrics", [])
        self.mitigation_methods = bias_plan.get("recommended_mitigation", {})
    
    # ========== EVALUATION PHASE ==========
    
    def evaluate_baseline_bias(self) -> Dict[str, Any]:
        """
        Step 1: Evaluate bias using recommended metrics
        Returns metrics BEFORE mitigation
        """
        y = self.df[self.target_col].astype(int)
        evaluation = {}
        
        for attr in self.protected_attributes:
            if attr not in self.df.columns:
                continue
            
            sensitive_features = self.df[attr]
            attr_metrics = {}
            
            # Metric 1: Statistical Parity Difference
            if "statistical_parity_difference" in self.recommended_metrics:
                spd = demographic_parity_difference(
                    y_true=y,
                    y_pred=y,  # Using actual labels as proxy
                    sensitive_features=sensitive_features
                )
                attr_metrics["statistical_parity_difference"] = {
                    "value": float(spd),
                    "threshold": 0.10,  # Industry standard
                    "passed": abs(spd) < 0.10,
                    "interpretation": self._interpret_spd(spd)
                }
            
            # Metric 2: Disparate Impact Ratio
            if "disparate_impact_ratio" in self.recommended_metrics:
                dpr = demographic_parity_ratio(
                    y_true=y,
                    y_pred=y,
                    sensitive_features=sensitive_features
                )
                attr_metrics["disparate_impact_ratio"] = {
                    "value": float(dpr),
                    "threshold": 0.80,  # Legal threshold (80% rule)
                    "passed": dpr >= 0.80,
                    "interpretation": self._interpret_dpr(dpr)
                }
            
            # Additional: Equalized Odds Difference
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
            
            evaluation[attr] = attr_metrics
        
        return {
            "phase": "baseline_evaluation",
            "bias_metrics": evaluation,
            "overall_status": self._determine_overall_status(evaluation)
        }
    
    # ========== MITIGATION PHASE ==========
    
    def apply_reweighing(self, test_size: float = 0.2) -> Dict[str, Any]:
        """
        Step 2: Apply fairlearn's Reweighing mitigation
        (pre-processing technique)
        
        Reweighing: Assigns weights to training samples to reduce bias
        """
        
        # Split data
        X = self.df.drop(columns=[self.target_col])
        y = self.df[self.target_col].astype(int)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        mitigation_results = {}
        
        # Apply reweighing for each protected attribute
        for attr in self.protected_attributes:
            if attr not in self.df.columns:
                continue
            
            # Get sensitive features for training set
            A_train = X_train[attr]
            A_test = X_test[attr]
            
            # Step 2a: Initialize reweigher
            reweigher = Reweigher(
                sensitive_feature=attr,
                parity_metric="demographic_parity"
            )
            
            # Step 2b: Fit reweigher on training data
            reweigher.fit(X_train, y_train, sensitive_features=A_train)
            
            # Step 2c: Get sample weights
            X_train_weighted = reweigher.transform(X_train)
            
            # Step 2d: Train model with reweighted data
            model = LogisticRegression(max_iter=1000, random_state=42)
            model.fit(X_train_weighted, y_train, 
                     sample_weight=X_train_weighted.get("weights", None))
            
            # Step 2e: Make predictions on test set
            y_pred = model.predict(X_test)
            
            # Store results
            mitigation_results[attr] = {
                "method": "reweighing",
                "model": model,
                "y_pred": y_pred,
                "A_test": A_test,
                "y_test": y_test
            }
        
        return mitigation_results
    
    # ========== POST-MITIGATION EVALUATION ==========
    
    def evaluate_mitigated_bias(self, mitigation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 3: Evaluate bias AFTER mitigation
        Compare with baseline to show improvement
        """
        evaluation_after = {}
        
        for attr, results in mitigation_results.items():
            y_test = results["y_test"]
            y_pred = results["y_pred"]
            A_test = results["A_test"]
            
            attr_metrics = {}
            
            # Metric 1: Statistical Parity Difference (After)
            if "statistical_parity_difference" in self.recommended_metrics:
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
            
            # Metric 2: Disparate Impact Ratio (After)
            if "disparate_impact_ratio" in self.recommended_metrics:
                dpr_after = demographic_parity_ratio(
                    y_true=y_test,
                    y_pred=y_pred,
                    sensitive_features=A_test
                )
                attr_metrics["disparate_impact_ratio"] = {
                    "value": float(dpr_after),
                    "threshold": 0.80,
                    "passed": dpr_after >= 0.80,
                    "interpretation": self._interpret_dpr(dpr_after)
                }
            
            # Equalized Odds
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
            
            evaluation_after[attr] = attr_metrics
        
        return {
            "phase": "post_mitigation_evaluation",
            "bias_metrics": evaluation_after,
            "overall_status": self._determine_overall_status(evaluation_after)
        }
    
    # ========== COMPARISON & REPORTING ==========
    
    def generate_mitigation_report(self, baseline: Dict, mitigated: Dict) -> Dict[str, Any]:
        """
        Step 4: Generate comprehensive before/after report
        """
        report = {
            "baseline": baseline,
            "after_mitigation": mitigated,
            "improvements": {}
        }
        
        baseline_metrics = baseline.get("bias_metrics", {})
        mitigated_metrics = mitigated.get("bias_metrics", {})
        
        for attr in baseline_metrics:
            if attr not in mitigated_metrics:
                continue
            
            improvement = {
                "statistical_parity_difference": {
                    "before": baseline_metrics[attr].get("statistical_parity_difference", {}).get("value"),
                    "after": mitigated_metrics[attr].get("statistical_parity_difference", {}).get("value"),
                },
                "disparate_impact_ratio": {
                    "before": baseline_metrics[attr].get("disparate_impact_ratio", {}).get("value"),
                    "after": mitigated_metrics[attr].get("disparate_impact_ratio", {}).get("value"),
                }
            }
            
            # Calculate % improvement
            spd_before = improvement["statistical_parity_difference"]["before"]
            spd_after = improvement["statistical_parity_difference"]["after"]
            if spd_before != 0:
                improvement["statistical_parity_difference"]["percent_change"] = (
                    (spd_before - spd_after) / abs(spd_before) * 100
                )
            
            report["improvements"][attr] = improvement
        
        return report
    
    # ========== INTERPRETATION HELPERS ==========
    
    def _interpret_spd(self, value: float) -> str:
        """Interpret Statistical Parity Difference"""
        if abs(value) < 0.10:
            return "✅ PASS: Acceptable statistical parity"
        elif abs(value) < 0.15:
            return "⚠️ WARNING: Marginal statistical parity"
        else:
            return "❌ FAIL: Significant bias detected"
    
    def _interpret_dpr(self, value: float) -> str:
        """Interpret Disparate Impact Ratio"""
        if value >= 0.80:
            return "✅ PASS: Meets 80% rule (legally safe)"
        elif value >= 0.70:
            return "⚠️ WARNING: Below 80% rule, legally risky"
        else:
            return "❌ FAIL: Severe disparate impact"
    
    def _interpret_eod(self, value: float) -> str:
        """Interpret Equalized Odds Difference"""
        if abs(value) < 0.10:
            return "✅ PASS: Equalized odds achieved"
        else:
            return "❌ FAIL: Unequal odds detected"
    
    def _determine_overall_status(self, evaluation: Dict) -> str:
        """Determine if all metrics pass"""
        all_passed = all(
            attr_metrics.get(metric, {}).get("passed", False)
            for attr_metrics in evaluation.values()
            for metric in attr_metrics
        )
        
        if all_passed:
            return "PASSED: All bias metrics acceptable"
        else:
            return "FAILED: Some bias metrics still high"
from __future__ import annotations

from pydantic import BaseModel, Field


class MitigationStrategies(BaseModel):
    pre_processing: list[str] = Field(
        default_factory=list,
        description=(
            "Pre-processing techniques applied to the data before model training. "
            "Use exact names: reweighing, disparate_impact_remover, optimized_preprocessing"
        ),
    )
    in_processing: list[str] = Field(
        default_factory=list,
        description=(
            "In-processing techniques that modify the learning algorithm itself. "
            "Use exact names: adversarial_debiasing, prejudice_remover, meta_fair_classifier. "
            "Only recommend if schema_inference.has_model_predictions is true."
        ),
    )
    post_processing: list[str] = Field(
        default_factory=list,
        description=(
            "Post-processing techniques applied to model predictions. "
            "Use exact names: equalized_odds_postprocessing, calibrated_equalized_odds, reject_option_classification. "
            "Only recommend if schema_inference.has_model_predictions is true."
        ),
    )


class BiasAnalysisPlan(BaseModel):
    dataset_domain: str = Field(
        description=(
            "Detected dataset domain. Must be one of: "
            "credit_scoring, hiring, healthcare, criminal_justice, housing, unknown"
        ),
    )
    protected_attributes: list[str] = Field(
        description=(
            "Exact column names from the dataset that are protected attributes. "
            "Derive from protected_attribute_candidates and group_outcome_stats keys."
        ),
    )
    target_variable: str | None = Field(
        default=None,
        description="The prediction target column name from target_analysis.target_column.",
    )
    positive_outcome_label: str | None = Field(
        default=None,
        description=(
            "The label value representing a favorable outcome "
            "(e.g. '1', 'approved', 'hired'). "
            "Derive from target_analysis.positive_class_label."
        ),
    )
    bias_types_detected: list[str] = Field(
        description=(
            "Types of bias present in the dataset. "
            "Use only these exact names: "
            "representation_bias, historical_bias, measurement_bias, "
            "aggregation_bias, label_bias, proxy_discrimination"
        ),
    )
    recommended_detection_metrics: list[str] = Field(
        description=(
            "Fairness metrics to compute, ordered by priority. "
            "These names map directly to library function names — use exactly: "
            "statistical_parity_difference, disparate_impact_ratio, "
            "equal_opportunity_difference, average_odds_difference, "
            "predictive_parity_difference, theil_index. "
            "Always include statistical_parity_difference and disparate_impact_ratio as baseline. "
            "Only include equal_opportunity_difference and average_odds_difference "
            "if schema_inference.has_model_predictions is true."
        ),
    )
    recommended_mitigation: MitigationStrategies = Field(
        default_factory=MitigationStrategies,
    )
    reasoning: str = Field(
        description=(
            "Concise explanation (3-5 sentences) of why these specific metrics and "
            "mitigations were chosen, referencing key numbers from preliminary_bias_signals "
            "and group_outcome_stats."
        ),
    )

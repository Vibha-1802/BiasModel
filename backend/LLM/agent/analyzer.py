from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from .schemas import BiasAnalysisPlan
from .state import AgentState
from llm.client import llm

_DATASET_SYSTEM_PROMPT = """You are a bias detection expert. You will receive a structured dataset statistics summary and must return a BiasAnalysisPlan.

Follow these rules precisely:

PROTECTED ATTRIBUTES
- Use exact column names from protected_attribute_candidates and group_outcome_stats keys.
- Only include columns that are genuinely sensitive (race, gender, age, religion, nationality, disability, marital status).

BIAS TYPE DETECTION — use only these exact names:
- representation_bias: any group has representation < 0.15 of total rows
- historical_bias: group_outcome_stats shows consistent outcome disparity across all groups of an attribute
- proxy_discrimination: protected_feature_correlations shows Cramér's V > 0.4 for a non-protected column
- measurement_bias: missingness_by_group shows differential missing rates across groups (> 2x difference)
- aggregation_bias: intersectional_groups shows disparity that does not appear in individual attribute analysis
- label_bias: domain is criminal_justice or hiring and historical_bias is present (labels reflect past discriminatory decisions)

DETECTION METRICS — use only these exact names, ordered by priority:
- Always include: statistical_parity_difference, disparate_impact_ratio
- Include if disparate_impact_ratio < 0.8: equal_opportunity_difference
- Include if schema_inference.has_model_predictions is true: average_odds_difference, predictive_parity_difference
- Include if multiple protected attributes exist: theil_index

MITIGATION — use only these exact names:
- pre_processing: reweighing, disparate_impact_remover, optimized_preprocessing
- in_processing: adversarial_debiasing, prejudice_remover, meta_fair_classifier
- post_processing: equalized_odds_postprocessing, calibrated_equalized_odds, reject_option_classification
Rules:
- Always recommend reweighing in pre_processing if disparate_impact_ratio < 0.8
- Only recommend in_processing or post_processing if schema_inference.has_model_predictions is true
- If has_model_predictions is false, only recommend pre_processing techniques

REASONING
- Reference specific numbers from preliminary_bias_signals and group_outcome_stats in your reasoning.
- Keep reasoning to 3-5 sentences."""

_GENERAL_SYSTEM_PROMPT = """You are an AI fairness and bias detection expert. Answer the user's question clearly and accurately, citing relevant fairness metrics, statistical concepts, and industry best practices where appropriate. Be concise and precise."""


def bias_reasoning_step(state: AgentState) -> dict:
    analysis_data = state.get("analysis_data", "none")
    has_dataset = isinstance(analysis_data, dict)

    if has_dataset:
        analysis_str = json.dumps(analysis_data, indent=2)
        messages = [
            SystemMessage(content=_DATASET_SYSTEM_PROMPT),
            HumanMessage(content=f"Dataset statistics summary:\n\n{analysis_str}"),
        ]
        structured_llm = llm.with_structured_output(BiasAnalysisPlan)
        plan: BiasAnalysisPlan = structured_llm.invoke(messages)
        return {"bias_plan": plan.model_dump(), "bias_report": ""}

    messages = [
        SystemMessage(content=_GENERAL_SYSTEM_PROMPT),
        HumanMessage(content=state["query"]),
    ]
    response = llm.invoke(messages)
    return {"bias_report": response.content, "bias_plan": None}

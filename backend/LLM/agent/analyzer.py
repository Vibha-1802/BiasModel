from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from .schemas import BiasAnalysisPlan
from .state import AgentState
from llm.client import llm

_DATASET_SYSTEM_PROMPT = """You are a fairness and bias detection expert. Your goal is to analyze a structured dataset statistics summary and provide a comprehensive BiasAnalysisPlan.

### GUIDELINES FOR ACCURATE ANALYSIS:

1. PROTECTED ATTRIBUTES:
   - Identify sensitive attributes from 'protected_attribute_candidates' and 'group_outcome_stats'.
   - Common attributes: race, gender, age, religion, nationality, disability, marital status, income, zip code.

2. BIAS TYPE DETECTION:
   - representation_bias: Detected when a sensitive group's representation is significantly lower than its expected real-world distribution or the majority group.
   - historical_bias: Evident when 'group_outcome_stats' shows consistent outcome disparities that reflect long-standing societal inequalities.
   - proxy_discrimination: Look for high correlations (e.g., Cramér's V > 0.3) between protected attributes and non-protected features in 'protected_feature_correlations'.
   - measurement_bias: Indicated by differential missingness rates across groups in 'missingness_by_group' or skewed distributions in 'feature_stats'.
   - aggregation_bias: Check 'intersectional_groups' for disparities that are hidden when looking at single attributes.
   - label_bias: Occurs in domains like hiring or criminal justice where the target variable may encode historical human prejudices.

3. FAIRNESS METRICS (Ordered by relevance):
   - Group Fairness: statistical_parity_difference, disparate_impact_ratio.
   - Individual/Intersectional: theil_index, generalized_entropy_index.
   - Error Rate Parity (If 'has_model_predictions' is true): equal_opportunity_difference, average_odds_difference, predictive_parity_difference.
   - Representation: kl_divergence, jensen_shannon_divergence.

4. MITIGATION STRATEGIES:
   - Pre-processing: Recommend for raw datasets. (e.g., reweighing, disparate_impact_remover, LFR).
   - In-processing: Recommend for training phases. (e.g., adversarial_debiasing, exponentiated_gradient_reduction).
   - Post-processing: Recommend for existing models with predictions. (e.g., equalized_odds_postprocessing, reject_option_classification).
   - If 'has_model_predictions' is FALSE, you may still suggest in-processing/post-processing as potential future steps if the user intends to build a model.

### REASONING:
- Reference specific metrics and numbers from 'preliminary_bias_signals', 'group_outcome_stats', and 'intersectional_groups'.
- Explain the real-world implications of the detected biases.
- Keep reasoning to 3-5 concise, high-impact sentences."""

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

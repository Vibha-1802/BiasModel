from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict):
    query: str
    category: str           # set by router node or pre-set at API level
    analysis_data: dict[str, Any] | str
    bias_report: str        # free-text output for general/behavioral queries
    bias_plan: dict[str, Any] | None  # structured BiasAnalysisPlan for dataset analysis

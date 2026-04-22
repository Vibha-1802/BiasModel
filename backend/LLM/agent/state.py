from typing import TypedDict, Annotated, List

class AgentState(TypedDict):
    query: str
    category: str
    analysis_data: str
    bias_report: str

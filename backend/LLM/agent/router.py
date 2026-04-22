from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from .state import AgentState
from llm.client import llm

_ROUTER_SYSTEM = (
    "You are a routing classifier. Classify the user's query into exactly one category:\n"
    "- 'dataset': the query is about a specific dataset, its statistics, or bias within it\n"
    "- 'behavioral': the query is about how a deployed model behaves or makes decisions\n"
    "- 'general': general AI ethics, fairness concepts, metric definitions, or methodology questions\n"
    "Respond with only the category name."
)


class RouteDecision(BaseModel):
    destination: str = Field(
        description="Must be exactly one of: 'dataset', 'behavioral', 'general'"
    )


def route_query(state: AgentState) -> dict:
    # If category was pre-set at the API level (e.g. dataset analysis), skip the LLM call.
    if state.get("category"):
        return {}

    structured_llm = llm.with_structured_output(RouteDecision)
    messages = [
        SystemMessage(content=_ROUTER_SYSTEM),
        HumanMessage(content=state["query"]),
    ]
    decision = structured_llm.invoke(messages)
    return {"category": decision.destination}


def get_route(state: AgentState) -> str:
    return state["category"]

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from .analyzer import bias_reasoning_step
from .router import get_route, route_query
from .state import AgentState

workflow = StateGraph(AgentState)

workflow.add_node("router", route_query)
workflow.add_node("analyzer", bias_reasoning_step)

workflow.add_edge(START, "router")
workflow.add_conditional_edges("router", get_route, {
    "dataset": "analyzer",
    "behavioral": "analyzer",
    "general": "analyzer",
})
workflow.add_edge("analyzer", END)

bias_agent = workflow.compile()

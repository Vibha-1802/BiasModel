from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .router import route_query
from .analyzer import bias_reasoning_step

workflow = StateGraph(AgentState)
workflow.add_node("analyzer", bias_reasoning_step)

workflow.add_conditional_edges(START, route_query, {
    "dataset": "analyzer",
    "behavioral": "analyzer",
    "general": "analyzer"
})
workflow.add_edge("analyzer", END)
bias_agent = workflow.compile()

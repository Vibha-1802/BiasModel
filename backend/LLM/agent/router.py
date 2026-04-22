from .state import AgentState
from llm.client import llm
from pydantic import BaseModel, Field

class RouteDecision(BaseModel):
    destination: str = Field(description="Must be 'dataset', 'behavioral', or 'general'")

def route_query(state: AgentState):
    structured_llm = llm.with_structured_output(RouteDecision)
    prompt = f"Analyze if this query is about 'dataset' stats, 'behavioral' model bias, or 'general' ethics: {state['query']}"
    decision = structured_llm.invoke(prompt)
    return [decision.destination]

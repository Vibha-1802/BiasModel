from .state import AgentState
from llm.client import llm

def bias_reasoning_step(state: AgentState):
    """
    Core reasoning step to analyze bias based on the query and any collected data.
    """
    prompt = f"Perform a detailed bias analysis for the following query: {state['query']}. " \
             f"Category: {state.get('category', 'unknown')}. " \
             f"Data context: {state.get('analysis_data', 'none')}"
    
    response = llm.invoke(prompt)
    
    # Return updated state
    return {"bias_report": response.content}

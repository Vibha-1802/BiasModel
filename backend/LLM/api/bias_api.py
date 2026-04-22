from fastapi import FastAPI
from agent.orchestrator import bias_agent

app = FastAPI(title="Bias Detection API")

@app.post("/analyze")
async def analyze_bias(user_query: str):
    inputs = {"query": user_query}
    result = await bias_agent.ainvoke(inputs)
    return {"report": result["bias_report"]}

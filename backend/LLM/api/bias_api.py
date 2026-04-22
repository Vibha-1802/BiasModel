import logging
import time
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from agent.orchestrator import bias_agent
from services.dataset_formatter import format_bias_analysis_payload

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("llm_service")

app = FastAPI(title="Bias Detection LLM Service")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    arrival_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    
    logger.info(f"Incoming request: {request.method} {request.url.path} at {arrival_time}")
    
    response = await call_next(request)
    
    end_time = time.time()
    completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    duration = end_time - start_time
    
    logger.info(f"Response generated at {completion_time}")
    logger.info(f"Total time taken for {request.url.path}: {duration:.4f} seconds")
    
    return response

class AnalyzeBiasRequest(BaseModel):
    user_query: str | None = Field(
        default=None,
        description="Natural-language question about bias or fairness.",
    )
    analysis_data: dict[str, Any] | None = Field(
        default=None,
        description="Raw dataset statistics payload from the dataset analysis service.",
    )


@app.post("/analyze")
async def analyze_bias(payload: AnalyzeBiasRequest) -> dict[str, Any]:
    """
    Two paths:
    - analysis_data provided → normalize stats, pass to LLM, return structured BiasAnalysisPlan.
    - user_query only → route and return a free-text report.
    """
    if payload.analysis_data is not None:
        formatted = format_bias_analysis_payload(payload.analysis_data)
        inputs: dict[str, Any] = {
            "query": payload.user_query or "Analyze this dataset for bias",
            "category": "dataset",   # pre-set so the router skips its LLM call
            "analysis_data": formatted,
            "bias_report": "",
            "bias_plan": None,
        }
        result = await bias_agent.ainvoke(inputs)
        return result["bias_plan"]

    if payload.user_query:
        inputs = {
            "query": payload.user_query,
            "category": "",          # empty so the router classifies it
            "analysis_data": "none",
            "bias_report": "",
            "bias_plan": None,
        }
        result = await bias_agent.ainvoke(inputs)
        return {"report": result["bias_report"]}

    raise HTTPException(
        status_code=400,
        detail="Provide either analysis_data for structured analysis or user_query for a text report.",
    )

import httpx
from fastapi import HTTPException
from app.services.bias_services import process_dataset, analyze_dataset

LLM_SERVICE_URL = "http://localhost:8001/analyze"

async def upload_dataset_controller(file):
    try:
        return await process_dataset(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def analyze_dataset_controller(file):
    try:
        # 1. Compute statistical analysis
        stats = await analyze_dataset(file)
        
        # 2. Call LLM service for bias reasoning
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    LLM_SERVICE_URL,
                    json={"analysis_data": stats},
                    timeout=60.0
                )
                if response.status_code == 200:
                    stats["bias_plan"] = response.json()
                else:
                    stats["bias_plan"] = {
                        "error": f"LLM service returned status code {response.status_code}",
                        "details": response.text
                    }
            except Exception as llm_err:
                stats["bias_plan"] = {
                    "error": "Failed to connect to LLM service",
                    "details": str(llm_err)
                }
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
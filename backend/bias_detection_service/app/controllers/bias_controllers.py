from fastapi import HTTPException
from app.services.bias_services import process_dataset,analyze_dataset

async def upload_dataset_controller(file):
    try:
        return await process_dataset(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def analyze_dataset_controller(file):
    try:
        return await analyze_dataset(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import APIRouter, UploadFile, File, Query
from app.controllers.bias_controllers import upload_dataset_controller,analyze_dataset_controller

router = APIRouter()

@router.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    return await upload_dataset_controller(file)

@router.post("/analyze-dataset")
async def analyze_dataset(
    file: UploadFile = File(...),
    response_mode: str = Query("summary", pattern="^(summary|full)$"),
):
    return await analyze_dataset_controller(file, include_full=(response_mode == "full"))
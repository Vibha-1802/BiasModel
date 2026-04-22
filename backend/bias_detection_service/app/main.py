from fastapi import FastAPI
from app.routes.bias_routes import router as bias_routes

app = FastAPI(title="Bias Detection API")

app.include_router(bias_routes, prefix="/bias")

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
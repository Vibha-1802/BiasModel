from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.bias_routes import router as bias_routes

app = FastAPI(title="Bias Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bias_routes, prefix="/bias")

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
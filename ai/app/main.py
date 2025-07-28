from fastapi import FastAPI
from ai.app.api.routers import analysis

app = FastAPI()

app.include_router(analysis.router, prefix="/api", tags=["analysis"])

@app.get("/")
def read_root():
    return {"Hello": "World"}
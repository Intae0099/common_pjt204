from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.handlers import (
    api_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
    http_error_handler,
)
from app.api.exceptions import APIException
from app.api.routers import analysis
from llm.models.model_loader import ModelLoader
from utils.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup: Loading models...")
    ModelLoader.get_embedding_model()
    ModelLoader.get_cross_encoder_model()
    logger.info("Application startup: Models loaded.")
    yield
    logger.info("Application shutdown.")

app = FastAPI(lifespan=lifespan)

app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(analysis.router, prefix="/api", tags=["analysis"])

@app.get("/")
def read_root():
    return {"Hello": "World"}

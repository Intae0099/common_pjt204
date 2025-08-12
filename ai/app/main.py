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
from app.api.routers import analysis, structuring, search, chat, consult
from config.settings import get_api_settings
from llm.models.model_loader import ModelLoader
from utils.logger import setup_logger, get_logger
from fastapi.middleware.cors import CORSMiddleware

setup_logger()
logger = get_logger(__name__)

# 설정 로드
api_settings = get_api_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup: Loading models...")
    ModelLoader.get_embedding_model()
    ModelLoader.get_cross_encoder_model()
    logger.info("Application startup: Models loaded.")
    yield
    logger.info("Application shutdown.")

app = FastAPI(lifespan=lifespan, response_model_exclude_none=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=api_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(analysis.router, prefix="/api", tags=["analysis"])
app.include_router(structuring.router, prefix="/api", tags=["structuring"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(chat.router, prefix="/api/ai", tags=["Chat"])
app.include_router(consult.router, prefix="/api", tags=["Consultation"])

@app.get("/")
def read_root():
    return {"Hello": "World"}

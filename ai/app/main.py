import json
from contextlib import asynccontextmanager
from datetime import datetime, date

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime, date and Pydantic objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        # Handle Pydantic models
        if hasattr(obj, 'model_dump'):
            return obj.model_dump()
        # Handle dataclasses
        if hasattr(obj, '__dataclass_fields__'):
            return {field.name: getattr(obj, field.name) for field in obj.__dataclass_fields__.values()}
        return super().default(obj)

from app.api.handlers import (
    api_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
    http_error_handler,
    service_exception_handler,
)
from app.api.exceptions import APIException
from utils.exceptions import BaseServiceException
from app.api.routers import analysis, structuring, search, chat, consult, queue_status
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
    
    # 큐 매니저 시작
    from services.lightweight_queue_manager import get_queue_manager
    queue_manager = get_queue_manager()
    await queue_manager.start()
    logger.info("Application startup: Queue manager started.")
    
    yield
    
    # 큐 매니저 정지
    await queue_manager.stop()
    logger.info("Application shutdown: Queue manager stopped.")
    logger.info("Application shutdown.")

app = FastAPI(lifespan=lifespan, response_model_exclude_none=True)

# Configure custom JSON encoder for FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

# Monkey patch the default JSONResponse to use our encoder
original_render = JSONResponse.render

def custom_render(self, content):
    return json.dumps(
        content,
        cls=DateTimeEncoder,
        ensure_ascii=False,
        allow_nan=False,
        indent=None,
        separators=(",", ":"),
    ).encode("utf-8")

JSONResponse.render = custom_render

app.add_middleware(
    CORSMiddleware,
    allow_origins=api_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(BaseServiceException, service_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(analysis.router, prefix="/api", tags=["analysis"])
app.include_router(structuring.router, prefix="/api", tags=["structuring"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(chat.router, prefix="/api/ai", tags=["Chat"])
app.include_router(consult.router, prefix="/api", tags=["Consultation"])
app.include_router(queue_status.router, prefix="/api", tags=["Queue"])

@app.get("/")
def read_root():
    return {"Hello": "World"}

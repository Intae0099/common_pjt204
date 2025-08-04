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
from app.api.routers import analysis, structuring, search, chat
from llm.models.model_loader import ModelLoader
from utils.logger import setup_logger, get_logger
from fastapi.middleware.cors import CORSMiddleware

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

app = FastAPI(lifespan=lifespan, response_model_exclude_none=True)

origins = [
    "http://localhost:5173",  # Vue.js 개발 서버 주소
    "https://i13b204.p.ssafy.io/"
    # "http://your-production-domain.com", # 나중에 배포할 프론트엔드 도메인 주소도 추가
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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

@app.get("/")
def read_root():
    return {"Hello": "World"}

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

app = FastAPI()

app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(analysis.router, prefix="/api", tags=["analysis"])

@app.get("/")
def read_root():
    return {"Hello": "World"}

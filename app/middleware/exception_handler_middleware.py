from fastapi import Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from app.helpers.exceptions import CustomException
from app.helpers.response_helper import error_response

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != 'body')
        message = error["msg"]
        errors.append(f"{field}: {message}")
    return error_response("Validation error", status.HTTP_422_UNPROCESSABLE_ENTITY, errors)

async def custom_exception_handler(request: Request, exc: CustomException):
    errors = []
    if exc.errors:
        errors = exc.errors
    return error_response(exc.message, exc.status_code, errors)

async def http_exception_handler(request: Request, exc: HTTPException):
    return error_response(exc.detail, exc.status_code)

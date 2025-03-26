
# app/core/exceptions.py
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List, Union

from app.core.config import settings


class AppExceptionBase(Exception):
    """Base class for application exceptions."""
    def __init__(
        self,
        status_code: int,
        message: str,
        detail: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    ):
        self.status_code = status_code
        self.message = message
        self.detail = detail


class BadRequestException(AppExceptionBase):
    """Exception raised for bad requests."""
    def __init__(
        self,
        message: str = "Bad request",
        detail: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    ):
        super().__init__(status.HTTP_400_BAD_REQUEST, message, detail)


class NotFoundException(AppExceptionBase):
    """Exception raised for resources that were not found."""
    def __init__(
        self,
        message: str = "Resource not found",
        detail: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    ):
        super().__init__(status.HTTP_404_NOT_FOUND, message, detail)


class UnauthorizedException(AppExceptionBase):
    """Exception raised for unauthorized access."""
    def __init__(
        self,
        message: str = "Unauthorized",
        detail: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    ):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message, detail)


class ForbiddenException(AppExceptionBase):
    """Exception raised for forbidden access."""
    def __init__(
        self,
        message: str = "Forbidden",
        detail: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    ):
        super().__init__(status.HTTP_403_FORBIDDEN, message, detail)


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Setup exception handlers for the FastAPI application.
    """
    @app.exception_handler(AppExceptionBase)
    async def app_exception_handler(request: Request, exc: AppExceptionBase) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.message,
                "detail": exc.detail,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": "Validation error",
                "detail": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # In production, you might want to log this error
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        message = "Internal server error"
        
        # In development, show the original error
        if settings.ENV == "local":
            message = str(exc)
            
        return JSONResponse(
            status_code=status_code,
            content={
                "message": message,
            },
        )
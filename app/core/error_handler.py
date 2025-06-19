from fastapi import Request, FastAPI,HTTPException
from fastapi.responses import JSONResponse
from app.core.logging_utils import logger
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

def register_exception_handlers(app: FastAPI):

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception): #fastapi hooks it internally, as it showing unused
        logger.exception(f"Unhandled Exception at {request.url} - {str(exc)}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "message": "Internal server error",
                "code": HTTP_500_INTERNAL_SERVER_ERROR
            }
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(f"HTTPException at {request.url} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "code": exc.status_code
            }
        )

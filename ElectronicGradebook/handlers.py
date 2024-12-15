from fastapi import Request
from fastapi.responses import JSONResponse
import logging
from .exception import ApplicationException

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def setup_exception_handlers(app):
    @app.exception_handler(ApplicationException)
    async def handle_application_exception(request: Request, error: ApplicationException) -> JSONResponse:
        logger.error(f"Error handler caught at {request.url} with method {request.method}. {error}")
        content,status_code = error.to_response()
        return JSONResponse(
            content=content,
            status_code=status_code,
        )
from fastapi import Request as fastapiRequest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match
from fastapi.responses import JSONResponse
import uuid
from starlette.requests import Request as starletteRequest
import structlog
import time

class InputSanitizerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: fastapiRequest, call_next):
        # Ограничить размер query-параметров
        if len(str(request.url)) > 2000:
            return JSONResponse({"detail": "URL too long"}, status_code=414)
        return await call_next(request)

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: starletteRequest, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        structlog.contextvars.bind_contextvars(request_id=request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: starletteRequest, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger = structlog.get_logger("access")
        logger.info(
            "request_handled",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(process_time * 1000, 2),
        )
        return response
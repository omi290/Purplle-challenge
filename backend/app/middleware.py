import uuid
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)

class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        
        # Inject trace ID into request state
        request.state.trace_id = trace_id
        
        # Start timer
        start_time = time.time()
        
        # Process request
        response: Response = await call_next(request)
        
        # Record execution time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Trace-ID"] = trace_id
        
        # Log request details
        logger.info(
            f"Request: {request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time:.4f}s",
            extra={"trace_id": trace_id}
        )
        
        return response

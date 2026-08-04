from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from src.foundation.utilities.identifiers import generate_uuid
from src.foundation.logging.context import set_request_id

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate a unique request ID
        request_id = generate_uuid()
        
        # Set the request ID in the context var for logging
        set_request_id(request_id)
        
        # Process the request
        response: Response = await call_next(request)
        
        # Inject the request ID back into the response headers
        response.headers["X-Request-ID"] = request_id
        
        return response

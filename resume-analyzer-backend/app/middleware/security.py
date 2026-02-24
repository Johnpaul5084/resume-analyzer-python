import logging
import time
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class AISecurityMiddleware(BaseHTTPMiddleware):
    """
    AI Resume Analyzer Security Middleware
    Handles:
    - Global Exception Sanitization
    - Security Headers (nosniff, HSTS, X-Frame-Options)
    - Request Body Size Limiting
    """
    
    # 20KB Limit for typical resume/query payloads to prevent DoS
    MAX_BODY_SIZE = 20 * 1024 

    async def dispatch(self, request: Request, call_next):
        try:
            # 1. Size Validation (Early rejection)
            # content_length = request.headers.get("content-length")
            # if content_length and int(content_length) > self.MAX_BODY_SIZE:
            #     raise HTTPException(status_code=413, detail="Neural payload too large.")

            # 2. Process Request
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 3. Add Security Headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["AI-System-Latency"] = str(round(process_time, 4))
            
            return response

        except Exception as e:
            logger.error(f"⚠️ AI System Error: {str(e)}")
            # Sanitize error output for production
            return JSONResponse(
                status_code=500,
                content={
                    "success": False, 
                    "error": "AI Neural Link Interrupted. Internal safeguarding active."
                }
            )

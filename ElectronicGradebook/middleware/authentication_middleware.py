from jose import jwt, JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException


class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: str,algorithm: str):
        super().__init__(app)
        self.secret_key = secret_key
        self.algorithm = algorithm

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                scheme,token = auth_header.split()
                if scheme.lower() != "bearer":
                    raise ValueError("Invalid authentication scheme")
                payload = jwt.decode(token,self.secret_key,algorithms=[self.algorithm])
                request.state.user = {
                    "username": payload.get("sub"),
                    "id": payload.get("id"),
                    "role": payload.get("role")
                }
            except (ValueError, JWTError):
                raise HTTPException(status_code=401, detail="Invalid token")
        else:
            request.state.user = None
        response = await call_next(request)
        return response
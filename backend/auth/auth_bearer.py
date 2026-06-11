from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.auth.auth_handler import decode_access_token

class JWTBearer(HTTPBearer):
    """
    JWTBearer security dependency that handles token extraction
    from the Authorization: Bearer header and performs signature validation.
    """
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        credentials: Optional[HTTPAuthorizationCredentials] = await super(JWTBearer, self).__call__(request)
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme. Only Bearer tokens are supported."
                )
            
            # This will decode and validate the token; raises 401 on failure
            payload = decode_access_token(credentials.credentials)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Token invalid or expired"
                )
            
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credentials signature missing or invalid"
            )

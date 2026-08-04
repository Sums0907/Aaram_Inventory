from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from src.foundation.exceptions.base import UnauthorizedException
from .jwt import decode_access_token
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class CurrentUser(BaseModel):
    id: str
    username: str
    role: str

async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """Dependency to retrieve the current user from JWT token."""
    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedException(message="Invalid or expired token")
        
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException(message="Invalid token structure")
        
    # Placeholder for actual user retrieval
    return CurrentUser(
        id=user_id,
        username=payload.get("username", "unknown"),
        role=payload.get("role", "user")
    )

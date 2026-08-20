from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from src.foundation.exceptions.base import UnauthorizedException
from typing import List, Optional
from pydantic import BaseModel
from src.foundation.configuration import get_settings
from .jwt import decode_access_token, decode_aaramidentity_token

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class CurrentIdentityContext(BaseModel):
    user_id: str
    name: str
    applications: List[str]
    roles: List[str]
    permissions: List[str]

    @property
    def id(self) -> str:
        """Alias for backward compatibility with older route usages."""
        return self.user_id

# Alias to avoid breaking all existing imports
CurrentUser = CurrentIdentityContext

async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentIdentityContext:
    """Dependency to retrieve the current user from JWT token based on AUTH_MODE."""
    if settings.AUTH_MODE == "aaramidentity":
        payload = decode_aaramidentity_token(token)
    else:
        payload = decode_access_token(token)
        
    if not payload:
        raise UnauthorizedException(message="Invalid or expired token")
        
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException(message="Invalid token structure")

    applications = payload.get("applications", [])
    if "AARAM_BOOKS" not in applications and settings.AUTH_MODE == "aaramidentity":
        raise UnauthorizedException(message="User does not have access to AaramBooks application")

    return CurrentIdentityContext(
        user_id=user_id,
        name=payload.get("name", payload.get("username", "unknown")),
        applications=applications,
        roles=payload.get("roles", [payload.get("role")] if payload.get("role") else []),
        permissions=payload.get("permissions", [])
    )

class require_permission:
    """Dependency factory to enforce granular AaramIdentity permissions."""
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, user: CurrentIdentityContext = Depends(get_current_user)) -> CurrentIdentityContext:
        if settings.AUTH_MODE == "local":
            # For local dev migration phase, we might mock permissions or bypass
            # but strictly we should check even in local if they are provided.
            # If not provided, we fallback to bypass only if explicitly configured (though here we just enforce).
            pass

        if self.required_permission not in user.permissions:
            from src.foundation.exceptions.base import ForbiddenException
            raise ForbiddenException(message=f"Missing required permission: {self.required_permission}")
        return user


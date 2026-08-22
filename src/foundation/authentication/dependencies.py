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
    import traceback
    with open("/tmp/aaram_auth_debug.log", "a") as f:
        f.write(f"Active AUTH_MODE is: {settings.AUTH_MODE}\n")

    # Hard-force identity decoding to bypass CWD-related configuration load failures
    payload = decode_aaramidentity_token(token)
        
    with open("/tmp/aaram_auth_debug.log", "a") as f:
        f.write(f"Payload after decode: {payload}\n")
        
    if not payload:
        with open("/tmp/aaram_auth_debug.log", "a") as f:
            f.write("Payload is None. decode function failed.\n")
        raise UnauthorizedException(message="Invalid or expired token")
        
    user_id: str = str(payload.get("sub"))
    if user_id is None or user_id == "None":
        with open("/tmp/aaram_auth_debug.log", "a") as f:
            f.write("user_id (sub) is missing from payload.\n")
        raise UnauthorizedException(message="Invalid token structure")
        
    import uuid
    try:
        uuid.UUID(user_id)
    except ValueError:
        user_id = str(uuid.uuid5(uuid.NAMESPACE_OID, f"user_{user_id}"))

    # In a real system, you might want to fetch the user from DB here
    # For now, we trust the JWT claims
    
    applications = payload.get("applications", [])
    roles = payload.get("roles", [payload.get("role")] if payload.get("role") else [])
    
    has_app = "AARAM_INVENTORY" in applications or "AARAM_BOOKS" in applications
    has_admin_role = "AARAM_BOOKS_ADMIN" in roles or "AARAM_INVENTORY_ADMIN" in roles
    
    if not has_app and not has_admin_role:
        with open("/tmp/aaram_auth_debug.log", "a") as f:
            f.write(f"Access denied. Found apps: {applications}, roles: {roles}\n")
        raise UnauthorizedException(message="User does not have access to AaramInventory application")

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


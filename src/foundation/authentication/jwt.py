from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from typing import Optional, Dict, Any
from src.foundation.configuration import get_settings

settings = get_settings()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Legacy local HS256 decode."""
    try:
        decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded_data
    except JWTError:
        return None

def decode_aaramidentity_token(token: str) -> Optional[Dict[str, Any]]:
    """Validate RS256 token using AaramIdentity public key."""
    try:
        if not settings.AARAMIDENTITY_PUBLIC_KEY:
            # Fallback or error if not configured
            raise ValueError("AARAMIDENTITY_PUBLIC_KEY is not configured")
        # Format the public key properly if it's missing the PEM header
        public_key = settings.AARAMIDENTITY_PUBLIC_KEY
        if "-----BEGIN PUBLIC KEY-----" not in public_key:
            public_key = f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"
            
        decoded_data = jwt.decode(token, public_key, algorithms=["RS256"], audience="AARAM_ECOSYSTEM")
        return decoded_data
    except (JWTError, ValueError) as e:
        # Log error in real implementation
        return None

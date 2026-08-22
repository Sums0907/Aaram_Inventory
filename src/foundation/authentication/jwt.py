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

_cached_public_key: Optional[str] = None

def _fetch_public_key() -> str:
    if settings.AARAMIDENTITY_PUBLIC_KEY:
        # In case the key is passed via inline env var without proper newlines
        return settings.AARAMIDENTITY_PUBLIC_KEY.replace("\\n", "\n")
        
    import httpx
    url = f"{settings.IDENTITY_SERVICE_URL}/auth/public-key"
    try:
        r = httpx.get(url, timeout=10.0)
        r.raise_for_status()
        data = r.json()
        return data["public_key"]
    except Exception as e:
        raise RuntimeError(f"Failed to fetch Identity public key from {url}: {e}")

def decode_aaramidentity_token(token: str) -> Optional[Dict[str, Any]]:
    """Validate RS256 token using AaramIdentity public key."""
    global _cached_public_key
    if not _cached_public_key:
        _cached_public_key = _fetch_public_key()
        
    try:
        decoded_data = jwt.decode(
            token, 
            _cached_public_key, 
            algorithms=["RS256"], 
            audience="AARAM_ECOSYSTEM"
        )
    except jwt.ExpiredSignatureError:
        return None
    except JWTError:
        # Error-Triggered Cache Invalidation
        _cached_public_key = _fetch_public_key()
        try:
            decoded_data = jwt.decode(
                token, 
                _cached_public_key, 
                algorithms=["RS256"], 
                audience="AARAM_ECOSYSTEM"
            )
        except JWTError:
            return None
    except Exception as e:
        with open("/tmp/aaram_auth_debug.log", "a") as f:
            f.write(f"JWT Decode Exception: {type(e).__name__}: {str(e)}\n")
        return None
        
    with open("/tmp/aaram_auth_debug.log", "a") as f:
        f.write(f"JWT Decode Success: {decoded_data}\n")
        
    return decoded_data

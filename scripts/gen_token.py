import jwt
import uuid

# Using same secret as backend: src/foundation/configuration.py -> settings.JWT_SECRET (default="your-secret-key-for-development-only")
secret = "your-secret-key-for-development-only"
payload = {
    "sub": str(uuid.uuid4()),
    "username": "demo",
    "role": "admin",
    "exp": 1817472606
}
token = jwt.encode(payload, secret, algorithm="HS256")
print(token)

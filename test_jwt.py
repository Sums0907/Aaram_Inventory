import sys
import uuid
from datetime import datetime, timedelta, timezone
from jose import jwt

sys.path.insert(0, '/Users/sumatidhingra/Documents/AaramBooks/Aaram_Inventory')
from src.foundation.configuration import get_settings
settings = get_settings()

try:
    with open('/Users/sumatidhingra/Documents/AaramBooks/AaramIdentity/backend/private.pem', 'r') as f:
        private_key = f.read()

    to_encode = {
        "sub": "test_user_id",
        "roles": ["OWNER"],
        "applications": ["AARAM_BOOKS"],
        "permissions": ["PRODUCT_VIEW"],
        "name": "Test User",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15)
    }

    # encode using RS256
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm="RS256")
    print(f"Encoded JWT: {encoded_jwt[:20]}...")

    # decode using decode_aaramidentity_token
    from src.foundation.authentication.jwt import decode_aaramidentity_token
    
    decoded = decode_aaramidentity_token(encoded_jwt)
    if decoded:
        print("Decode successful!")
        print(decoded)
    else:
        print("Decode failed!")
except Exception as e:
    import traceback
    traceback.print_exc()


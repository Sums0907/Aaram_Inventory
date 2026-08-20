import sys
from datetime import datetime, timedelta, timezone
from jose import jwt

try:
    with open('/Users/sumatidhingra/Documents/AaramBooks/AaramIdentity/backend/private.pem', 'r') as f:
        private_key = f.read()

    to_encode = {
        "sub": "test_user_id",
        "aud": "AARAM_ECOSYSTEM",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15)
    }

    # encode using RS256
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm="RS256")
    
    with open('/Users/sumatidhingra/Documents/AaramBooks/AaramIdentity/backend/public.pem', 'r') as f:
        public_key = f.read()

    # decode without audience parameter
    try:
        decoded = jwt.decode(encoded_jwt, public_key, algorithms=["RS256"])
        print("Decode successful without audience!")
    except Exception as e:
        print(f"Decode failed without audience: {type(e).__name__}: {e}")

    # decode with audience parameter
    try:
        decoded = jwt.decode(encoded_jwt, public_key, algorithms=["RS256"], audience="AARAM_ECOSYSTEM")
        print("Decode successful with audience!")
    except Exception as e:
        print(f"Decode failed with audience: {type(e).__name__}: {e}")

except Exception as e:
    print(f"Error: {e}")


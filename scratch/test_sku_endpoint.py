import asyncio
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

def test_endpoint():
    # Attempt to call the new endpoint, even without auth it should return 401 or a result
    response = client.get("/api/v1/masters/skus/by-product-name/test")
    print("Status code:", response.status_code)
    print("Response:", response.json())

if __name__ == "__main__":
    test_endpoint()

import requests

payload = {
  "grn_number": "TEST-001",
  "supplier_id": "00000000-0000-0000-0000-000000000000",
  "warehouse_id": "00000000-0000-0000-0000-000000000000",
  "receipt_date": "2026-08-11",
  "receipt_type": "RAW_MATERIAL_RECEIPT",
  "items": [
    {
      "sku_id": "00000000-0000-0000-0000-000000000000",
      "quantity": 10
    }
  ]
}

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MDJlYWMxMS0yMWUyLTRkNTMtYTllOS0yYmEyMWJjMDRiOWEiLCJ1c2VybmFtZSI6ImRlbW8iLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE4MTc0NzI2MDZ9._cuQTw-7zam00atnpTsxsklre2ZsOFVKPkbvChQpSMM",
    "Content-Type": "application/json"
}

res = requests.post("http://localhost:8000/api/v1/inventory/goods-receipts", json=payload, headers=headers)
print("Status:", res.status_code)
print("Body:", res.text)

import requests

response = requests.get("http://localhost:8000/api/v1/masters/units-of-measure")
if response.status_code == 200:
    data = response.json()
    uoms = data.get("data", [])
    print(f"Found {len(uoms)} UOMs")
    for u in uoms:
        print(f" - {u.get('unit_name')} : {u.get('status')}")
else:
    print(f"Failed to fetch UOMs: {response.status_code} {response.text}")


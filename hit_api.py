import urllib.request
import urllib.error

url = "http://127.0.0.1:8100/api/v1/skus"
print(f"Hitting {url} ...")
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=2) as response:
        print("Status:", response.status)
        print("Body:", response.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Body:", e.read().decode())
except Exception as e:
    print("Exception:", e)

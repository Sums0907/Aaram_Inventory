import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

html = urllib.request.urlopen("https://inventory.aarambooks.cloud", context=ctx).read().decode('utf-8')
js_match = re.search(r'src="(/assets/index-.*?\.js)"', html)
if not js_match:
    print("Could not find js file")
    exit(1)
js_file = js_match.group(1)
js_content = urllib.request.urlopen("https://inventory.aarambooks.cloud" + js_file, context=ctx).read().decode('utf-8')
if "localhost:9001" in js_content:
    print("YES - Old code is still running on the server!")
else:
    print("NO - New code is deployed, something else is wrong.")

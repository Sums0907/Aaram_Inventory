import re

with open("/Users/sumatidhingra/AaramDevLauncher/start_all.sh", "r") as f:
    content = f.read()

injection = """
if [ ! -d "/Users/sumatidhingra/Documents/AaramBooks/Aaram_Inventory/frontend" ]; then
    echo "ERROR: Inventory frontend folder not found!"
    exit 1
fi

# Inventory frontend config is generated automatically.
# Do not manually edit config.js.
# Ports are controlled only from start_all.sh.
cat << CONFIG > /Users/sumatidhingra/Documents/AaramBooks/Aaram_Inventory/frontend/config.js
window.AARAM_CONFIG = {
    API_URL: "http://127.0.0.1:${INVENTORY_BACKEND_PORT}/api/v1"
};
CONFIG
"""

target = "echo \"Starting Inventory Frontend...\""

if injection not in content:
    content = content.replace(target, injection + "\n\n" + target)

with open("/Users/sumatidhingra/AaramDevLauncher/start_all.sh", "w") as f:
    f.write(content)

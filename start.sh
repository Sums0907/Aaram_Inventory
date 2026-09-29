#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
LOG_DIR="${AARAM_LOG_DIR:-$HOME/AaramDevLauncher}"; mkdir -p "$LOG_DIR"

set -a; source .env; set +a
export PYTHONPATH=.

INVENTORY_BACKEND_PORT="${INVENTORY_BACKEND_PORT:-8100}"
INVENTORY_FRONTEND_PORT="${INVENTORY_FRONTEND_PORT:-5173}"

lsof -ti:"$INVENTORY_BACKEND_PORT" | xargs kill -9 2>/dev/null || true
lsof -ti:"$INVENTORY_FRONTEND_PORT" | xargs kill -9 2>/dev/null || true

venv/bin/uvicorn src.app.main:app --reload --host 0.0.0.0 --port "$INVENTORY_BACKEND_PORT" > "$LOG_DIR/inventory_backend.log" 2>&1 &

cat > "$SCRIPT_DIR/frontend/public/config.js" <<EOF
const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
window.AARAM_CONFIG = {
    API_URL: isLocalhost ? "http://127.0.0.1:${INVENTORY_BACKEND_PORT}" : "https://api-inventory.aarambooks.cloud",
    IDENTITY_URL: "${IDENTITY_FRONTEND_URL:-https://identity.aarambooks.cloud}",
    IDENTITY_API_URL: "${IDENTITY_API_URL:-https://api-identity.aarambooks.cloud}"
};
EOF

cd "$SCRIPT_DIR/frontend"
nohup ./node_modules/.bin/vite --host 0.0.0.0 --port "$INVENTORY_FRONTEND_PORT" > "$LOG_DIR/inventory_frontend.log" 2>&1 &

disown -a 2>/dev/null || true
echo "Inventory started: http://127.0.0.1:${INVENTORY_BACKEND_PORT}"

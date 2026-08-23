#!/bin/bash
export AUTH_MODE=local
# Start server in background
venv/bin/python -m uvicorn src.app.main:app --host 127.0.0.1 --port 8123 > scratch/server.log 2>&1 &
SERVER_PID=$!
sleep 3

# Send request
curl -s -X POST http://127.0.0.1:8123/api/v1/categories \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer mock_token_because_auth_mode_is_local_maybe" \
  -d '{"category_name": "Test1", "item_type": "FINISHED_GOODS", "attributes": []}' > scratch/response.json

# Kill server
kill $SERVER_PID
cat scratch/response.json

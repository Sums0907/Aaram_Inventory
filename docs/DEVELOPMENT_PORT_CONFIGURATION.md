# Development Port Configuration

## Architecture Overview
The Aaram development stack (comprising multiple frontends and backends) manages its ports and API URLs centrally to prevent drift and configuration chaos.

**The single source of truth for ports is:**
`/Users/sumatidhingra/AaramDevLauncher/start_all.sh`

## Runtime Configuration Injection
The frontends do not hardcode backend API URLs in their source code or `.env` files. 
Instead, they consume a runtime-generated configuration file (`config.js`) injected by the `start_all.sh` launcher.

### How it works:
1. `start_all.sh` defines ports like `INVENTORY_BACKEND_PORT=8100`.
2. Before launching the Inventory frontend, the script generates `frontend/config.js` with:
```javascript
window.AARAM_CONFIG = {
    API_URL: "http://127.0.0.1:8100/api/v1"
};
```
3. The frontend's `index.html` loads this `config.js` before the main application code.
4. The API client uses `window.AARAM_CONFIG?.API_URL` to route requests.

## Developer Guidelines
- **NEVER** edit `config.js` manually. It is overwritten every time the stack starts.
- **NEVER** hardcode `localhost`, `127.0.0.1`, or port numbers in the frontend source files (e.g., in axios/fetch clients).
- To change the backend port, simply modify the `INVENTORY_BACKEND_PORT` variable in `/Users/sumatidhingra/AaramDevLauncher/start_all.sh` and restart the stack. The frontend will automatically adapt.

# AaramBooks Ecosystem Deployment Journey & Lessons Learned

This document serves as a comprehensive "Brain Dump" of the AaramIdentity deployment process. It captures not just the final state, but the errors faced, the architectural pivots, and the critical gotchas that future AIs and developers MUST know before deploying AaramInventory or AaramPacking.

## 1. The Database Pivot: SQLite to Bare-Metal PostgreSQL
**Initial State**: The application was initially using a file-based SQLite database (`identity.db`) inside a Docker container.
**The Problem**: Docker containers are ephemeral. Restarting or updating the container wiped the database. Furthermore, SQLite cannot handle concurrent writes effectively at an enterprise scale.
**The Solution**: We abandoned SQLite and installed a **bare-metal PostgreSQL 16** instance directly on the Hostinger VPS host OS. We ran a custom Python migration script (`run_migration.py`) to extract the SQLite data and inject it into the new `identity_prod` PostgreSQL database.

**CRITICAL GOTCHA FOR FUTURE DEPLOYMENTS**:
- **Do NOT** put the primary database inside a Docker container unless using highly managed external volumes. The host-installed PostgreSQL is now the central source of truth for the ecosystem.
- New services (Inventory, Packing) should create their own databases (e.g., `inventory_prod`) inside this same bare-metal PostgreSQL instance.

## 2. Docker-to-Host Database Connectivity (The `pg_hba.conf` Trap)
**The Problem**: Once PostgreSQL was on the host, the Docker containers couldn't connect to it. `localhost` inside a Docker container points to the container itself, not the host.
**The Solution**: 
1. We had to point the `.env` database URLs to the actual VPS Host IP or Docker Gateway IP, NOT `localhost`.
2. We had to modify `/etc/postgresql/16/main/postgresql.conf` to `listen_addresses = '*'`
3. We had to modify `/etc/postgresql/16/main/pg_hba.conf` to explicitly trust connections coming from the Docker subnet (e.g., `172.17.0.0/12` and `192.168.0.0/16`).

**CRITICAL GOTCHA FOR FUTURE DEPLOYMENTS**:
- If `AaramInventory` cannot connect to the database, **do not change the code**. Check the Docker bridge network IP and ensure `pg_hba.conf` trusts that subnet.

## 3. The Domain Migration & SSL (The Certbot Failure)
**Initial State**: We attempted to provision SSL certificates for `identity.aarambooks.com`.
**The Problem**: Certbot threw DNS `NXDOMAIN` errors because the `.com` domain was unavailable or improperly propagated.
**The Solution**: We abandoned `.com` and claimed `aarambooks.cloud`. We wrote an aggressive bash script (`update_nginx_domain.sh`) to tear down the `.com` Nginx configs, generate new `.cloud` configs, and successfully provision Let's Encrypt SSL certificates.

**CRITICAL GOTCHA FOR FUTURE DEPLOYMENTS**:
- The production ecosystem lives on `.aarambooks.cloud`.
- When exposing the AaramInventory frontend/API, you must create new Nginx server blocks (e.g., `inventory.aarambooks.cloud`) and use `certbot --nginx` to secure them. 
- **Do not** expose Docker ports directly to the internet. Always route through Nginx.

## 4. Frontend API Routing (The Hardcoded Localhost Bug)
**The Problem**: The React/Next.js frontend was trying to make API calls to `http://localhost:8000` from the user's browser, which failed in production.
**The Solution**: We had to inject the production API URL dynamically. We used a `sed` command during deployment to replace the local API URL in `config.js` with `https://api-identity.aarambooks.cloud`.

**CRITICAL GOTCHA FOR FUTURE DEPLOYMENTS**:
- Ensure the frontend for Inventory/Packing is configured to hit the public `https://api...` endpoint, not a local Docker network name or localhost.

## 5. The 50GB VPS Storage Constraint
**The Problem**: The Hostinger VPS has a hard 50GB NVMe limit. Unchecked Docker logs, dangling images, or infinite backup archives would crash the server within months.
**The Solution**:
1. **Docker Logs**: Verified `/etc/docker/daemon.json` limits logs to 10MB (`max-size: 10m`).
2. **Backups**: Created an asset-type hierarchy (`postgres/`, `secrets/`, `deployment/`, `nginx/`) with a strict retention script that forces deletion of backups older than 7 days (and 4 weeks for weeklies).
3. **Compression**: Used `pg_dump | gzip` which shrank the ecosystem backup to under 100KB.

**CRITICAL GOTCHA FOR FUTURE DEPLOYMENTS**:
- Before pulling large Docker images or installing heavy dependencies, ALWAYS check disk space using `df -h`. 
- When building `AaramInventory`, rely on GHCR (GitHub Container Registry) for pre-built images rather than building heavy images directly on the VPS. 
- Use the `disk_monitor.sh` script to verify space.

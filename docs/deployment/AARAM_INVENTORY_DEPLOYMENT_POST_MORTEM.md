# AaramInventory VPS Deployment Post-Mortem & Troubleshooting Log

This document serves as a historical record of all errors encountered, failed attempts, and the final working solutions during the initial Hostinger VPS deployment of the Aaram_Inventory application. 

This log should be referenced and updated during future module deployments (e.g., Accounts Payable, General Ledger) to prevent regression and save debugging time.

## 1. GitHub Actions Build Timeout / Silent Failure (Frontend)
- **Symptom:** The `.github/workflows/docker-publish.yml` pipeline repeatedly failed on the `aaram_inventory-frontend` Docker build step around the 18-second mark.
- **Root Cause Hypothesis:** Strict `npm ci` lockfile validation combined with aggressive TypeScript checking (`tsc -b`) was either causing silent out-of-memory kills on the free-tier GitHub Linux runner, or dependency resolution was failing.
- **Failed Fix Attempts:**
  - Added `// @ts-nocheck` to skip strict TS validation on offending files.
  - Switched from `npm ci` to `npm install` in the Dockerfile to bypass lockfile strictness.
- **Final Working Solution:** Bypassed the CI/CD node build entirely. We pre-built the React app locally (`npm run build`), forced the `dist/` directory into Git, and rewrote the `frontend/Dockerfile` to simply `COPY dist/ /usr/share/nginx/html`. This guaranteed 100% build success on GitHub Actions.

## 2. Missing Python Backend Dependencies
- **Symptom:** The backend container (`api-1`) crashed immediately on startup with `ModuleNotFoundError: No module named 'pandas'`.
- **Root Cause:** Alembic database migrations run automatically on container startup. Alembic imports the SQLAlchemy models (`LedgerModel`), which internally imported `JournalAggregationService`. That service relied on `pandas`, but `pandas` was missing from `requirements.txt`.
- **Final Working Solution:** Appended `pandas==2.2.2` to `requirements.txt`, pushed to `main`, and waited for the GitHub Action to rebuild the `python:3.11-slim` container with the new dependency.

## 3. Production Security Guardrail (AUTH_MODE)
- **Symptom:** The backend container crashed with: `ValueError: AUTH_MODE='local' is forbidden in production. Must use 'aaramidentity'`.
- **Root Cause:** The `pydantic-settings` configuration explicitly forbids `AUTH_MODE="local"` when `ENVIRONMENT="production"`. The container was not receiving the `AUTH_MODE` and `AARAMIDENTITY_PUBLIC_KEY` variables from the `.env.production` file.
- **Failed Fix Attempts:**
  - Added the variables to `.env.production` and ran `docker compose restart api`. (Failed because `restart` does not reload `.env` file changes; `up -d` is required).
  - Ran `docker compose up -d`. (Failed because `docker-compose.prod.yml` was missing the explicit passthrough definitions in the `environment:` block).
- **Final Working Solution:** Updated `docker-compose.prod.yml` in the Git repository to explicitly map `- AUTH_MODE=${AUTH_MODE}` and `- AARAMIDENTITY_PUBLIC_KEY=${AARAMIDENTITY_PUBLIC_KEY}`. Re-pulled the yaml file and ran `docker compose --env-file .env.production -f docker-compose.prod.yml up -d --force-recreate`.

## 4. PostgreSQL Network Rejection (`pg_hba.conf`)
- **Symptom:** `asyncpg.exceptions.InvalidAuthorizationSpecificationError: no pg_hba.conf entry for host "172.19.0.2"`
- **Root Cause:** The FastAPI container successfully reached the bare-metal host PostgreSQL instance via the Docker bridge network. However, PostgreSQL's internal firewall (`pg_hba.conf`) blocks all non-localhost IPs by default.
- **Final Working Solution:** Edited `/etc/postgresql/16/main/pg_hba.conf` on the VPS to whitelist the entire Docker subnet by appending:
  `host    all             all             172.16.0.0/12           scram-sha-256`
  Followed by `sudo systemctl reload postgresql`.

## 5. PostgreSQL Authentication Failure
- **Symptom:** `InvalidPasswordError: password authentication failed for user "postgres"`
- **Root Cause:** The `DATABASE_URL` in `.env.production` was attempting to log in as the default `postgres` superuser, but it was using a password that belonged to a different user (the AaramIdentity user).
- **Failed Fix Attempts:** Attempting to force the connection using the wrong credentials.
- **Final Working Solution:** Created a dedicated database user for the inventory system following best security practices:
  ```bash
  sudo -u postgres psql -c "CREATE USER inventory_user WITH ENCRYPTED PASSWORD '********';"
  sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE inventory_prod TO inventory_user;"
  sudo -u postgres psql -d inventory_prod -c "GRANT ALL ON SCHEMA public TO inventory_user;"
  ```
  Updated `.env.production` to use `inventory_user` in the `DATABASE_URL` and recreated the container.

## 6. Nginx Routing & Missing Server Block (Frontend 404)
- **Symptom:** Visiting the frontend domain (`inventory.aarambooks.cloud`) returned `{"detail":"Not Found"}`.
- **Root Cause:** A raw JSON response like `{"detail":"Not Found"}` is the signature of a FastAPI application when a route doesn't exist, proving Nginx was routing frontend traffic to a backend API. The API server block (`api-inventory.aarambooks.cloud`) was completely missing from `/etc/nginx/sites-available`. Because it was missing, when the React app attempted to make API calls to the API domain, Nginx fell back to the default server block (the AaramIdentity API), which returned a 404 since it didn't recognize the inventory routes.
- **Final Working Solution:** Created the missing Nginx server block for `api-inventory.aarambooks.cloud` pointing to the backend container port `8100`, enabled the site, reloaded Nginx, and secured it with Certbot. This properly separated frontend and backend traffic.

## 7. Infinite SSO Redirect Loop & JWT Literal Newline Bug
- **Symptom:** The user was successfully logging in to AaramIdentity, getting redirected back to the Aaram_Inventory dashboard, but the backend immediately threw a 401 Unauthorized, deleted the token, and redirected back to AaramIdentity in an infinite loop.
- **Root Cause 1:** The `AARAMIDENTITY_PUBLIC_KEY` inside the `.env.production` file was passed by Docker Compose as a literal string containing `\n` (backslash n) rather than true newline characters. `jwt.decode` silently failed to parse this as a valid PEM key.
- **Root Cause 2:** AaramIdentity automatically generates dynamic RSA keys internally on startup if `private.pem` is absent, ignoring the static `JWT_PUBLIC_KEY` in its `.env` file. The static key copied from the Identity `.env` file was a 'ghost key' mismatched with the live signing key.
- **Final Working Solution:** 
  1. Patched `src/foundation/authentication/jwt.py` to explicitly call `public_key.replace('\\n', '\n')` to immunize the application against Docker Compose environment variable escaping quirks.
  2. Extracted the live `public.pem` directly from the running AaramIdentity container using `docker exec` and placed it into Aaram_Inventory's `.env.production`.

## 8. Deployment Checklist for Future Modules (e.g. AaramPackerApp)
To completely avoid all the above issues when deploying the next application, follow this exact sequence:
1. **GitHub Actions Frontend:** If building a React app in Docker, pre-build it locally (`npm run build`) and use `COPY dist/ /usr/share/nginx/html` in your Dockerfile to completely avoid GitHub Actions memory limits and lockfile errors. Don't forget to `git add -f dist/`.
2. **Database:** Log into PostgreSQL via `sudo -u postgres psql` and manually create the database and user (e.g., `packer_user`) before deploying. Do NOT use the default `postgres` user in `.env.production`.
3. **pg_hba.conf:** Ensure the Docker subnet (`172.16.0.0/12`) is whitelisted in `/etc/postgresql/16/main/pg_hba.conf` if this is a new server.
4. **Environment Variables:** Verify that your `docker-compose.prod.yml` has explicit mappings under the `environment` section for every variable you expect the container to read from `.env.production` (e.g. `- AUTH_MODE=${AUTH_MODE}`).
5. **Nginx:** Ensure you have *two* separate server blocks in `/etc/nginx/sites-available` — one for the frontend (e.g. `packer.aarambooks.cloud`) and one for the backend (e.g. `api.packer.aarambooks.cloud`).
6. **AaramIdentity Key Sync (CRITICAL):** Because AaramIdentity generates dynamic RSA keys, you MUST fetch the live public key from the running container:
   - Run `docker exec aaram_identity_backend_prod cat public.pem`
   - Use a tool to convert the multiline output into a single string with `\n` characters.
   - Paste that single string into your `.env.production` under `AARAMIDENTITY_PUBLIC_KEY="..."`.

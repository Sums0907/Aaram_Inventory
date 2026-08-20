# AaramPackerApp Deployment Handoff & Instructions

**Goal:** Deploy `AaramPackerApp` to the Hostinger VPS production environment, integrated with `AaramIdentity` for SSO and using PostgreSQL.

## Critical Context from Previous Deployments
We just successfully deployed the Inventory module and discovered several severe architectural traps. To ensure the Packer deployment is seamless, you must follow the `AARAM_INVENTORY_DEPLOYMENT_POST_MORTEM.md` playbook strictly. 

## Immediate Tasks for Packer Deployment

1. **Frontend CI/CD Bypass:** Do not attempt to build the Vite/React frontend using Docker on GitHub Actions (it will silently timeout/fail). You must pre-build the frontend locally (`npm run build`), force-add `dist/` to git (`git add -f frontend/dist`), and update the frontend Dockerfile to simply `COPY dist/ /usr/share/nginx/html`.
2. **Database Preparation:** SSH into the VPS and manually create a dedicated database and user (`packer_user` / `packer_prod`) via `sudo -u postgres psql`. Do not use the default `postgres` superuser. (The Docker subnet `172.16.0.0/12` is already whitelisted in `pg_hba.conf`).
3. **Nginx Separation:** Ensure there are two distinct server blocks on the VPS (e.g., `packer.aarambooks.cloud` for port 3200 and `api.packer.aarambooks.cloud` for port 8200) to prevent routing 404s.
4. **Environment Variables:** Double-check `docker-compose.prod.yml` to ensure every variable (like `DATABASE_URL`, `AUTH_MODE`, and `AARAMIDENTITY_PUBLIC_KEY`) is explicitly mapped in the `environment` block, otherwise they will be silently dropped.
5. **The JWT "Ghost Key" Bug (CRITICAL):** AaramIdentity dynamically generates its RSA keys on the VPS. Do not use the static public key from the infrastructure secrets folder. You MUST run `docker exec aaram_identity_backend_prod cat public.pem` on the VPS to extract the live key. Furthermore, you must ensure Packer's `jwt.py` explicitly unescapes literal newlines (`public_key.replace('\\n', '\n')`) because Docker Compose mangles multiline `.env` variables.

## Next Step
Begin preparing the Packer repository's `docker-compose.prod.yml`, `Dockerfile`s, and `.env.production` file using the rules above.

#!/bin/bash
set -e

# ── Output styling ──────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

section() { printf "\n${BOLD}${CYAN}════════════════════════════════════════════════════════${NC}\n${BOLD}${CYAN}  %s${NC}\n${BOLD}${CYAN}════════════════════════════════════════════════════════${NC}\n" "$1"; }
step()    { printf "\n${BOLD}▶ %s${NC}\n" "$1"; }
ok()      { printf "${GREEN}✅ %s${NC}\n" "$1"; }
warn()    { printf "${YELLOW}⚠️  %s${NC}\n" "$1"; }
fail()    { printf "${RED}❌ %s${NC}\n" "$1" >&2; }
info()    { printf "${DIM}   %s${NC}\n" "$1"; }

trap 'fail "Deployment failed at line $LINENO — stopped there, nothing after it ran."' ERR

APP_FOLDER="inventory"
VPS_USER="aaramhomes"
VPS_IP="200.234.39.72"

section "Starting Full Deployment Pipeline — Inventory"

step "[1/3] Committing and pushing code to GitHub"
if [ -n "$1" ]; then
    COMMIT_MSG="$1"
    info "Commit message: $COMMIT_MSG"
else
    read -p "Enter commit message: " COMMIT_MSG
fi
git add .
git commit -m "$COMMIT_MSG" || warn "No new changes to commit."
git push origin main || warn "No new changes to push."

info "GitHub Actions is now building your Docker image in the cloud."
info "🕒 Giving GitHub a few seconds to trigger the Action..."
sleep 5

section "Tracking Live Build Progress"
RUN_ID=$(gh run list --limit 1 --json databaseId -q ".[0].databaseId")

if [ -z "$RUN_ID" ]; then
    warn "Could not automatically detect the GitHub Action."
    read -p "Please wait 3 minutes, then press Enter to trigger the VPS pull... "
else
    if gh run watch $RUN_ID --exit-status; then
        ok "GitHub Action completed successfully!"
    else
        fail "GitHub Action failed — the VPS will NOT be touched."
        exit 1
    fi
fi

step "[3/3] Connecting to VPS to pull and restart"
# This sends the deployment commands directly to your VPS over SSH!
ssh $VPS_USER@$VPS_IP << EOF
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    BOLD='\033[1m'
    NC='\033[0m'
    # Without set -e + this trap, a failed cd/pull/up on the remote side just
    # prints an error and falls through to the final echo, which always
    # succeeds — meaning this whole SSH block reports success back to the
    # local script no matter what actually happened on the VPS.
    trap 'printf "\${RED}❌ VPS deploy failed at line \$LINENO — stopped there, nothing after it ran.\${NC}\n" >&2' ERR
    set -e
    cd ~/aarambooks/$APP_FOLDER

    printf "\${BOLD}Pulling latest images...\${NC}\n"
    docker compose -f docker-compose.prod.yml pull

    printf "\${BOLD}Restarting containers...\${NC}\n"
    docker compose -f docker-compose.prod.yml up -d

    # Run migrations if it's the backend
    BACKEND_CONTAINER=\$(docker compose -f docker-compose.prod.yml ps -q | xargs -r docker inspect -f '{{.Name}}' | grep "backend" | sed 's/^\///' || true)
    if [ -n "\$BACKEND_CONTAINER" ]; then
        printf "\${BOLD}Running Alembic migrations...\${NC}\n"
        docker exec "\$BACKEND_CONTAINER" alembic upgrade head || true
    fi

    printf "\${BOLD}Cleaning up...\${NC}\n"
    docker image prune -f

    printf "\n\${BOLD}Verifying containers actually restarted just now:\${NC}\n"
    docker compose -f docker-compose.prod.yml ps --format '{{.Name}}\t{{.RunningFor}}'

    printf "\${GREEN}✅ VPS Deployment Complete!\${NC}\n"
EOF

section "All Done! Your app is live."

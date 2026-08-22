#!/bin/bash
set -e

# Change this to whichever app you are deploying (packing, inventory, identity)
APP_FOLDER="inventory"
VPS_USER="aaramhomes"
VPS_IP="200.234.39.72"

echo "========================================="
echo " Starting Full Deployment Pipeline"
echo "========================================="

# Step 1: Push to GitHub
echo ""
echo "[1/3] Committing and pushing code to GitHub..."
read -p "Enter commit message: " COMMIT_MSG
git add .
git commit -m "$COMMIT_MSG"
git push origin main

# Step 2: Wait for GitHub Actions
echo ""
echo "[2/3] Code pushed successfully!"
echo "GitHub Actions is now building your Docker image in the cloud.\n"
echo "⚠️  You usually need to wait 2-3 minutes for the build to finish.\n"
read -p "Press Enter when you are sure the GitHub Action is complete...\n==============================================\n"

# Step 3: Trigger VPS Update
echo ""
echo "[3/3] Connecting to VPS to pull and restart..."
# This sends the deployment commands directly to your VPS over SSH!
ssh $VPS_USER@$VPS_IP << EOF
    cd ~/aarambooks/$APP_FOLDER
    
    echo "Pulling latest images..."
    docker-compose -f docker-compose.prod.yml pull
    
    echo "Restarting containers..."
    docker-compose -f docker-compose.prod.yml up -d
    
    # Run migrations if it's the backend
    BACKEND_CONTAINER=\$(docker-compose -f docker-compose.prod.yml ps -q | xargs docker inspect -f '{{.Name}}' | grep "backend" | sed 's/^\///' || true)
    if [ -n "\$BACKEND_CONTAINER" ]; then
        echo "Running Alembic migrations..."
        docker exec "\$BACKEND_CONTAINER" alembic upgrade head || true
    fi
    
    echo "Cleaning up..."
    docker image prune -f
    
    echo "✅ VPS Deployment Complete!"
EOF

echo ""
echo "========================================="
echo " All Done! Your app is live."
echo "========================================="

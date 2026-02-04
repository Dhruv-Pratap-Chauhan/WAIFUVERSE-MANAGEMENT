#!/bin/bash

# Configuration
VPS_IP="15.235.193.186"
VPS_USER="ubuntu"
VPS_PATH="/home/$VPS_USER/waifu_mgmt"
SERVICE_NAME="waifu-mgmt"

echo "🚀 Deploying WaifuVerse Management Bot to VPS ($VPS_IP)..."

# Files to transfer
FILES=(
    "MukeshRobot"
    "requirements.txt"
    "start.sh"
    "waifu-mgmt.service"
)

# Check if requirements changed (Calculate remote hash BEFORE sync)
echo "🔍 Checking for dependency changes..."
REMOTE_HASH=$(ssh "$VPS_USER@$VPS_IP" "cd $VPS_PATH && md5sum requirements.txt 2>/dev/null || echo 'new'" | awk '{print $1}')
LOCAL_HASH=$(md5sum requirements.txt | awk '{print $1}')

# Transfer files
echo "📦 Transferring codebase..."
ssh "$VPS_USER@$VPS_IP" "mkdir -p $VPS_PATH"
# Rsync files
rsync -az --delete --relative "${FILES[@]}" "$VPS_USER@$VPS_IP:$VPS_PATH/"
if [ $? -ne 0 ]; then echo "❌ Transfer failed"; exit 1; fi

# VPS .env Management
echo "⚙️  Syncing .env file..."
# Note: Usually better to manage .env manually on server, but syncing for now as requested
rsync -az ".env" "$VPS_USER@$VPS_IP:$VPS_PATH/.env"
echo "✅ .env synced successfully"

# Ensure dependencies are installed
echo "🐍 Ensuring system packages..."
ssh "$VPS_USER@$VPS_IP" "sudo apt-get update -qq && sudo apt-get install -y -qq python3-venv libxml2-dev libxslt-dev python3-dev" 2>/dev/null

# Virtual Environment Setup
echo "🐍 Setting up Virtual Environment..."
VENV_EXISTS=$(ssh "$VPS_USER@$VPS_IP" "[ -f '$VPS_PATH/venv/bin/activate' ] && echo 'yes' || echo 'no'")

INSTALL_DEPS="no"
if [ "$VENV_EXISTS" == "no" ]; then
    echo "📦 Creating new Virtual Environment..."
    ssh "$VPS_USER@$VPS_IP" "cd $VPS_PATH && rm -rf venv && python3 -m venv venv"
    INSTALL_DEPS="yes"
else
    if [ "$REMOTE_HASH" != "$LOCAL_HASH" ]; then
        echo "📦 Requirements changed..."
        INSTALL_DEPS="yes"
    else
        echo "✅ Venv exists, dependencies unchanged."
    fi
fi

if [ "$INSTALL_DEPS" == "yes" ]; then
    echo "📦 Installing Python dependencies strictly in venv..."
    ssh "$VPS_USER@$VPS_IP" "cd $VPS_PATH && ./venv/bin/pip install --upgrade pip && ./venv/bin/pip install lxml==5.3.0 psycopg2-binary && ./venv/bin/pip install -r requirements.txt"
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully within venv"
    else
        echo "⚠️  Dependency installation had warnings"
    fi
fi

# Configure Local DB Links in .env (Management Bot specific)
echo "🗄️  Configuring Local DBs..."
ssh "$VPS_USER@$VPS_IP" "sed -i 's|^MONGO_DB_URI=.*|MONGO_DB_URI=mongodb://localhost:27017/waifu_mgmt|' '$VPS_PATH/.env'"
ssh "$VPS_USER@$VPS_IP" "sed -i 's|^DATABASE_URL=.*|DATABASE_URL=postgresql://dhruv_user:dhruv_pass_123@localhost:5432/dhruv_bot_db|' '$VPS_PATH/.env'"

# Setup Systemd Service
echo "🔧 Configuring Systemd..."
ssh "$VPS_USER@$VPS_IP" "sudo mv $VPS_PATH/waifu-mgmt.service /etc/systemd/system/$SERVICE_NAME.service"
ssh "$VPS_USER@$VPS_IP" "sudo systemctl daemon-reload && sudo systemctl enable $SERVICE_NAME"

# Restart
echo "🔄 Restarting Service..."
ssh "$VPS_USER@$VPS_IP" "sudo systemctl restart $SERVICE_NAME"

# Verify
sleep 5
RUNNING=$(ssh "$VPS_USER@$VPS_IP" "systemctl is-active $SERVICE_NAME")

echo ""
if [ "$RUNNING" == "active" ]; then
    echo "✅ Deployment Successful! Bot is ACTIVE."
else
    echo "❌ Deployment completed but bot is NOT active. Status: $RUNNING"
    echo "   Check logs: ssh $VPS_USER@$VPS_IP 'sudo journalctl -u $SERVICE_NAME -f'"
fi
echo ""

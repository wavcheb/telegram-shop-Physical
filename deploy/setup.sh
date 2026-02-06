#!/bin/bash
# Setup script for Telegram Shop Bot on FastPanel server with MariaDB
# Run as root or with sudo

set -e

APP_DIR="/var/www/telegram-shop"
APP_USER="www-data"

echo "=== Telegram Shop Bot - Setup ==="

# 1. Install system dependencies
echo "[1/7] Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-venv python3-pip redis-server

# 2. Create application directory
echo "[2/7] Setting up application directory..."
mkdir -p "$APP_DIR"/{logs,data}
cp -r . "$APP_DIR/"
chown -R "$APP_USER":"$APP_USER" "$APP_DIR"

# 3. Create Python virtual environment
echo "[3/7] Creating Python virtual environment..."
cd "$APP_DIR"
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

# 4. Setup MariaDB database
echo "[4/7] Setting up MariaDB database..."
echo "Make sure MariaDB is installed (FastPanel provides it)."
echo "Run the following SQL commands in MariaDB as root:"
echo ""
echo "  CREATE DATABASE telegram_shop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo "  CREATE USER 'shop_user'@'localhost' IDENTIFIED BY 'YOUR_STRONG_PASSWORD';"
echo "  GRANT ALL PRIVILEGES ON telegram_shop.* TO 'shop_user'@'localhost';"
echo "  FLUSH PRIVILEGES;"
echo ""

# 5. Configure environment
echo "[5/7] Configuring environment..."
if [ ! -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    echo "Created .env from .env.example - EDIT IT with your actual values!"
else
    echo ".env already exists, skipping."
fi

# 6. Install systemd service
echo "[6/7] Installing systemd service..."
cp "$APP_DIR/deploy/telegram-shop-bot.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable telegram-shop-bot

# 7. Setup nginx monitoring proxy (optional)
echo "[7/7] Nginx monitoring config available at:"
echo "  $APP_DIR/deploy/nginx-monitoring.conf"
echo "  Copy it to /etc/nginx/conf.d/ and edit the server_name."

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit $APP_DIR/.env with your credentials"
echo "  2. Create the MariaDB database (see SQL commands above)"
echo "  3. Start the bot: sudo systemctl start telegram-shop-bot"
echo "  4. Check logs: sudo journalctl -u telegram-shop-bot -f"
echo "  5. (Optional) Setup nginx monitoring proxy"

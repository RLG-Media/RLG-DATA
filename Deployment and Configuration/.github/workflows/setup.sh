#!/bin/bash

# Exit on any error
set -e

echo "Starting setup for RLG Data and RLG Fans..."

# Function to log messages
log() {
    echo -e "\e[32m$1\e[0m"
}

# Update package lists and install dependencies
log "Updating package lists and installing dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv postgresql redis nginx docker.io docker-compose git curl build-essential

# Set environment variables
log "Setting up environment variables..."
export FLASK_ENV=production
export FLASK_APP=app.py
export DATABASE_URL="postgresql://rlg_user:secure_password@localhost:5432/rlg_data"
export FANS_DATABASE_URL="postgresql://rlg_user:secure_password@localhost:5432/rlg_fans_data"
export REDIS_URL="redis://localhost:6379/0"
export JWT_SECRET_KEY="your_jwt_secret_key"
export STRIPE_SECRET_KEY="your_stripe_secret_key"
export SENTRY_DSN="your_sentry_dsn"

# Backend setup for RLG DATA
log "Setting up backend for RLG Data..."
cd RLGDATA_backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
flask db upgrade
deactivate
cd ..

# Backend setup for RLG FANS
log "Setting up backend for RLG Fans..."
cd RLGFANS_backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
flask db upgrade
deactivate
cd ..

# Frontend setup
log "Setting up frontend..."
cd frontend
npm install
npm run build
cd ..

# Configure PostgreSQL
log "Configuring PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE rlg_data;"
sudo -u postgres psql -c "CREATE DATABASE rlg_fans_data;"
sudo -u postgres psql -c "CREATE USER rlg_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE rlg_data TO rlg_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE rlg_fans_data TO rlg_user;"

# Redis setup (ensure service is running)
log "Starting Redis service..."
sudo systemctl enable redis
sudo systemctl start redis

# Nginx setup
log "Setting up Nginx..."
sudo cp deployment_and_configuration/nginx.conf /etc/nginx/sites-available/rlg
if [ ! -L /etc/nginx/sites-enabled/rlg ]; then
    sudo ln -s /etc/nginx/sites-available/rlg /etc/nginx/sites-enabled/
fi
sudo nginx -t
sudo systemctl restart nginx

# Docker and Docker Compose setup
log "Starting Docker containers..."
sudo docker-compose -f deployment_and_configuration/docker-compose.yml up -d

# Zapier integration (optional, if Zapier integration is included in the project)
if [ -f "shared/zapier.py" ]; then
    log "Configuring Zapier integration..."
    python3 shared/zapier.py --setup
fi

# Final steps
log "Setup complete! RLG Data and RLG Fans are now ready to use."
log "Access the tools at http://your-domain.com"

#!/bin/bash

# Stop script execution on errors
set -e

echo "Starting frontend deployment..."

# Update the system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Node.js and npm
echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs

# Clone or pull the latest frontend code
if [ ! -d "frontend" ]; then
  echo "Cloning frontend repository..."
  git clone https://github.com/yourusername/frontend-repo.git frontend
else
  echo "Updating frontend repository..."
  cd frontend
  git pull origin main
  cd ..
fi

# Navigate to the frontend folder
cd frontend

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

# Build the frontend
echo "Building the frontend..."
npm run build

# Deploy the build folder to the web server
echo "Deploying the build to the web server..."
sudo rm -rf /var/www/html/*
sudo cp -r dist/* /var/www/html/

# Restart the web server
echo "Restarting Nginx..."
sudo systemctl restart nginx

echo "Frontend deployment complete!"

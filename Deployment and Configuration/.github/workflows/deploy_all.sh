#!/bin/bash

# Stop script execution on errors
set -e

echo "Starting full deployment..."

# Backend deployment
echo "Deploying backend..."
./deploy_backend.sh

# Frontend deployment
echo "Deploying frontend..."
./deploy_frontend.sh

echo "Full deployment complete!"

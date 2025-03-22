#!/bin/bash

# Stop script execution on errors
set -e

echo "Running post-deployment tests..."

# Check backend API health
echo "Testing backend health..."
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://your-backend-domain.com/health)
if [ "$BACKEND_HEALTH" -eq 200 ]; then
  echo "Backend is healthy!"
else
  echo "Backend health check failed with status code: $BACKEND_HEALTH"
  exit 1
fi

# Check frontend homepage
echo "Testing frontend homepage..."
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://your-frontend-domain.com)
if [ "$FRONTEND_HEALTH" -eq 200 ]; then
  echo "Frontend is healthy!"
else
  echo "Frontend health check failed with status code: $FRONTEND_HEALTH"
  exit 1
fi

echo "All post-deployment tests passed successfully!"

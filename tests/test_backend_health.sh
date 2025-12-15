#!/bin/bash

#Test script for backend container
#Tests backen /health endpoint

BACKEND_URL="http://localhost:5000/api/health"

echo "Testing backend health endpoint..."

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL")

if [ "$HTTP_STATUS" -eq 200 ]; then
	echo "Backend health test passed (HTTP $HTTP_STATUS)"
	exit 0
else
	echo "Backend health test failed (HTPP $HTTP_STATUS)"
	exit 1
fi

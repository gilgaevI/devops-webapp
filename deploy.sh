#!/bin/bash

set -e

echo "=== Pull latest images ==="
docker compose pull

echo "=== Restart services ==="
docker compose up -d

echo "=== Check services ==="
docker compose ps

echo "=== Deployment completed ==="

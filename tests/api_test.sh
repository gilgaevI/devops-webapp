#!/bin/bash

set -e

BASE_URL="http://localhost"

echo "=== GET /health ==="
curl --fail "$BASE_URL/health"
echo
echo

echo "=== GET /db ==="
curl --fail "$BASE_URL/db"
echo
echo

echo "=== POST /servers ==="

RESPONSE=$(curl --fail -s \
  -X POST "$BASE_URL/servers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ci-test-server",
    "status": "up",
    "cpu": 70,
    "ram": 4096
  }')

echo "$RESPONSE"

SERVER_ID=$(echo "$RESPONSE" | python -c "
import sys
import json
data = json.load(sys.stdin)
print(data['id'])
")

echo "Created server ID: $SERVER_ID"
echo

echo "=== GET /servers/$SERVER_ID ==="

curl --fail \
  "$BASE_URL/servers/$SERVER_ID"

echo
echo

echo "=== PUT /servers/$SERVER_ID ==="

curl --fail \
  -X PUT "$BASE_URL/servers/$SERVER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "cpu": 80,
    "status": "up"
  }'

echo
echo

echo "=== DELETE /servers/$SERVER_ID ==="

curl --fail \
  -X DELETE "$BASE_URL/servers/$SERVER_ID"

echo
echo

echo "=== GET deleted server ==="

if curl -s -o /dev/null -w "%{http_code}" \
  "$BASE_URL/servers/$SERVER_ID" | grep -q "^404$"; then
    echo "Server correctly returns 404"
else
    echo "ERROR: deleted server is still available"
    exit 1
fi

echo
echo "=== ALL API TESTS PASSED ==="

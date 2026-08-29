#!/bin/bash
echo "=============================="
echo "     DEVOPS WEBAPP MONITOR"
echo "=============================="
echo
echo "[CONTAINERS]"
docker compose ps
echo
echo "[HEALTH]"
if curl -fs http://localhost/health > /dev/null; then
    echo "Backend: OK"
else
    echo "Backend: FAILED"
fi
echo
echo "[RESOURCES]"
docker stats --no-stream \
    --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

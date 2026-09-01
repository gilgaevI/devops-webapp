#!/bin/bash

FAILED=0
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGFILE="$SCRIPT_DIR/monitor.log"

exec >> "$LOGFILE" 2>&1
echo
echo "Check time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=============================="
echo "      DEVOPS WEBAPP MONITOR"
echo "=============================="

echo
echo "[CONTAINERS]"

docker compose ps

echo
echo "[STATUS]"

if curl -fs http://localhost/health > /dev/null; then
    echo "Backend: OK"
else
    echo "Backend: FAILED"
    FAILED=1
fi

if curl -fs http://localhost/ > /dev/null; then
    echo "Nginx: OK"
else
    echo "Nginx: FAILED"
    FAILED=1
fi

if docker compose exec -T postgres \
    pg_isready -U "${POSTGRES_USER}" -d postgres > /dev/null 2>&1; then
    echo "PostgreSQL: OK"
else
    echo "PostgreSQL: FAILED"
    FAILED=1
fi

echo
echo "[RESOURCES]"

docker stats --no-stream \
    --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

echo
echo "[DISK]"

DISK_USAGE=$(df -P / | awk 'NR==2 {print $5}' | tr -d '%')

echo "Disk usage: ${DISK_USAGE}%"

if [ "$DISK_USAGE" -ge 80 ]; then
    echo "WARNING: Disk usage is above 80%"
    FAILED=1
else
    echo "Disk usage is normal"
fi

echo
echo "[SUMMARY]"
if [ "$FAILED" -eq 0 ]; then
    echo "ALL CHECKS PASSED"
    exit 0
else
    echo "SOME CHECKS FAILED"
    exit 1
fi

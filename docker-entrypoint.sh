#!/bin/bash
set -e

echo "=========================================="
echo "  Video Parser - Starting Services"
echo "=========================================="

mkdir -p static/videos static/images downloads cache logs

if [ -n "$DB_HOST" ] && [ -n "$DB_USER" ] && [ -n "$DB_NAME" ]; then
    echo "Waiting for MySQL: ${DB_HOST}:${DB_PORT:-3306}"
    python - <<'PY'
import os
import sys
import time
import mysql.connector

host = os.getenv("DB_HOST")
port = int(os.getenv("DB_PORT", "3306"))
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD", "")
database = os.getenv("DB_NAME")

for i in range(40):
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connection_timeout=3,
        )
        conn.close()
        print("MySQL is ready")
        sys.exit(0)
    except Exception:
        time.sleep(2)

print("MySQL is not reachable")
sys.exit(1)
PY
fi

echo "[1/2] Starting FastAPI backend on port 5001..."
python api.py &
API_PID=$!

sleep 3

if ! kill -0 $API_PID 2>/dev/null; then
    echo "Error: FastAPI backend failed to start"
    exit 1
fi

echo "[1/2] FastAPI backend started successfully (PID: $API_PID)"

echo "[2/2] Starting Gradio frontend on port 7860..."
python app.py

kill $API_PID 2>/dev/null || true

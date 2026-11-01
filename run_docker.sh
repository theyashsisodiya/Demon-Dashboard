#!/bin/bash
echo "========================================================"
echo "  Launching Demon-Dashboard via Docker"
echo "========================================================"

if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed. Please install Docker first."
    exit 1
fi

echo "Building and starting Demon-Dashboard container..."
docker compose up -d --build

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================================"
    echo "  Demon-Dashboard is RUNNING in Docker!"
    echo "  Access URL: http://localhost:8080"
    echo "========================================================"
    echo "Live logs: docker logs -f demon-dashboard"
    echo "Stop:      docker compose down"
else
    echo "[ERROR] Failed to start Docker container."
fi

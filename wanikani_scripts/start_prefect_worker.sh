#!/bin/bash
# Start Prefect Worker
# Keep this terminal open - the worker needs to run to execute flows

echo "=================================="
echo "Starting Prefect Worker"
echo "=================================="
echo ""
echo "This worker will execute flows when triggered from the UI"
echo ""
echo "Keep this terminal open!"
echo "Press Ctrl+C to stop the worker"
echo ""
echo "=================================="
echo ""

cd "$(dirname "$0")"

# Check if server is running
if ! curl -s http://localhost:4200/api/health > /dev/null 2>&1; then
    echo "⚠ WARNING: Prefect server doesn't seem to be running!"
    echo ""
    echo "Start the server first in another terminal:"
    echo "  ./start_prefect_server.sh"
    echo ""
    echo "Or run: prefect server start"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
fi

echo "Starting worker for pool: default-agent-pool"
echo ""
prefect worker start --pool "default-agent-pool"

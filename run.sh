#!/usr/bin/env bash
# ==============================================================================
# OmniMCP Pro Unified Root Launcher
# Starts both FastAPI Web API Gateway & Vite React Command Center
# ==============================================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT_DIR}"

echo -e "\033[1;36m"
echo "================================================================================"
echo "   ____                  _ __  __  ____ ____     ____            "
echo "  / __ \____ ___  ____  (_)  \/  |/ ___|  _ \   |  _ \ _ __ ___  "
echo " / / / / __ \`__ \/ __ \/ / /\_/ | |   | |_) |  | |_) | '__/ _ \ "
echo "/ /_/ / / / / / / / / / / /  / / | |___|  __/   |  __/| | | (_) |"
echo "\____/_/ /_/ /_/_/ /_/_/_/  /_/   \____|_|      |_|   |_|  \___/ "
echo "================================================================================"
echo -e "\033[0m"
echo -e "\033[1;32m[OmniMCP Pro]\033[0m Starting unified protocol gateway & web command center..."

# 1. Ensure Python dependencies are synced
if [ ! -d ".venv" ]; then
    echo -e "\033[1;33m[Backend]\033[0m Initializing Python virtual environment via uv..."
    uv sync
fi

# 2. Ensure Frontend dependencies are installed
if [ ! -d "node_modules" ] || [ ! -d "frontend/node_modules" ]; then
    echo -e "\033[1;33m[Frontend]\033[0m Installing frontend dependencies via npm..."
    npm install
fi

# Trap to ensure cleanup of all background child processes
cleanup() {
    echo -e "\n\033[1;33m[OmniMCP Pro]\033[0m Shutting down backend and frontend servers..."
    kill $(jobs -p) 2>/dev/null || true
    wait 2>/dev/null || true
    echo -e "\033[1;32m[OmniMCP Pro]\033[0m Clean shutdown complete. Goodbye!"
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 3. Launch FastAPI backend on port 8000
echo -e "\033[1;34m[Backend]\033[0m Launching FastAPI server on http://127.0.0.1:8000..."
uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to become responsive
for i in {1..30}; do
    if curl -s http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
        echo -e "\033[1;32m[Backend]\033[0m API Gateway is live at http://127.0.0.1:8000"
        break
    fi
    sleep 0.5
done

# 4. Launch Vite React Frontend on port 5173
echo -e "\033[1;35m[Frontend]\033[0m Launching Vite Web Command Center on http://localhost:5173..."
npm run dev &
FRONTEND_PID=$!

echo -e "\n\033[1;32m✓ OmniMCP Pro is ready!\033[0m"
echo -e "  → Web Command Center: \033[1;36mhttp://localhost:5173\033[0m"
echo -e "  → REST API Docs:      \033[1;36mhttp://localhost:8000/docs\033[0m"
echo -e "  → FastMCP Stdio:      \033[1;36muv run -m src.mcp_server.server\033[0m"
echo -e "\nPress [Ctrl+C] to stop all servers.\n"

# Wait for both processes
wait "${BACKEND_PID}" "${FRONTEND_PID}"

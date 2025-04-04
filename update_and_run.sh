#!/bin/bash
# Script to update, install dependencies, and run the AI NVCB application

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Store process IDs
BACKEND_PID=""
FRONTEND_PID=""

# Function to clean up processes on exit
cleanup() {
    echo -e "\n${BLUE}==== Shutting down servers ====${NC}"
    
    if [ ! -z "$BACKEND_PID" ]; then
        echo "Terminating backend server (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Terminating frontend server (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    echo "All processes terminated."
    exit 0
}

# Set up trap to catch SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

# Function to run a command and handle errors
run_command() {
    echo -e "\n${BLUE}[Running]${NC} $1"
    eval $1
    if [ $? -ne 0 ]; then
        echo -e "${RED}[Error]${NC} Command failed: $1"
        return 1
    else
        echo -e "${GREEN}[Success]${NC} $1"
        return 0
    fi
}

# Step 1: Update git repository if it exists
if [ -d ".git" ]; then
    echo -e "\n${BLUE}==== Updating repository ====${NC}"
    if ! run_command "git pull"; then
        echo -e "${YELLOW}[Warning]${NC} Repository update failed, continuing with local version."
    fi
else
    echo -e "${YELLOW}[Warning]${NC} Not a git repository, skipping update."
fi

# Step 2: Update dependencies
echo -e "\n${BLUE}==== Updating dependencies ====${NC}"
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}[Error]${NC} pyproject.toml not found. Cannot update dependencies."
    exit 1
fi

if ! run_command "poetry lock"; then
    echo -e "${RED}[Error]${NC} Failed to update Poetry lock file."
    exit 1
fi

if ! run_command "poetry install"; then
    echo -e "${RED}[Error]${NC} Failed to install dependencies."
    exit 1
fi

# Step 3: Start the backend server
echo -e "\n${BLUE}==== Starting backend server ====${NC}"
python run_backend.py &
BACKEND_PID=$!
echo "Backend server started (PID: $BACKEND_PID)"

# Wait for backend to initialize
echo "Waiting for backend to initialize..."
sleep 5

# Step 4: Start the frontend server
echo -e "\n${BLUE}==== Starting frontend server ====${NC}"
cd "$(dirname "$0")"
streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0 &
FRONTEND_PID=$!
echo "Frontend server started (PID: $FRONTEND_PID)"

echo -e "\n${GREEN}==== Application started successfully ====${NC}"
echo "Backend server running at: http://localhost:8000"
echo "Frontend available at: http://localhost:8501"
echo -e "${YELLOW}Press Ctrl+C to stop all servers.${NC}"

# Keep the script running and check if processes are still alive
while true; do
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}Backend server (PID: $BACKEND_PID) terminated unexpectedly.${NC}"
        BACKEND_PID=""
        cleanup
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}Frontend server (PID: $FRONTEND_PID) terminated unexpectedly.${NC}"
        FRONTEND_PID=""
        cleanup
    fi
    
    sleep 1
done 
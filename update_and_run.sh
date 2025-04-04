#!/bin/bash
# Script to update, install dependencies, and run the AI NVCB application in separate terminals

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Detect the terminal emulator available
detect_terminal() {
    if command -v gnome-terminal &> /dev/null; then
        echo "gnome-terminal"
    elif command -v xterm &> /dev/null; then
        echo "xterm"
    elif command -v konsole &> /dev/null; then
        echo "konsole"
    elif command -v terminator &> /dev/null; then
        echo "terminator"
    elif command -v xfce4-terminal &> /dev/null; then
        echo "xfce4-terminal"
    elif command -v terminal &> /dev/null; then
        echo "terminal"
    elif command -v osascript &> /dev/null; then
        echo "apple-terminal"
    else
        echo "unknown"
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

# Detect terminal for opening new windows
TERMINAL=$(detect_terminal)
CURRENT_DIR=$(pwd)

# Step 3: Start the backend server in a new terminal window
echo -e "\n${BLUE}==== Starting backend server in new terminal ====${NC}"

case $TERMINAL in
    "gnome-terminal")
        gnome-terminal -- bash -c "cd \"$CURRENT_DIR\" && python run_backend.py; exec bash"
        ;;
    "xterm")
        xterm -e "cd \"$CURRENT_DIR\" && python run_backend.py; exec bash" &
        ;;
    "konsole")
        konsole --workdir "$CURRENT_DIR" -e "python run_backend.py" &
        ;;
    "terminator")
        terminator --working-directory="$CURRENT_DIR" -e "python run_backend.py" &
        ;;
    "xfce4-terminal")
        xfce4-terminal --working-directory="$CURRENT_DIR" -e "python run_backend.py" &
        ;;
    "terminal")
        terminal --working-directory="$CURRENT_DIR" -e "python run_backend.py" &
        ;;
    "apple-terminal")
        osascript -e "tell application \"Terminal\" to do script \"cd '$CURRENT_DIR' && python run_backend.py\""
        ;;
    *)
        echo -e "${YELLOW}[Warning]${NC} Could not detect terminal emulator. Starting backend in background instead."
        python run_backend.py &
        ;;
esac

echo "Backend server started in new terminal window."

# Wait for backend to initialize
echo "Waiting for backend to initialize..."
sleep 5

# Step 4: Start the frontend server in a new terminal window
echo -e "\n${BLUE}==== Starting frontend server in new terminal ====${NC}"

case $TERMINAL in
    "gnome-terminal")
        gnome-terminal -- bash -c "cd \"$CURRENT_DIR\" && streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0; exec bash"
        ;;
    "xterm")
        xterm -e "cd \"$CURRENT_DIR\" && streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0; exec bash" &
        ;;
    "konsole")
        konsole --workdir "$CURRENT_DIR" -e "streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0" &
        ;;
    "terminator")
        terminator --working-directory="$CURRENT_DIR" -e "streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0" &
        ;;
    "xfce4-terminal")
        xfce4-terminal --working-directory="$CURRENT_DIR" -e "streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0" &
        ;;
    "terminal")
        terminal --working-directory="$CURRENT_DIR" -e "streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0" &
        ;;
    "apple-terminal")
        osascript -e "tell application \"Terminal\" to do script \"cd '$CURRENT_DIR' && streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0\""
        ;;
    *)
        echo -e "${YELLOW}[Warning]${NC} Could not detect terminal emulator. Starting frontend in background instead."
        streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0 &
        ;;
esac

echo "Frontend server started in new terminal window."

echo -e "\n${GREEN}==== Application started successfully ====${NC}"
echo "Backend server running at: http://localhost:8000"
echo "Frontend available at: http://localhost:8501"
echo -e "${YELLOW}You can close each terminal window individually to stop the services.${NC}"
echo -e "${YELLOW}Press Enter to close this launcher...${NC}"
read 
#!/bin/bash

# Format output with colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}======================================${NC}"
echo -e "${YELLOW}  AI NVCB Project Update Helper${NC}"
echo -e "${YELLOW}======================================${NC}"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python is not found in PATH! Please install Python or add it to your PATH.${NC}"
    exit 1
fi

# Check if Git is available
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git is not found in PATH! Please install Git or add it to your PATH.${NC}"
    exit 1
fi

# Check if Poetry is available
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Poetry is not found in PATH! Please install Poetry or add it to your PATH.${NC}"
    exit 1
fi

echo -e "${GREEN}All required tools are available.${NC}"
echo
echo -e "Running update and dependency check script..."
echo

# Make the script executable if it isn't already
chmod +x update_and_test.py

# Run the Python script
python3 update_and_test.py "$@"

if [ $? -ne 0 ]; then
    echo
    echo -e "${RED}There were errors during the update process.${NC}"
    echo -e "${YELLOW}Please check the output above for details.${NC}"
    exit $?
fi

echo
echo -e "${GREEN}Update completed successfully!${NC}"
echo 
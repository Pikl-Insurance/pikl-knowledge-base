#!/bin/bash

# Pikl KB Processor - Web UI Launcher
# Quick script to start the Streamlit UI

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Pikl KB Processor - Web UI${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Running setup...${NC}"
    ./setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Check if Streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo -e "${YELLOW}Streamlit not installed. Installing dependencies...${NC}"
    pip install -r requirements.txt
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo -e "${YELLOW}Warning: .env.local not found${NC}"
    echo "Please create .env.local with your API keys:"
    echo "  ANTHROPIC_API_KEY=your_key_here"
    echo "  INTERCOM_ACCESS_TOKEN=your_token_here"
    echo ""
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
fi

echo -e "${GREEN}Starting Streamlit UI...${NC}"
echo ""
echo -e "The UI will open in your browser at: ${BLUE}http://localhost:8501${NC}"
echo ""
echo -e "${YELLOW}Tip:${NC} Press Ctrl+C to stop the server"
echo ""

# Launch Streamlit
streamlit run app.py

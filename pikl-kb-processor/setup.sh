#!/bin/bash

# Pikl KB Processor Setup Script

set -e

echo "🚀 Pikl KB Processor Setup"
echo "=========================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "✓ Python $python_version (meets requirement >= $required_version)"
else
    echo "✗ Python $python_version is too old (need >= $required_version)"
    echo "Please upgrade Python and try again."
    exit 1
fi

echo ""

# Create virtual environment
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
    read -p "Recreate it? (y/N): " recreate
    if [ "$recreate" = "y" ] || [ "$recreate" = "Y" ]; then
        echo "Removing old virtual environment..."
        rm -rf venv
        echo "Creating new virtual environment..."
        python3 -m venv venv
    fi
else
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "✓ Virtual environment ready"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Dependencies installed"
echo ""

# Setup .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - INTERCOM_ACCESS_TOKEN"
else
    echo ".env file already exists"
fi

echo ""

# Create data directories
echo "Creating data directories..."
mkdir -p data/transcripts
mkdir -p data/emails
mkdir -p reports
mkdir -p examples

echo "✓ Directories created"
echo ""

# Test setup
echo "Testing setup..."
if python cli.py --help > /dev/null 2>&1; then
    echo "✓ CLI working"
else
    echo "✗ CLI test failed"
    exit 1
fi

echo ""
echo "=========================="
echo "✅ Setup Complete!"
echo "=========================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Test Intercom connection: python cli.py test-intercom"
echo "4. Fetch your KB: python cli.py fetch-kb"
echo "5. See USAGE_GUIDE.md for full documentation"
echo ""

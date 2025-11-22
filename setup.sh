#!/bin/bash
# Setup script for Company Research Assistant (macOS/Linux)

echo "========================================"
echo "Company Research Assistant Setup"
echo "========================================"
echo ""

# Check Python installation
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

echo "Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
else
    python3 -m venv venv
    echo "Virtual environment created!"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "========================================"
    echo "IMPORTANT: Edit .env file and add your API keys!"
    echo "========================================"
    echo ""
    echo "You need:"
    echo "1. Groq API key - Get from https://console.groq.com"
    echo "2. SerpAPI key - Get from https://serpapi.com"
    echo ""
else
    echo ".env file already exists."
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Run: python run.py --mode web"
echo "3. Open browser to http://localhost:8000"
echo ""
echo "For voice mode: python run.py --mode voice"
echo ""

#!/bin/bash

# Setup script for Deep Research Agent (LangGraph)

set -e  # Exit on error

echo "================================================"
echo "  Deep Research Agent - Setup Script"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.10 or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✅ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Setup environment file
echo "Setting up environment variables..."
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Skipping..."
else
    cp .env.example .env
    echo "✅ .env file created from .env.example"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your API keys:"
    echo "   - FIRECRAWL_API_KEY"
    echo "   - OPENAI_API_KEY or FIREWORKS_API_KEY"
fi
echo ""

# Create reports directory
echo "Creating reports directory..."
mkdir -p reports
echo "✅ Reports directory created"
echo ""

# Run tests
echo "Running tests..."
pytest tests/ -v
if [ $? -eq 0 ]; then
    echo "✅ All tests passed"
else
    echo "⚠️  Some tests failed, but setup is complete"
fi
echo ""

echo "================================================"
echo "  Setup Complete! 🎉"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your API keys"
echo "  2. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo "  3. Run the agent:"
echo "     python run.py"
echo ""
echo "For more information, see README.md"
echo ""

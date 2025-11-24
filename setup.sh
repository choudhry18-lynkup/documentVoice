#!/bin/bash

# Setup script for HVAC Voice Agent

echo "Setting up HVAC Voice Agent..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env and fill in your API keys:"
    echo "   - LIVEKIT_URL"
    echo "   - LIVEKIT_API_KEY"
    echo "   - LIVEKIT_API_SECRET"
    echo "   - OPENAI_API_KEY"
    echo ""
fi

# Create documents directory
mkdir -p documents
echo "Created documents/ directory. Add your PDF manuals here."

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Add PDF manuals to the documents/ directory"
echo "3. Test document loading: python test_documents.py"
echo "4. Run the agent: python main.py dev"
echo ""


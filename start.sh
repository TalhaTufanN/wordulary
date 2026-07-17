#!/bin/bash

echo "=============================================="
echo "       Starting Wordulary..."
echo "=============================================="

# Determine python command
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "Python could not be found. Please install Python 3.8+."
    exit 1
fi

# Create Virtual Environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON -m venv venv
fi

# Activate Virtual Environment
source venv/bin/activate

# Install Requirements
echo "Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating a template .env file..."
    echo 'DEEPL_API_KEY="your_actual_deepl_api_key_here"' > .env
    echo "-------------------------------------------------------------------"
    echo "ATTENTION: A new .env file has been created."
    echo "Please open the .env file and add your DEEPL_API_KEY!"
    echo "Then, run this script again."
    echo "-------------------------------------------------------------------"
    exit 1
fi

# Open browser (tries to handle different OS commands)
echo "Opening browser..."
if command -v xdg-open > /dev/null; then
  xdg-open http://127.0.0.1:8000
elif command -v open > /dev/null; then
  open http://127.0.0.1:8000
else
  echo "Please open http://127.0.0.1:8000 in your browser."
fi

# Run the app
echo "Starting the server..."
$PYTHON -m uvicorn app:app --reload

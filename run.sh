#!/bin/bash
# Run the Firebolt Intelligent Query Assistant

# Check if API key is provided as argument
if [ $# -eq 0 ]; then
    echo "❌ Error: ANTHROPIC_API_KEY is required"
    echo "Usage: $0 <anthropic_api_key>"
    echo "Example: $0 your-actual-anthropic-api-key-here"
    exit 1
fi

echo "🚀 Starting Firebolt Intelligent Query Assistant..."

# Activate virtual environment
source venv/bin/activate

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Set Claude API key from command line argument (secure - not stored anywhere)
export ANTHROPIC_API_KEY="$1"
echo "🔐 API key configured securely (not stored in files)"

# Run the app
echo "🌐 Access the app at: http://localhost:8504"
streamlit run app.py --server.port=8504

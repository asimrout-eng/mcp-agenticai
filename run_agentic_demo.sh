#!/bin/bash
# Launch the Agentic AI Business Intelligence Demo

# Check if API key is provided
if [ $# -eq 0 ]; then
    echo "🤖 Agentic AI Business Intelligence Demo"
    echo "========================================"
    echo "❌ Error: ANTHROPIC_API_KEY is required"
    echo "Usage: $0 <anthropic_api_key>"
    echo "Example: $0 your-actual-anthropic-api-key-here"
    echo ""
    echo "🚀 This demo showcases:"
    echo "   • Multi-step AI reasoning"
    echo "   • Business intelligence automation"  
    echo "   • Planning trace visualization"
    echo "   • Hypothesis-driven analysis"
    exit 1
fi

echo "🤖 Starting Agentic AI Business Intelligence Demo..."
echo "=================================================="

# Activate virtual environment
source venv/bin/activate

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Set Claude API key securely
export ANTHROPIC_API_KEY="$1"
echo "🔐 API key configured securely"

# Launch the agentic AI demo
echo "🧠 Launching Agentic AI Demo..."
echo "🌐 Access the demo at: http://localhost:8505"
echo ""
echo "🎯 Demo Features:"
echo "   • Ask complex business questions"
echo "   • Watch AI agent reasoning in real-time"
echo "   • See multi-step analysis breakdowns"
echo "   • View confidence scores and insights"
echo ""

streamlit run agentic_ai_demo.py --server.port=8505

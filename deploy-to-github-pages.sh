#!/bin/bash

# Deploy to GitHub Pages - asimrout-eng/mcp-agenticai
# This script will push the project to your GitHub repository and set up GitHub Pages

echo "🚀 Deploying Firebolt AI Demos to GitHub Pages"
echo "Repository: https://github.com/asimrout-eng/mcp-agenticai"
echo "=================================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
fi

# Add your repository as remote
echo "📡 Adding your GitHub repository as remote..."
git remote remove myrepo 2>/dev/null || true
git remote add myrepo https://github.com/asimrout-eng/mcp-agenticai.git

# Stage all files
echo "📦 Staging files for commit..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    echo "💾 Committing changes..."
    git commit -m "Deploy Firebolt AI-Powered Analytics Demos to GitHub Pages

Features:
- 🧠 Natural Language to SQL Demo
- 🤖 Agentic AI Business Intelligence Demo  
- 📱 Responsive GitHub Pages site
- 🎨 Professional UI with interactive features
- 📊 Complete documentation and setup guides"
fi

# Push to your repository
echo "🚀 Pushing to your GitHub repository..."
if git push myrepo main; then
    echo ""
    echo "✅ Successfully deployed to GitHub!"
    echo ""
    echo "🎯 Next Steps:"
    echo "1. Go to: https://github.com/asimrout-eng/mcp-agenticai/settings/pages"
    echo "2. Under 'Source', select 'GitHub Actions'"
    echo "3. Wait 2-5 minutes for deployment"
    echo ""
    echo "🌐 Your site will be available at:"
    echo "   https://asimrout-eng.github.io/mcp-agenticai/"
    echo ""
    echo "📋 Demo URLs:"
    echo "   NL2SQL:     https://asimrout-eng.github.io/mcp-agenticai/demos/nl2sql.html"
    echo "   Agentic AI: https://asimrout-eng.github.io/mcp-agenticai/demos/agentic-ai.html"
    echo ""
else
    echo "❌ Failed to push to repository"
    echo "Please check your repository permissions and try again"
    echo ""
    echo "🔧 Manual steps:"
    echo "1. Make sure you have write access to the repository"
    echo "2. Try: git push myrepo main --force (if needed)"
    echo "3. Or push via GitHub Desktop/VS Code"
fi

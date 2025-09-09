# 🚀 Firebolt Intelligent Query Assistant

A powerful Natural Language to SQL converter for Firebolt databases with real-time query execution and sub-second performance insights.

## ✨ Features

- 🧠 **AI-Powered NL2SQL**: Convert natural language questions to SQL using Claude 3.5 Sonnet
- 🔌 **Real Firebolt Integration**: Direct MCP server connection to Firebolt databases  
- 📊 **Dynamic Schema Discovery**: Automatic table discovery with DDL and primary indexes
- ⚡ **Performance Tracking**: Real-time query execution times and performance metrics
- 🎨 **Interactive UI**: Beautiful Streamlit interface with editable SQL queries
- 📈 **Data Visualization**: Automatic chart generation for query results

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
./run.sh <your_anthropic_api_key>
```

**Example:**
```bash
./run.sh your-actual-anthropic-api-key-here
```

**🔐 Security Note:** The API key is provided as a command line argument and is never stored in any files.

### 3. Access the App
Open your browser to: **http://localhost:8504**

## 📁 Project Structure

```
mcp-nl2sql/
├── app.py                      # 🎯 Main Streamlit application
├── nl2sql_claude.py            # 🧠 Claude API integration for NL2SQL
├── test_mcp_real.py            # 🔌 MCP server integration functions
├── requirements.txt            # 📦 Python dependencies
├── demo_prompts_working.md     # 💡 Demo questions and expected SQL
├── env_example.txt             # 🔑 Environment variables template
├── run.sh                      # 🏃 Quick start script
├── fb-logo.png                 # 🔥 Firebolt logo for UI
├── README.md                   # 📖 This file
└── venv/                       # 🐍 Virtual environment
```

## 🔧 Configuration

### Environment Variables (Optional)
You can pre-configure credentials via environment variables, or enter them directly in the UI. 
Copy `env_example.txt` to `.env` and update with your credentials:

```env
# Firebolt MCP Server Credentials
FIREBOLT_MCP_ACCOUNT=your_account
FIREBOLT_MCP_DATABASE=your_database  
FIREBOLT_MCP_ENGINE=your_engine
FIREBOLT_MCP_CLIENT_ID=your_service_account_id
FIREBOLT_MCP_CLIENT_SECRET=your_service_account_secret

# Claude API (NOT STORED - API key passed via command line only)
# ANTHROPIC_API_KEY=provided_at_runtime_via_command_line
```

## 🎯 How It Works

1. **Connect**: Enter your Firebolt credentials in the UI (or configure via environment variables)
2. **Discover**: App automatically discovers all tables, columns, DDL, and primary indexes
3. **Ask**: Type your question in natural language
4. **Convert**: Claude AI converts your question to optimized Firebolt SQL  
5. **Edit**: Review and modify the generated SQL if needed
6. **Execute**: Run the query on your live Firebolt database
7. **Analyze**: View results with execution times and auto-generated visualizations

## 💡 Example Questions (AdTech Demo)

- "Show me the total conversions and revenue for each campaign type for AutoCorp"
- "Which publishers are performing best for AutoCorp in terms of conversion rate and revenue?"
- "Show me AutoCorp's hourly conversion patterns with revenue trends"
- "What's the cost per conversion and ROI for each of AutoCorp's campaign types?"
- "Break down AutoCorp's campaign performance by publisher region and campaign type"

## 🏗️ Architecture

- **Frontend**: Streamlit web application
- **NL2SQL**: Claude 3.5 Sonnet via Anthropic API
- **Database**: Firebolt cloud data warehouse
- **Integration**: Model Context Protocol (MCP) server
- **Visualization**: Plotly charts and tables


## 🛠️ Development

### Core Files
- `app.py` - Main Streamlit UI and user interaction
- `nl2sql_claude.py` - Claude AI integration and prompt engineering
- `test_mcp_real.py` - MCP server communication and query execution



## 🤝 Contributing

This is a demonstration project showcasing Firebolt's sub-second analytics capabilities with AI-powered natural language interfaces.

## 📞 Support

For Firebolt-related questions, visit: https://docs.firebolt.io/
For technical support, contact your Firebolt representative.

---

**Built with ❤️ for Firebolt Analytics demos and customer showcases**
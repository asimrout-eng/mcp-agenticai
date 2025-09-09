import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import asyncio
import json
import time
import os
import sys
from datetime import datetime
from PIL import Image

# Add current directory to path
sys.path.append('/Users/kushagrnagpal/mcp-nl2sql')
from nl2sql_claude import NL2SQLConverter
from test_mcp_real import execute_query_via_mcp

# Page config
st.set_page_config(
    page_title="Firebolt Intelligent Query Assistant",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean, modern design
st.markdown("""
<style>
    /* Global styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #E53E3E 0%, #C62828 100%);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(229, 62, 62, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .logo-title-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1.5rem;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
    }
    
    .firebolt-logo {
        width: 80px;
        height: 80px;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    
    .header-title {
        font-size: 2.6rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        letter-spacing: -0.5px;
        line-height: 1.1;
        white-space: nowrap;
    }
    
    .header-subtitle {
        font-size: 1.3rem;
        opacity: 0.95;
        margin: 0;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    
    /* Connection card */
    .connection-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        color: white;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .connection-card.connected {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    }
    
    .connection-card.disconnected {
        background: linear-gradient(135deg, #FF6B6B 0%, #EE5A24 100%);
    }
    
    /* Query interface */
    .query-container {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 2rem 0;
        color: white;
        box-shadow: 0 12px 40px rgba(240, 147, 251, 0.4);
    }
    
    .query-title {
        font-size: 2.8rem;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Results container */
    .results-container {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 2rem 0;
        box-shadow: 0 12px 40px rgba(255, 236, 210, 0.4);
    }
    
    .results-title {
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 2rem;
        color: #2d3748;
        font-weight: 700;
    }
    
    /* Performance section */
    .performance-container {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 3rem;
        border-radius: 20px;
        margin: 2rem 0;
        box-shadow: 0 12px 40px rgba(168, 237, 234, 0.4);
    }
    
    .performance-title {
        font-size: 2.8rem;
        text-align: center;
        margin-bottom: 1.5rem;
        color: #2d3748;
        font-weight: 700;
    }
    
    .performance-subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #4a5568;
        margin-bottom: 2rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 0.5rem;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .metric-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2d3748;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #718096;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 28px rgba(102, 126, 234, 0.6);
        border-color: rgba(255,255,255,0.3);
    }
    
    /* Engine time display */
    .engine-time-reveal {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 2.5rem;
        border-radius: 16px;
        text-align: center;
        margin: 2rem 0;
        border: 3px solid #28a745;
        box-shadow: 0 8px 32px rgba(40, 167, 69, 0.3);
    }
    
    .engine-time-title {
        font-size: 2.5rem;
        color: #155724;
        margin: 0;
        font-weight: 700;
    }
    
    .engine-time-value {
        font-size: 3rem;
        color: #155724;
        margin: 1rem 0;
        font-weight: 800;
    }
    
    .engine-time-desc {
        font-size: 1.2rem;
        color: #155724;
        margin: 0;
    }
    
    /* Schema card */
    .schema-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 6px 24px rgba(102, 126, 234, 0.3);
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Responsive design */
    @media (max-width: 768px) {
        .logo-title-container {
            flex-direction: column;
            gap: 1rem;
        }
        
        .header-title {
            font-size: 1.8rem;
            text-align: center !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .metric-card {
            margin: 0.25rem;
        }
    }
    
    /* For very wide screens, ensure proper scaling */
    @media (min-width: 1400px) {
        .header-title {
            font-size: 3.0rem;
        }
    }
</style>
""", unsafe_allow_html=True)

class FireboltNL2SQLApp:
    """Clean, modern Firebolt Intelligent Query Assistant"""
    
    def __init__(self):
        self.init_session_state()
        self.nl2sql_converter = None
    
    def init_session_state(self):
        """Initialize session state variables"""
        if 'is_connected' not in st.session_state:
            st.session_state.is_connected = False
        if 'credentials' not in st.session_state:
            st.session_state.credentials = {}
        if 'schema_info' not in st.session_state:
            st.session_state.schema_info = {}
        if 'last_query_result' not in st.session_state:
            st.session_state.last_query_result = None
        if 'last_executed_sql' not in st.session_state:
            st.session_state.last_executed_sql = ""
        if 'last_execution_time' not in st.session_state:
            st.session_state.last_execution_time = None
        if 'query_history' not in st.session_state:
            st.session_state.query_history = []
        if 'engine_time_data' not in st.session_state:
            st.session_state.engine_time_data = None
        if 'show_visualizations' not in st.session_state:
            st.session_state.show_visualizations = False
        if 'selected_chart_type' not in st.session_state:
            st.session_state.selected_chart_type = None
        if 'connection_error' not in st.session_state:
            st.session_state.connection_error = None
    
    def render_header(self):
        """Render clean header with proper alignment"""
        # Load Firebolt logo
        try:
            logo = Image.open('/Users/kushagrnagpal/mcp-nl2sql/fb-logo.png')
        except:
            logo = None
        
        st.markdown("""
        <div class="header-container">
            <div class="logo-title-container" style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 10px;">
        """, unsafe_allow_html=True)
        
        if logo:
            # Create a centered layout with bigger logo and title on one line
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                logo_col, title_col = st.columns([1, 4])
                with logo_col:
                    st.image(logo, width=120)
                with title_col:
                    st.markdown("""
                    <h1 class="header-title" style="margin: 0; line-height: 120px; text-align: left; white-space: nowrap;">Firebolt Intelligent Query Assistant</h1>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="text-align: center;">
                    <h1 class="header-title">🔥 Firebolt Intelligent Query Assistant</h1>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
            </div>
            <p class="header-subtitle" style="text-align: center; margin-top: 0;">Transform natural language into blazing-fast SQL insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_demo_sidebar(self):
        """Render demo sidebar with session stats"""
        with st.sidebar:
            if st.session_state.is_connected:
                st.markdown("## 📊 Session Stats")
                st.metric("Queries Executed", len(st.session_state.query_history))
                if st.session_state.schema_info:
                    st.metric("Tables", len(st.session_state.schema_info))
                
                st.markdown("## 🎮 Gaming Analytics")
                st.markdown("""
                **Available Tables:**
                - Players (Demographics)
                - Games (Sessions)  
                - Transactions (Revenue)
                - Events (Player behavior)
                - External tables (Real-time data)
                """)
            else:
                st.markdown("## 🚀 Getting Started")
                st.markdown("""
                **Connect to explore:**
                - Gaming player analytics
                - Real-time event data
                - Revenue insights
                - Multi-table joins
                """)
    
    def render_connection_ui(self):
        """Render connection interface"""
        if not st.session_state.is_connected:
            st.markdown("""
            <div class="connection-card disconnected">
                <h2 style="margin: 0; text-align: center;">🔌 Connect to Firebolt</h2>
                <p style="text-align: center; margin: 0.5rem 0 0 0; opacity: 0.9;">
                    Enter your credentials to begin
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Initialize session state for credentials
            if 'selected_client_id' not in st.session_state:
                st.session_state.selected_client_id = ""
            if 'auto_client_secret' not in st.session_state:
                st.session_state.auto_client_secret = ""
            
            # Manual credential entry only - no hardcoded options
            client_id_options = [
                "Enter manually"
            ]
            
            # Manual credential entry only - users must provide their own credentials
            custom_client_id = st.text_input("🔑 Client ID", value="", placeholder="Enter your Firebolt client ID", key="custom_client_id")
            custom_client_secret = st.text_input("🔒 Client Secret", value="", type="password", placeholder="Enter your Firebolt client secret", key="custom_client_secret")
            st.session_state.selected_client_id = custom_client_id
            st.session_state.auto_client_secret = custom_client_secret

            with st.form("connection_form"):
                col1, col2 = st.columns(2)
                with col1:
                    # Account dropdown with options
                    account_options = [
                        "kush-demo-account",  # Default
                        "jauneet-india-demo",
                        "se-demo-account",
                        "Custom (Enter manually)"
                    ]
                    account_choice = st.selectbox("🏢 Account", account_options, index=0)
                    
                    if account_choice == "Custom (Enter manually)":
                        account = st.text_input("Enter Custom Account", value="", placeholder="Enter your account name")
                    else:
                        account = account_choice
                    
                    # Database dropdown with options
                    database_options = [
                        "devr",  # Default
                        "intdemo",
                        "kush_firex_demo",
                        "Custom (Enter manually)"
                    ]
                    database_choice = st.selectbox("🗄️ Database", database_options, index=0)
                    
                    if database_choice == "Custom (Enter manually)":
                        database = st.text_input("Enter Custom Database", value="", placeholder="Enter your database name")
                    else:
                        database = database_choice
                        
                with col2:
                    # Engine dropdown with options
                    engine_options = [
                        "kush_engine",  # Default
                        "jimmydemo",
                        "kush_test_engine",
                        "Custom (Enter manually)"
                    ]
                    engine_choice = st.selectbox("⚡ Engine", engine_options, index=0)
                    
                    if engine_choice == "Custom (Enter manually)":
                        engine = st.text_input("Enter Custom Engine", value="", placeholder="Enter your engine name")
                    else:
                        engine = engine_choice
                
                # Get credentials from session state
                client_id = st.session_state.selected_client_id
                client_secret = st.session_state.auto_client_secret
                
                if st.form_submit_button("🚀 Connect", type="primary", use_container_width=True):
                    if all([account, database, engine, client_id, client_secret]):
                        self.connect_to_firebolt(account, database, engine, client_id, client_secret)
                    else:
                        st.error("❌ Please fill in all fields")
            
            # Display persistent connection error if exists
            if st.session_state.connection_error:
                error_data = st.session_state.connection_error
                st.markdown("""
                <div style="background: linear-gradient(135deg, #FF6B6B 0%, #EE5A24 100%); 
                           padding: 2rem; border-radius: 16px; margin: 2rem 0; color: white; 
                           box-shadow: 0 8px 32px rgba(255, 107, 107, 0.4); text-align: center;">
                    <h2 style="margin: 0 0 1rem 0; font-size: 2rem;">🚫 CONNECTION FAILED</h2>
                    <p style="font-size: 1.2rem; margin: 0;">Unable to connect to Firebolt database</p>
                </div>
                """, unsafe_allow_html=True)
                
                error_msg = error_data['error_msg']
                account = error_data['account']
                
                if "account name does not exist" in error_msg.lower() or "not authorized" in error_msg.lower():
                    st.error(f"❌ **Invalid Account Name**: The account '{account}' does not exist in your organization or you don't have access to it.")
                    st.error("🔍 **Please verify**: Account name spelling and your organization access")
                elif "connection" in error_msg.lower() or "failed to create connection" in error_msg.lower():
                    st.error(f"❌ **Connection Failed**: Unable to establish connection to Firebolt")
                    st.error("🔍 **Please check**: Credentials, network connection, and service account permissions")
                elif "client_id" in error_msg.lower() or "client_secret" in error_msg.lower():
                    st.error(f"❌ **Authentication Failed**: Invalid Client ID or Client Secret")
                    st.error("🔍 **Please verify**: Your service account credentials are correct")
                else:
                    st.error(f"❌ **Connection Failed**: {error_msg}")
                
                st.warning("💡 **Common Issues**: Account name typos, expired credentials, insufficient RBAC permissions, or network connectivity")
                st.info("🔄 **Next Steps**: Double-check your credentials above and try connecting again")
                
                # Add button to clear error
                if st.button("🗑️ Clear Error", type="secondary"):
                    st.session_state.connection_error = None
                    st.rerun()
        else:
            st.markdown(f"""
            <div class="connection-card connected">
                <h2 style="margin: 0; text-align: center;">✅ Connected to Firebolt</h2>
                <p style="text-align: center; margin: 0.5rem 0 0 0; opacity: 0.9;">
                    Database: <strong>{st.session_state.credentials['database']}</strong> • 
                    Engine: <strong>{st.session_state.credentials['engine']}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Disconnect", type="secondary"):
                self.disconnect_from_firebolt()
    
    def connect_to_firebolt(self, account, database, engine, client_id, client_secret):
        """Connect to Firebolt and discover schema"""
        with st.spinner("🔌 Connecting to Firebolt..."):
            try:
                # Set environment variables
                os.environ['FIREBOLT_MCP_CLIENT_ID'] = client_id
                os.environ['FIREBOLT_MCP_CLIENT_SECRET'] = client_secret
                os.environ['FIREBOLT_MCP_ACCOUNT'] = account
                os.environ['FIREBOLT_MCP_DATABASE'] = database
                os.environ['FIREBOLT_MCP_ENGINE'] = engine
                
                # Test connection and discover schema
                schema_info = self.discover_schema()
                
                # Store connection details
                st.session_state.credentials = {
                    'account': account,
                    'database': database,
                    'engine': engine,
                    'client_id': client_id,
                    'client_secret': client_secret
                }
                st.session_state.is_connected = True
                st.session_state.schema_info = schema_info
                st.session_state.connection_error = None  # Clear any previous errors
                
                # Initialize NL2SQL converter
                schema_context = self.format_schema_for_claude()
                self.nl2sql_converter = NL2SQLConverter(schema_context=schema_context)
                
                st.success("✅ Connected successfully!")
                st.rerun()
                
            except Exception as e:
                # Reset connection state on failure
                st.session_state.is_connected = False
                st.session_state.credentials = {}
                st.session_state.schema_info = {}
                st.session_state.last_query_result = None
                st.session_state.last_executed_sql = ""
                st.session_state.last_execution_time = None
                st.session_state.engine_time_data = None
                self.nl2sql_converter = None
                
                # Store error in session state for persistent display
                st.session_state.connection_error = {
                    'account': account,
                    'error_msg': str(e),
                    'timestamp': time.time()
                }
                
                # Display prominent connection failure message
                st.markdown("""
                <div style="background: linear-gradient(135deg, #FF6B6B 0%, #EE5A24 100%); 
                           padding: 2rem; border-radius: 16px; margin: 2rem 0; color: white; 
                           box-shadow: 0 8px 32px rgba(255, 107, 107, 0.4); text-align: center;">
                    <h2 style="margin: 0 0 1rem 0; font-size: 2rem;">🚫 CONNECTION FAILED</h2>
                    <p style="font-size: 1.2rem; margin: 0;">Unable to connect to Firebolt database</p>
                </div>
                """, unsafe_allow_html=True)
                
                error_msg = str(e)
                if "account name does not exist" in error_msg.lower() or "not authorized" in error_msg.lower():
                    st.error(f"❌ **Invalid Account Name**: The account '{account}' does not exist in your organization or you don't have access to it.")
                    st.error("🔍 **Please verify**: Account name spelling and your organization access")
                elif "connection" in error_msg.lower() or "failed to create connection" in error_msg.lower():
                    st.error(f"❌ **Connection Failed**: Unable to establish connection to Firebolt")
                    st.error("🔍 **Please check**: Credentials, network connection, and service account permissions")
                elif "client_id" in error_msg.lower() or "client_secret" in error_msg.lower():
                    st.error(f"❌ **Authentication Failed**: Invalid Client ID or Client Secret")
                    st.error("🔍 **Please verify**: Your service account credentials are correct")
                else:
                    st.error(f"❌ **Connection Failed**: {error_msg}")
                
                st.warning("💡 **Common Issues**: Account name typos, expired credentials, insufficient RBAC permissions, or network connectivity")
                
                # Add a retry suggestion
                st.info("🔄 **Next Steps**: Double-check your credentials above and try connecting again")
                st.rerun()
    
    def disconnect_from_firebolt(self):
        """Disconnect from Firebolt"""
        st.session_state.is_connected = False
        st.session_state.credentials = {}
        st.session_state.schema_info = {}
        st.session_state.last_query_result = None
        st.session_state.last_executed_sql = ""
        st.session_state.last_execution_time = None
        st.session_state.engine_time_data = None
        self.nl2sql_converter = None
        st.rerun()
    
    def discover_schema(self):
        """Discover database schema"""
        try:
            # Get tables
            tables_query = "SELECT table_name, table_type, ddl, primary_index FROM information_schema.tables WHERE table_schema = 'public'"
            tables_result = asyncio.run(execute_query_via_mcp(tables_query))
            
            # Get columns
            columns_query = "SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_schema = 'public' ORDER BY table_name, ordinal_position"
            columns_result = asyncio.run(execute_query_via_mcp(columns_query))
            
            # Organize schema information
            schema_info = {}
            
            # Process tables
            for table in tables_result:
                table_name = table['table_name']
                schema_info[table_name] = {
                    'type': table.get('table_type', 'TABLE'),
                    'ddl': table.get('ddl', ''),
                    'primary_index': table.get('primary_index', 'None'),
                    'columns': []
                }
            
            # Process columns
            for column in columns_result:
                table_name = column['table_name']
                if table_name in schema_info:
                    schema_info[table_name]['columns'].append({
                        'name': column['column_name'],
                        'type': column['data_type']
                    })
            
            return schema_info
            
        except Exception as e:
            # Re-raise the exception so connection fails properly
            raise Exception(f"Schema discovery failed: {str(e)}")
    
    def format_schema_for_claude(self):
        """Format schema information for Claude"""
        if not st.session_state.schema_info:
            return ""
        
        context_parts = [
            f"Database: {st.session_state.credentials['database']}",
            "\\nCOMPLETE DATABASE SCHEMA:\\n"
        ]
        
        for table_name, info in st.session_state.schema_info.items():
            context_parts.append(f"## Table: {table_name} ({info['type']})")
            context_parts.append(f"Primary Index: {info['primary_index']}")
            context_parts.append("Columns:")
            
            for col in info['columns']:
                context_parts.append(f"  - {col['name']} ({col['type']})")
            
            context_parts.append("")
        
        return '\\n'.join(context_parts)
    
    def render_schema_info(self):
        """Render schema information"""
        if st.session_state.schema_info:
            with st.expander("📋 Database Schema", expanded=False):
                for table_name, info in st.session_state.schema_info.items():
                    st.markdown(f"""
                    <div class="schema-card">
                        <h4>🗃️ {table_name} ({info['type']})</h4>
                        <p><strong>Primary Index:</strong> {info['primary_index']}</p>
                        <p><strong>Columns:</strong> {', '.join([col['name'] for col in info['columns']])}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    def render_query_interface(self):
        """Render query interface"""
        if not st.session_state.is_connected:
            st.warning("⚠️ Please connect to Firebolt first")
            return
        
        st.markdown("""
        <div class="query-container">
            <h2 class="query-title">💬 Ask Your Question</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Demo queries dropdown
        demo_queries = [
            "Type your own question...",
            "Show me the count of players by country (Simple - 1 table - Market analysis for localization)",
            "Show me total events and average event level by game type from player event data (Intermediate - 2-table join - Game engagement insights)",
            "Show me player event activity by country using our external event data, including total events and unique players (External table integration - Real-time regional analysis)",
            "Show me premium players with their average game score and total events, grouped by country (Advanced - 3-table join - Premium player performance)"
        ]
        
        selected_demo = st.selectbox(
            "🎯 Choose a demo query or type your own:",
            demo_queries,
            index=0
        )
        
        # Handle demo prompt selection
        default_value = ""
        if hasattr(st.session_state, 'selected_demo_prompt'):
            default_value = st.session_state.selected_demo_prompt
            del st.session_state.selected_demo_prompt
        elif selected_demo != "Type your own question...":
            # Extract just the query text before the parentheses
            default_value = selected_demo.split(" (")[0]
        
        question = st.text_area(
            "Enter your question in natural language:",
            value=default_value,
            height=100,
            placeholder="Example: Show me the count of players by country"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🧠 Convert to SQL", type="primary", disabled=not question.strip()):
                self.convert_to_sql(question)
        
        with col2:
            if st.button("⚡ Run Query", type="secondary", disabled=not st.session_state.get('converted_sql', '')):
                self.execute_query(st.session_state.get('converted_sql', ''))
        
        # Show converted SQL
        if st.session_state.get('converted_sql', ''):
            st.markdown("### 📝 Generated SQL")
            edited_sql = st.text_area(
                "Review and edit if needed:",
                value=st.session_state.converted_sql,
                height=150,
                key="sql_editor"
            )
            st.session_state.converted_sql = edited_sql
    
    def convert_to_sql(self, question):
        """Convert natural language to SQL"""
        with st.spinner("🧠 Converting to SQL..."):
            try:
                if not self.nl2sql_converter:
                    schema_context = self.format_schema_for_claude()
                    self.nl2sql_converter = NL2SQLConverter(schema_context=schema_context)
                
                result = self.nl2sql_converter.generate_sql(question)
                
                if result['success']:
                    st.session_state.converted_sql = result['sql']
                    st.success("✅ SQL generated successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Conversion failed: {result['error']}")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    def execute_query(self, sql):
        """Execute SQL query"""
        with st.spinner("⚡ Executing query..."):
            try:
                start_time = datetime.now()
                result = asyncio.run(execute_query_via_mcp(sql))
                end_time = datetime.now()
                
                execution_time = (end_time - start_time).total_seconds() * 1000
                
                # Store results
                st.session_state.last_query_result = result
                st.session_state.last_executed_sql = sql
                st.session_state.last_execution_time = execution_time
                st.session_state.engine_time_data = None  # Reset engine time
                st.session_state.show_visualizations = False  # Reset visualizations
                st.session_state.selected_chart_type = None  # Reset chart selection
                
                st.success(f"✅ Query executed! {len(result) if result else 0} rows returned")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Query failed: {str(e)}")
    
    def render_results(self):
        """Render query results"""
        if st.session_state.last_query_result is None:
            return
            
        st.markdown("""
        <div class="results-container">
            <h2 class="results-title">📊 Query Results</h2>
        </div>
        """, unsafe_allow_html=True)
        
        result = st.session_state.last_query_result
        
        if result and len(result) > 0:
            df = pd.DataFrame(result)
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{len(df)}</div>
                    <div class="metric-label">Rows Returned</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{len(df.columns)}</div>
                    <div class="metric-label">Columns</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                response_time = st.session_state.last_execution_time
                
                # Check if engine time data is available
                if st.session_state.engine_time_data:
                    # Show Firebolt engine time details
                    data = st.session_state.engine_time_data
                    st.markdown(f"""
                    <div class="metric-card" style="padding: 2rem 1.5rem;">
                        <div class="metric-number" style="font-size: 2.5rem; color: #48bb78;">{data['duration_ms']:.1f}ms</div>
                        <div class="metric-label" style="color: #48bb78;">🔥 Firebolt Engine Time</div>
                        <div style="font-size: 0.9rem; color: #718096; margin-top: 0.5rem;">
                            Database execution: {data['duration_us']:,}μs<br>
                            Network overhead: {data['overhead_ms']:.1f}ms
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Show Get Firebolt Engine Time button
                    if st.button("🔥 Get Firebolt Engine Time", type="secondary", key="engine_time_button", use_container_width=True):
                        self.fetch_engine_time()
            
            # Data table
            st.markdown("### 📋 Data")
            st.dataframe(df, use_container_width=True, height=400)
            
            # Add visualization button
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
            if len(df) > 1 and len(df.columns) >= 2:
                st.markdown("### 📈 Data Visualization")
                if st.button("📊 Visualize This Data", type="primary", key="viz_button"):
                    st.session_state.show_visualizations = True
                
                # Show visualizations if button was clicked
                if st.session_state.get('show_visualizations', False):
                    st.markdown("#### 📊 Create Visualization")
                    
                    # Simple column selection and chart type interface
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # X-axis column selection - smart defaults
                        all_columns = df.columns.tolist()
                        
                        # For pie charts, prefer categorical (non-numeric) columns for X-axis
                        if numeric_columns:
                            categorical_columns = [col for col in all_columns if col not in numeric_columns]
                            x_options = categorical_columns + numeric_columns if categorical_columns else all_columns
                        else:
                            x_options = all_columns
                        
                        x_column = st.selectbox(
                            "📍 X-axis (Categories/Time):",
                            options=x_options,
                            key="viz_x_col"
                        )
                    
                    with col2:
                        # Y-axis column selection - prefer numeric columns first
                        if numeric_columns:
                            y_options = numeric_columns + [col for col in df.columns if col not in numeric_columns]
                        else:
                            y_options = df.columns.tolist()
                        
                        y_column = st.selectbox(
                            "📊 Y-axis (Values):",
                            options=y_options,
                            key="viz_y_col"
                        )
                    
                    # Chart type selection with smart default
                    chart_col1, chart_col2, chart_col3, chart_col4 = st.columns(4)
                    
                    # Smart default suggestion
                    x_unique_count = df[x_column].nunique()
                    total_rows = len(df)
                    is_time_like = any(keyword in str(x_column).lower() for keyword in ['time', 'date', 'hour', 'day', 'month', 'year'])
                    
                    # Suggest chart type based on data
                    if is_time_like:
                        suggested_chart = "Line Chart (Time Series)"
                        default_chart = "line"
                    elif x_unique_count <= 6 and len(df) >= x_unique_count:
                        suggested_chart = "Pie Chart (Distribution)"
                        default_chart = "pie"
                    elif x_unique_count <= 15:
                        suggested_chart = "Bar Chart (Categories)"
                        default_chart = "bar"
                    else:
                        suggested_chart = "Scatter Plot (Many Values)"
                        default_chart = "scatter"
                    
                    st.info(f"💡 Suggested: **{suggested_chart}** based on your data")
                    
                    # Show helpful tip for pie charts
                    if default_chart == "pie":
                        st.success("📝 **Pie Chart Tip:** Use categories (like campaign_type) for X-axis and values (like total_budget) for Y-axis")
                    
                    with chart_col1:
                        if st.button("📊 Bar Chart", type="primary" if default_chart == "bar" else "secondary", key="chart_bar"):
                            st.session_state.selected_chart_type = "bar"
                    
                    with chart_col2:
                        if st.button("📈 Line Chart", type="primary" if default_chart == "line" else "secondary", key="chart_line"):
                            st.session_state.selected_chart_type = "line"
                    
                    with chart_col3:
                        if st.button("🥧 Pie Chart", type="primary" if default_chart == "pie" else "secondary", key="chart_pie"):
                            st.session_state.selected_chart_type = "pie"
                    
                    with chart_col4:
                        if st.button("🎯 Scatter Plot", type="primary" if default_chart == "scatter" else "secondary", key="chart_scatter"):
                            st.session_state.selected_chart_type = "scatter"
                    
                    # Create chart based on selection
                    if st.session_state.get('selected_chart_type'):
                        try:
                            chart_type = st.session_state.selected_chart_type
                            
                            if chart_type == "bar":
                                # Sort data for better visualization (largest values first)
                                sorted_df = df.sort_values(by=y_column, ascending=False).head(15)
                                fig = px.bar(sorted_df, x=x_column, y=y_column,
                                           title=f"📊 {y_column} by {x_column}",
                                           color_discrete_sequence=['#667eea'])
                                # Force Y-axis to start at 0 for bar charts
                                fig.update_layout(yaxis=dict(range=[0, None]))
                            elif chart_type == "line":
                                fig = px.line(df, x=x_column, y=y_column,
                                            title=f"📈 {y_column} over {x_column}",
                                            color_discrete_sequence=['#667eea'])
                                # Smart Y-axis for line charts (only for numeric Y-axis)
                                if df[y_column].dtype in ['int64', 'float64']:
                                    y_min = df[y_column].min()
                                    y_max = df[y_column].max()
                                    y_range = y_max - y_min
                                    if y_range > 0 and y_min >= 0 and y_min <= y_range * 0.3:
                                        fig.update_layout(yaxis=dict(range=[0, None]))
                                    elif y_range > 0:
                                        padding = y_range * 0.1
                                        fig.update_layout(yaxis=dict(range=[max(0, y_min - padding), y_max + padding]))
                            elif chart_type == "pie":
                                # Ensure we have valid data for pie chart
                                pie_df = df.groupby(x_column)[y_column].sum().reset_index()
                                # Sort pie chart data (largest slices first)
                                pie_df = pie_df.sort_values(by=y_column, ascending=False)
                                if len(pie_df) > 0:
                                    fig = px.pie(pie_df, names=x_column, values=y_column,
                                               title=f"🥧 {y_column} Distribution by {x_column}",
                                               color_discrete_sequence=px.colors.qualitative.Set3)
                                else:
                                    st.error("❌ No data available for pie chart")
                                    fig = None
                            else:  # scatter
                                fig = px.scatter(df, x=x_column, y=y_column,
                                               title=f"🎯 {y_column} vs {x_column}",
                                               color_discrete_sequence=['#667eea'])
                                # Add padding for scatter plots (only for numeric data)
                                if df[y_column].dtype in ['int64', 'float64']:
                                    y_min = df[y_column].min()
                                    y_max = df[y_column].max()
                                    y_range = y_max - y_min
                                    y_padding = y_range * 0.1 if y_range > 0 else 1
                                    fig.update_layout(yaxis=dict(range=[y_min - y_padding, y_max + y_padding]))
                                
                                # Also handle X-axis for numeric data
                                if df[x_column].dtype in ['int64', 'float64']:
                                    x_min = df[x_column].min()
                                    x_max = df[x_column].max()
                                    x_range = x_max - x_min
                                    x_padding = x_range * 0.1 if x_range > 0 else 1
                                    fig.update_layout(xaxis=dict(range=[x_min - x_padding, x_max + x_padding]))
                            
                            if fig is not None:
                                fig.update_layout(
                                    height=500,
                                    template="plotly_white",
                                    title_font_size=16,
                                    showlegend=False
                                )
                                

                                
                                st.plotly_chart(fig, use_container_width=True)
                            
                        except Exception as e:
                            st.error(f"📊 Unable to create {chart_type} chart: {str(e)}")
                            st.info("💡 Try selecting different columns or chart type")
                    
                    else:
                        # Show data preview when no chart selected
                        st.markdown("#### 📋 Data Preview")
                        st.dataframe(df.head(10), use_container_width=True)
                        st.caption("👆 Select X-axis, Y-axis, and chart type above to create visualization")
            
        else:
            st.info("✅ Query executed successfully but returned no data")
    

    
    def fetch_engine_time(self):
        """Fetch actual engine execution time"""
        with st.spinner("🔍 Fetching Firebolt engine time..."):
            try:
                escaped_sql = st.session_state.last_executed_sql.replace("'", "''")
                time_query = f"""
                SELECT duration_us, query_text, start_time 
                FROM information_schema.engine_user_query_history 
                WHERE query_text = '{escaped_sql}' 
                  AND status = 'ENDED_SUCCESSFULLY'
                ORDER BY start_time DESC
                LIMIT 1
                """
                
                result = asyncio.run(execute_query_via_mcp(time_query))
                
                if result and len(result) > 0:
                    duration_us = result[0].get('duration_us', 0)
                    duration_ms = duration_us / 1000.0
                    total_ms = st.session_state.last_execution_time
                    overhead_ms = max(0, total_ms - duration_ms)
                    efficiency = (duration_ms / total_ms * 100) if total_ms > 0 else 0
                    
                    st.session_state.engine_time_data = {
                        'duration_us': duration_us,
                        'duration_ms': duration_ms,
                        'overhead_ms': overhead_ms,
                        'efficiency': efficiency
                    }
                    
                    st.rerun()
                else:
                    st.warning("⚠️ Engine time not found in query history")
                    
            except Exception as e:
                st.error(f"❌ Failed to fetch engine time: {str(e)}")
    
    def run(self):
        """Main application"""
        self.render_demo_sidebar()
        self.render_header()
        self.render_connection_ui()
        
        if st.session_state.is_connected:
            self.render_schema_info()
            self.render_query_interface()
            
            if st.session_state.last_query_result is not None:
                self.render_results()

def main():
    """Main function"""
    app = FireboltNL2SQLApp()
    app.run()

if __name__ == "__main__":
    main()

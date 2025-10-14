#!/usr/bin/env python3
"""
Enhanced Agentic AI Demo for Firebolt MCP
Multi-step Business Intelligence Agent with Planning Trace
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import asyncio
import json
import time
import os
import sys
from datetime import datetime, timedelta
from PIL import Image
from typing import Dict, List, Any, Optional
import uuid

# Add current directory to path
sys.path.append('/Users/kushagrnagpal/mcp-nl2sql')
from nl2sql_claude import NL2SQLConverter
from test_mcp_real import execute_query_via_mcp

# Enhanced page config for agent demo
st.set_page_config(
    page_title="🤖 Agentic AI Business Intelligence Demo",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AgentStep:
    """Represents a step in the agent's reasoning process"""
    def __init__(self, step_type: str, description: str, status: str = "pending"):
        self.id = str(uuid.uuid4())
        self.step_type = step_type  # discovery, analysis, hypothesis, validation, conclusion
        self.description = description
        self.status = status  # pending, in_progress, completed, failed
        self.timestamp = datetime.now()
        self.sql_query = None
        self.results = None
        self.insights = []
        self.confidence = 0.0

class BusinessIntelligenceAgent:
    """Enhanced AI agent that performs multi-step business analysis"""
    
    def __init__(self, nl2sql_converter: NL2SQLConverter):
        self.nl2sql_converter = nl2sql_converter
        self.planning_steps = []
        self.execution_log = []
        self.final_insights = []
        
    def create_analysis_plan(self, user_question: str) -> List[AgentStep]:
        """Create a multi-step analysis plan based on the user question"""
        
        question_lower = user_question.lower()
        
        # Store the original question for context
        self.original_question = user_question
        
        # More detailed question analysis
        if any(word in question_lower for word in ["revenue", "money", "monetization", "spending", "income"]):
            return self._create_revenue_analysis_plan(user_question)
        elif any(word in question_lower for word in ["player", "user", "retention", "engagement", "churn"]):
            return self._create_player_analysis_plan(user_question)
        elif any(word in question_lower for word in ["performance", "benchmark", "compete", "market"]):
            return self._create_performance_analysis_plan(user_question)
        elif any(word in question_lower for word in ["geographic", "country", "region", "expansion", "market"]):
            return self._create_geographic_analysis_plan(user_question)
        elif any(word in question_lower for word in ["correlation", "correlate", "relationship", "value"]):
            return self._create_correlation_analysis_plan(user_question)
        else:
            return self._create_general_exploration_plan(user_question)
    
    def _create_revenue_analysis_plan(self, question: str) -> List[AgentStep]:
        """Create analysis plan for revenue-related questions"""
        return [
            AgentStep("discovery", "🔍 Analyzing current revenue trends and patterns"),
            AgentStep("analysis", "📊 Segmenting revenue by player demographics and regions"),
            AgentStep("comparison", "📈 Comparing performance across time periods"),
            AgentStep("hypothesis", "🎯 Identifying top revenue drivers and potential issues"),
            AgentStep("validation", "✅ Validating insights with supporting data"),
            AgentStep("conclusion", "💡 Generating strategic recommendations")
        ]
    
    def _create_player_analysis_plan(self, question: str) -> List[AgentStep]:
        """Create analysis plan for player-related questions"""
        return [
            AgentStep("discovery", "👥 Analyzing player base demographics and behavior"),
            AgentStep("analysis", "🎮 Examining game session patterns and engagement"),
            AgentStep("segmentation", "📊 Segmenting players by value and activity"),
            AgentStep("hypothesis", "🔍 Identifying retention and churn patterns"),
            AgentStep("validation", "📈 Testing hypotheses with cohort analysis"),
            AgentStep("conclusion", "🎯 Recommending player experience improvements")
        ]
    
    def _create_performance_analysis_plan(self, question: str) -> List[AgentStep]:
        """Create analysis plan for performance/benchmark questions"""
        return [
            AgentStep("discovery", "📊 Calculating key performance indicators"),
            AgentStep("benchmarking", "🏆 Comparing against historical baselines"),
            AgentStep("analysis", "🔍 Identifying performance drivers and bottlenecks"),
            AgentStep("forecasting", "📈 Projecting future trends and scenarios"),
            AgentStep("validation", "✅ Validating assumptions with data evidence"),
            AgentStep("conclusion", "🚀 Developing optimization strategies")
        ]
    
    def _create_geographic_analysis_plan(self, question: str) -> List[AgentStep]:
        """Create analysis plan for geographic/market questions"""
        return [
            AgentStep("discovery", "🌍 Mapping current geographic distribution and performance"),
            AgentStep("analysis", "📊 Analyzing market penetration and player behavior by region"),
            AgentStep("comparison", "🔍 Comparing revenue and engagement across markets"),
            AgentStep("opportunity", "🎯 Identifying expansion opportunities and market gaps"),
            AgentStep("validation", "✅ Validating market potential with supporting metrics"),
            AgentStep("conclusion", "🚀 Prioritizing markets for expansion strategy")
        ]
    
    def _create_correlation_analysis_plan(self, question: str) -> List[AgentStep]:
        """Create analysis plan for correlation/relationship questions"""
        return [
            AgentStep("discovery", "🔍 Identifying key variables and metrics for correlation"),
            AgentStep("measurement", "📏 Measuring baseline metrics and data distributions"),
            AgentStep("correlation", "📊 Calculating correlations and statistical relationships"),
            AgentStep("segmentation", "🎯 Analyzing relationships across different player segments"),
            AgentStep("validation", "✅ Validating statistical significance of relationships"),
            AgentStep("conclusion", "💡 Interpreting correlations for business insights")
        ]

    def _create_general_exploration_plan(self, question: str) -> List[AgentStep]:
        """Create general exploration plan"""
        return [
            AgentStep("discovery", "🗺️ Exploring available data and key metrics"),
            AgentStep("analysis", "📊 Identifying interesting patterns and trends"),
            AgentStep("correlation", "🔗 Finding relationships between variables"),
            AgentStep("insight", "💡 Generating data-driven insights"),
            AgentStep("validation", "✅ Validating findings with additional queries"),
            AgentStep("conclusion", "📋 Summarizing key takeaways")
        ]

    def execute_analysis_plan(self, steps: List[AgentStep]) -> List[Dict[str, Any]]:
        """Execute the analysis plan step by step (simplified for demo)"""
        results = []
        
        for i, step in enumerate(steps):
            step.status = "pending"
            results.append({
                "step_index": i,
                "step": step,
                "simulated": True
            })
                
        return results

    # Query methods removed - using simulated execution for demo

# Enhanced Streamlit App
class AgenticAIDemo:
    def __init__(self):
        self.agent = None
        self.init_session_state()
        
    def init_session_state(self):
        """Initialize enhanced session state for agent demo"""
        
        # Base session state from original app
        if 'is_connected' not in st.session_state:
            st.session_state.is_connected = False
        if 'credentials' not in st.session_state:
            st.session_state.credentials = {}
        if 'schema_info' not in st.session_state:
            st.session_state.schema_info = {}
            
        # Agent-specific session state
        if 'agent_mode' not in st.session_state:
            st.session_state.agent_mode = False
        if 'current_analysis_plan' not in st.session_state:
            st.session_state.current_analysis_plan = []
        if 'agent_execution_log' not in st.session_state:
            st.session_state.agent_execution_log = []
        if 'final_insights' not in st.session_state:
            st.session_state.final_insights = []
        if 'analysis_in_progress' not in st.session_state:
            st.session_state.analysis_in_progress = False
        if 'show_execution_controls' not in st.session_state:
            st.session_state.show_execution_controls = False
        if 'current_step_index' not in st.session_state:
            st.session_state.current_step_index = 0

    def render_enhanced_header(self):
        """Enhanced header for agentic AI demo"""
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   padding: 3rem 2rem; border-radius: 20px; margin-bottom: 2rem; 
                   color: white; box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4); text-align: center;">
            <h1 style="margin: 0; font-size: 3rem; font-weight: 700;">
                🤖 Agentic AI Business Intelligence
            </h1>
            <p style="margin: 1rem 0 0 0; font-size: 1.4rem; opacity: 0.9;">
                Multi-step reasoning • Planning traces • Autonomous insights
            </p>
        </div>
        """, unsafe_allow_html=True)

    def render_agent_sidebar(self):
        """Enhanced sidebar with agent planning trace"""
        
        with st.sidebar:
            st.markdown("## 🧠 Agent Planning Trace")
            
            if st.session_state.current_analysis_plan:
                st.markdown("### 📋 Current Analysis Plan")
                
                for i, step in enumerate(st.session_state.current_analysis_plan):
                    status_icon = {
                        "pending": "⏳",
                        "in_progress": "🔄", 
                        "completed": "✅",
                        "failed": "❌"
                    }.get(step.status, "❓")
                    
                    # Step header
                    st.markdown(f"""
                    **Step {i+1}**: {status_icon} {step.description}
                    """)
                    
                    # Show details if completed
                    if step.status == "completed" and step.insights:
                        with st.expander(f"💡 Insights {i+1}", expanded=False):
                            for insight in step.insights:
                                st.markdown(f"• {insight}")
                            
                            if step.confidence:
                                st.progress(step.confidence)
                                st.caption(f"Confidence: {step.confidence:.1%}")
                    
                    elif step.status == "failed":
                        st.error("Step failed - trying alternative approach")
                
                # Progress indicator
                completed_steps = len([s for s in st.session_state.current_analysis_plan if s.status == "completed"])
                total_steps = len(st.session_state.current_analysis_plan)
                
                if total_steps > 0:
                    progress = completed_steps / total_steps
                    st.markdown("### 📊 Overall Progress")
                    st.progress(progress)
                    st.caption(f"{completed_steps}/{total_steps} steps completed")
            
            else:
                st.info("🤖 Agent is ready to analyze your business questions with multi-step reasoning!")
                
                st.markdown("### 🎯 Agent Capabilities")
                st.markdown("""
                - **🔍 Discovery**: Explore data autonomously
                - **📊 Analysis**: Multi-dimensional breakdowns  
                - **🎯 Hypothesis**: Form and test theories
                - **✅ Validation**: Verify insights with data
                - **💡 Insights**: Generate recommendations
                """)

    def render_agent_query_interface(self):
        """Enhanced query interface for agentic AI"""
        
        if not st.session_state.is_connected:
            st.warning("⚠️ Please connect to Firebolt first using the connection form below")
            return
            
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                   padding: 2.5rem; border-radius: 20px; margin: 2rem 0; color: white; 
                   box-shadow: 0 12px 40px rgba(240, 147, 251, 0.4);">
            <h2 style="margin: 0 0 1rem 0; font-size: 2.5rem; text-align: center;">
                💬 Ask Complex Business Questions
            </h2>
            <p style="text-align: center; margin: 0; font-size: 1.2rem; opacity: 0.9;">
                The AI agent will break down your question into analytical steps
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Demo questions for agentic AI
        agent_demo_questions = [
            "Type your own complex business question...",
            "🚀 What's happening with our gaming revenue and should we be concerned?",
            "🎮 How are different player segments performing and what opportunities exist?", 
            "🌍 Which geographic markets should we prioritize for expansion?",
            "💰 What drives player spending and how can we optimize monetization?",
            "📈 How does player engagement correlate with long-term value?"
        ]
        
        selected_question = st.selectbox(
            "🎯 Choose an intelligent analysis or ask your own:",
            agent_demo_questions,
            key="agent_question_select"
        )
        
        # User input
        if selected_question != "Type your own complex business question...":
            default_question = selected_question.split(" ", 1)[1]  # Remove emoji
        else:
            default_question = ""
            
        user_question = st.text_area(
            "Enter your complex business question:",
            value=default_question,
            height=120,
            placeholder="Example: What's driving our revenue growth and what risks should we watch out for?",
            key="agent_question_input",
            help="💡 Ask multi-faceted business questions that require investigation and analysis"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🧠 Start AI Agent Analysis", type="primary", disabled=not user_question.strip() or st.session_state.analysis_in_progress):
                # Reset previous analysis first
                self.reset_analysis_state()
                self.start_agent_analysis(user_question)
        
        with col2:
            if st.button("🔄 Reset Analysis", type="secondary", disabled=st.session_state.analysis_in_progress):
                self.reset_analysis()

    def start_agent_analysis(self, question: str):
        """Start the agentic AI analysis"""
        
        st.session_state.analysis_in_progress = True
        
        try:
            with st.spinner("🧠 Initializing AI agent..."):
                # Initialize agent (simplified for demo)
                self.agent = BusinessIntelligenceAgent(None)  # Simplified for demo
                
                # Store the question in session state too for UI access
                st.session_state.current_question = question
                
                # Create analysis plan
                st.session_state.current_analysis_plan = self.agent.create_analysis_plan(question)
                
                # Mark first step as in progress
                if st.session_state.current_analysis_plan:
                    st.session_state.current_analysis_plan[0].status = "in_progress"
            
            st.success("🎉 AI Agent Analysis Plan Created!")
            st.info("👆 Check the sidebar to see the agent's planning trace. Click 'Execute Next Step' to proceed through the analysis.")
            
            # Show execution controls
            st.session_state.show_execution_controls = True
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            st.exception(e)  # Show full error for debugging
        finally:
            st.session_state.analysis_in_progress = False
            
        st.rerun()  # Force UI update to show sidebar changes

    def reset_analysis_state(self):
        """Reset analysis state for new query (no UI refresh)"""
        st.session_state.current_analysis_plan = []
        st.session_state.agent_execution_log = []
        st.session_state.final_insights = []
        st.session_state.analysis_in_progress = False
        st.session_state.show_execution_controls = False
        st.session_state.current_step_index = 0
        if 'current_question' in st.session_state:
            del st.session_state.current_question

    def reset_analysis(self):
        """Reset the current analysis (with UI refresh)"""
        self.reset_analysis_state()
        st.rerun()

    def render_step_execution_controls(self):
        """Render controls for step-by-step execution"""
        
        st.markdown("## 🎮 Agent Execution Controls")
        
        current_step_index = st.session_state.current_step_index
        total_steps = len(st.session_state.current_analysis_plan)
        
        # Progress indicator
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.progress(current_step_index / total_steps)
            st.caption(f"Step {current_step_index} of {total_steps}")
        
        with col2:
            if st.button("▶️ Execute Next Step", disabled=current_step_index >= total_steps):
                self.execute_next_step()
        
        with col3:
            if st.button("🚀 Auto-Execute All", disabled=current_step_index >= total_steps):
                self.auto_execute_all_steps()
                
        # Current step info
        if current_step_index < total_steps:
            current_step = st.session_state.current_analysis_plan[current_step_index]
            
            st.markdown(f"### 🔄 Next Step: {current_step.description}")
            st.markdown(f"**Type:** {current_step.step_type}")
            
            if current_step.status == "in_progress":
                st.info("⏳ This step is ready to execute")
            elif current_step.status == "completed":
                st.success("✅ This step has been completed")
        else:
            st.success("🎉 All analysis steps completed!")

    def execute_next_step(self):
        """Execute the next step in the analysis"""
        
        current_step_index = st.session_state.current_step_index
        
        if current_step_index < len(st.session_state.current_analysis_plan):
            current_step = st.session_state.current_analysis_plan[current_step_index]
            
            with st.spinner(f"🔄 {current_step.description}"):
                # Simulate step execution
                import time
                time.sleep(1)  # Simulate processing time
                
                # Generate simulated insights
                current_step.status = "completed"
                current_step.confidence = 0.85 + (current_step_index * 0.02)  # Increasing confidence
                current_step.insights = self.generate_demo_insights(current_step.step_type, current_step_index)
                
                # Move to next step
                st.session_state.current_step_index += 1
                
                # Mark next step as in progress if it exists
                if st.session_state.current_step_index < len(st.session_state.current_analysis_plan):
                    st.session_state.current_analysis_plan[st.session_state.current_step_index].status = "in_progress"
            
            st.success(f"✅ Completed: {current_step.description}")
            st.rerun()

    def auto_execute_all_steps(self):
        """Auto-execute all remaining steps"""
        
        remaining_steps = len(st.session_state.current_analysis_plan) - st.session_state.current_step_index
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(remaining_steps):
            step_index = st.session_state.current_step_index + i
            current_step = st.session_state.current_analysis_plan[step_index]
            
            status_text.text(f"🔄 {current_step.description}")
            
            # Simulate processing
            import time
            time.sleep(0.5)
            
            # Complete step
            current_step.status = "completed"
            current_step.confidence = 0.85 + (step_index * 0.02)
            current_step.insights = self.generate_demo_insights(current_step.step_type, step_index)
            
            progress_bar.progress((i + 1) / remaining_steps)
        
        st.session_state.current_step_index = len(st.session_state.current_analysis_plan)
        
        status_text.text("🎉 All steps completed!")
        st.success("✅ Agent analysis complete!")
        st.rerun()

    def generate_demo_insights(self, step_type: str, step_index: int) -> List[str]:
        """Generate demo insights customized for the question type and step"""
        
        # Determine the analysis type from the current question
        if hasattr(self.agent, 'original_question'):
            question_lower = self.agent.original_question.lower()
        elif 'current_question' in st.session_state:
            question_lower = st.session_state.current_question.lower()
        else:
            question_lower = "general"
            
        # Customize insights based on question type and step type
        if any(word in question_lower for word in ["revenue", "money", "monetization"]):
            return self._get_revenue_insights(step_type, step_index)
        elif any(word in question_lower for word in ["player", "retention", "engagement"]):
            return self._get_player_insights(step_type, step_index)
        elif any(word in question_lower for word in ["geographic", "country", "expansion"]):
            return self._get_geographic_insights(step_type, step_index)
        elif any(word in question_lower for word in ["correlation", "correlate", "relationship", "value"]):
            return self._get_correlation_insights(step_type, step_index)
        elif any(word in question_lower for word in ["performance", "benchmark"]):
            return self._get_performance_insights(step_type, step_index)
        else:
            return self._get_general_insights(step_type, step_index)
    
    def _get_revenue_insights(self, step_type: str, step_index: int) -> List[str]:
        """Revenue-focused insights"""
        insights_map = {
            "discovery": [
                "💰 Total revenue: $3.2M with 22% month-over-month growth",
                "🎮 Revenue per player: $64 average, $180 for premium users",
                "📊 Revenue streams: 65% in-app purchases, 35% subscriptions"
            ],
            "analysis": [
                "🏆 Premium players drive 78% of total revenue",
                "🌍 Top revenue markets: US ($1.2M), Germany ($480K), Japan ($380K)",
                "📈 Mobile IAP conversion rate: 12.5% vs desktop 8.3%"
            ],
            "comparison": [
                "📊 Q3 revenue growth: +28% vs Q2, exceeding 15% target",
                "💸 ARPU increased 18% after pricing optimization",
                "🎯 Revenue concentration: Top 5% users generate 45% revenue"
            ],
            "conclusion": [
                "🚀 Prioritize premium feature development for high-LTV segments",
                "💡 Optimize mobile payment flows for higher conversion",
                "📈 Expected revenue impact: +25% with recommended changes"
            ]
        }
        return insights_map.get(step_type, [f"💰 Revenue analysis: {step_type} completed"])
    
    def _get_player_insights(self, step_type: str, step_index: int) -> List[str]:
        """Player engagement and retention insights"""
        insights_map = {
            "discovery": [
                "👥 Active player base: 125K daily, 480K monthly users",
                "📊 Retention rates: Day 1 (45%), Day 7 (23%), Day 30 (12%)",
                "🎮 Average session: 18 minutes, 3.2 sessions per day"
            ],
            "analysis": [
                "🎯 High-engagement players: 15% of base, 4+ hours daily",
                "📱 Mobile players show 35% higher retention than desktop",
                "🏆 Level progression strongly predicts long-term retention"
            ],
            "segmentation": [
                "👑 Power users: 8% of players, 60+ min daily, 85% retention",
                "🎮 Core players: 25% of players, 20-60 min daily, 45% retention",
                "🎯 Casual players: 67% of players, <20 min daily, 15% retention"
            ],
            "conclusion": [
                "⚡ Focus onboarding improvements for casual player conversion",
                "🎮 Enhance social features to boost core player engagement",
                "📈 Projected retention lift: +40% with targeted interventions"
            ]
        }
        return insights_map.get(step_type, [f"👥 Player analysis: {step_type} completed"])
    
    def _get_geographic_insights(self, step_type: str, step_index: int) -> List[str]:
        """Geographic and market expansion insights"""
        insights_map = {
            "discovery": [
                "🌍 Current presence: 28 countries across 5 regions",
                "📊 Regional distribution: NA (45%), EU (30%), APAC (20%), Others (5%)",
                "💰 Revenue per region: NA leads with $1.8M, EU $950K, APAC $420K"
            ],
            "analysis": [
                "🇺🇸 US market: Mature, high ARPU ($85), competitive landscape",
                "🇩🇪 Germany: Growing fast (+45% QoQ), strong retention rates",
                "🇯🇵 Japan: Untapped potential, cultural adaptation needed"
            ],
            "opportunity": [
                "🎯 High-potential markets: Brazil, India, Southeast Asia",
                "💡 Expansion readiness: Localization for 3 new languages identified",
                "📈 Market size estimates: $2.5M additional revenue potential"
            ],
            "conclusion": [
                "🚀 Immediate expansion: Brazil and India within Q1",
                "🌟 Localization priorities: Portuguese, Hindi, Thai",
                "💰 Expected ROI: 280% over 18 months for expansion investment"
            ]
        }
        return insights_map.get(step_type, [f"🌍 Geographic analysis: {step_type} completed"])
    
    def _get_correlation_insights(self, step_type: str, step_index: int) -> List[str]:
        """Correlation and relationship insights"""
        insights_map = {
            "discovery": [
                "🔍 Key variables identified: engagement time, spending, social activity",
                "📊 Data quality: 95% complete records across 480K players",
                "📈 Measurement period: 90 days of player behavior data"
            ],
            "correlation": [
                "📊 Engagement ↔ LTV correlation: 0.78 (strong positive)",
                "💰 Social activity ↔ spending: 0.65 (moderate positive)",
                "🎮 Session frequency ↔ retention: 0.72 (strong positive)"
            ],
            "segmentation": [
                "👑 High-LTV players: 3x more social interactions, 2.5x longer sessions",
                "🎯 Premium subscribers: 85% have >10 friends, vs 35% for free users",
                "📱 Mobile users show stronger engagement-spending correlation (0.82 vs 0.71)"
            ],
            "conclusion": [
                "💡 Social features are strongest predictor of player value",
                "🎮 Engagement optimization can drive 45% LTV increase",
                "🚀 Recommend: Social onboarding flow for new players"
            ]
        }
        return insights_map.get(step_type, [f"🔗 Correlation analysis: {step_type} completed"])
    
    def _get_performance_insights(self, step_type: str, step_index: int) -> List[str]:
        """Performance and benchmarking insights"""
        insights_map = {
            "discovery": [
                "📊 Current KPIs: DAU 125K, Revenue $3.2M/month, Retention 23% D7",
                "🎯 Industry benchmarks: DAU growth +15%, Revenue growth +20%",
                "⚡ Performance gaps: Retention below industry average (30% D7)"
            ],
            "benchmarking": [
                "🏆 Above benchmark: Revenue per user (+25% vs industry)",
                "📈 Meeting benchmark: User acquisition cost (industry average)",
                "⚠️ Below benchmark: Retention rates (-23% vs top performers)"
            ],
            "forecasting": [
                "📊 Revenue projection: $4.1M by Q4 with current trends",
                "🎯 User growth forecast: 180K DAU by year-end",
                "⚡ Optimization potential: +30% revenue with retention fixes"
            ],
            "conclusion": [
                "🚀 Priority focus: Retention optimization programs",
                "💰 Revenue optimization: Already outperforming market",
                "📈 Target: Reach top quartile retention within 6 months"
            ]
        }
        return insights_map.get(step_type, [f"📊 Performance analysis: {step_type} completed"])
    
    def _get_general_insights(self, step_type: str, step_index: int) -> List[str]:
        """General exploration insights"""
        insights_map = {
            "discovery": [
                "🎮 Dataset overview: 480K players, 28 countries, 90 days data",
                "📊 Key metrics identified: engagement, revenue, retention",
                "🔍 Data quality: High completeness, ready for analysis"
            ],
            "analysis": [
                "📈 Growth trends: Steady user acquisition, increasing engagement",
                "💰 Revenue patterns: Strong weekend spikes, mobile preference",
                "🎯 User segments: Clear differentiation by engagement level"
            ],
            "conclusion": [
                "💡 Multiple optimization opportunities identified",
                "🚀 Data-driven insights ready for strategic planning",
                "📊 Comprehensive analysis completed successfully"
            ]
        }
        return insights_map.get(step_type, [f"✅ {step_type.title()} analysis completed"])

    def format_schema_for_claude(self):
        """Format schema context (simplified version)"""
        return """
        Gaming Analytics Database Schema:
        
        Tables:
        - players: Player demographics and activity data
        - games: Game sessions and performance metrics  
        - transactions: Player purchases and revenue data
        - player_events: Detailed behavioral event tracking
        - leaderboards: Competition rankings and scores
        
        Key relationships: All tables connect via player_id
        """

    def render_connection_ui(self):
        """Simplified connection UI for demo"""
        if not st.session_state.is_connected:
            st.markdown("### 🔌 Connect to Firebolt")
            st.info("For this demo, we'll simulate a connection to showcase agentic AI capabilities")
            
            if st.button("🚀 Connect Demo Database", type="primary"):
                # Simulate connection for demo
                st.session_state.is_connected = True
                st.session_state.credentials = {"database": "gaming_demo", "engine": "ai_demo_engine"}
                st.success("✅ Connected to demo environment!")
                st.rerun()
        else:
            st.success("✅ Connected to Firebolt Gaming Analytics Database")
            if st.button("🔄 Disconnect"):
                st.session_state.is_connected = False
                st.rerun()

    def run_demo(self):
        """Main demo application"""
        self.render_enhanced_header()
        self.render_agent_sidebar()
        self.render_connection_ui()
        
        if st.session_state.is_connected:
            self.render_agent_query_interface()
            
            # Show step execution controls if analysis plan exists
            if st.session_state.show_execution_controls and st.session_state.current_analysis_plan:
                self.render_step_execution_controls()
            
            # Show final insights if analysis is complete
            if st.session_state.current_analysis_plan and not st.session_state.analysis_in_progress:
                completed_steps = [s for s in st.session_state.current_analysis_plan if s.status == "completed"]
                if completed_steps:
                    self.render_analysis_results(completed_steps)

    def render_analysis_results(self, completed_steps: List[AgentStep]):
        """Render the final analysis results"""
        
        st.markdown("## 📊 AI Agent Analysis Results")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📋 Executive Summary", "📊 Detailed Findings", "🤖 Agent Reasoning"])
        
        with tab1:
            st.markdown("### 💡 Key Insights")
            all_insights = []
            for step in completed_steps:
                all_insights.extend(step.insights)
            
            for insight in all_insights[:10]:  # Top 10 insights
                st.markdown(f"• {insight}")
        
        with tab2:
            st.markdown("### 📈 Data Analysis")
            for i, step in enumerate(completed_steps):
                if step.results:
                    st.markdown(f"#### Step {i+1}: {step.description}")
                    
                    # Display data as DataFrame
                    df = pd.DataFrame(step.results)
                    st.dataframe(df, use_container_width=True)
                    
                    # Simple visualization
                    if len(df) > 1 and len(df.columns) >= 2:
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        if len(numeric_cols) >= 1:
                            fig = px.bar(df.head(10), x=df.columns[0], y=numeric_cols[0])
                            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.markdown("### 🧠 Agent Decision Process")
            for i, step in enumerate(completed_steps):
                with st.expander(f"Step {i+1}: {step.description}", expanded=False):
                    st.markdown(f"**Status:** {step.status}")
                    st.markdown(f"**Timestamp:** {step.timestamp}")
                    if step.sql_query:
                        st.code(step.sql_query, language="sql")
                    st.markdown(f"**Confidence:** {step.confidence:.1%}")

def main():
    """Main function for agentic AI demo"""
    demo = AgenticAIDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()

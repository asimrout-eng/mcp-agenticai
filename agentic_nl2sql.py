"""
Enhanced NL2SQL Converter for Agentic AI
Supports multi-step reasoning, business context, and hypothesis formation
"""

import os
import anthropic
from typing import Dict, List, Optional, Tuple
import json
import re
from datetime import datetime

class AgenticNL2SQLConverter:
    """Enhanced NL2SQL converter designed for agentic AI workflows"""
    
    def __init__(self, api_key: Optional[str] = None, schema_context: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.schema_context = schema_context
        
    def generate_analysis_plan(self, business_question: str) -> Dict[str, any]:
        """Generate a multi-step analysis plan for complex business questions"""
        
        prompt = f"""
You are a business intelligence expert. Break down this complex business question into a structured analysis plan.

BUSINESS QUESTION: {business_question}

DATABASE CONTEXT:
{self.schema_context or "Gaming analytics database with players, games, transactions, events data"}

Create a JSON response with this structure:
{{
    "analysis_type": "revenue_analysis|player_analysis|performance_analysis|exploratory",
    "complexity": "simple|moderate|complex",
    "steps": [
        {{
            "step_number": 1,
            "step_type": "discovery|analysis|comparison|hypothesis|validation|conclusion",
            "description": "What this step accomplishes",
            "business_value": "Why this step matters for business decisions",
            "query_focus": "What data to query",
            "expected_insights": ["List of potential insights"]
        }}
    ],
    "success_metrics": ["How to measure if analysis is successful"],
    "business_impact": "Expected business value of this analysis"
}}

Focus on actionable business insights, not just data reporting.
"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0.2,
                system="You are a business intelligence expert who creates structured analysis plans. Always respond with valid JSON only.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            return self._parse_json_response(content)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis plan generation failed: {str(e)}",
                "fallback_plan": self._create_fallback_plan(business_question)
            }
    
    def generate_step_query(self, step_description: str, step_type: str, 
                           business_context: str = "", previous_results: List[Dict] = None) -> Dict[str, any]:
        """Generate SQL query for a specific analysis step with business context"""
        
        context_summary = ""
        if previous_results:
            context_summary = f"Previous analysis found: {self._summarize_previous_results(previous_results)}"
        
        prompt = f"""
You are generating SQL for a business intelligence analysis step.

STEP DESCRIPTION: {step_description}
STEP TYPE: {step_type}
BUSINESS CONTEXT: {business_context}
{context_summary}

DATABASE SCHEMA:
{self.schema_context or "Standard gaming analytics schema"}

Generate a SQL query that:
1. Directly addresses this analysis step
2. Provides actionable business insights
3. Uses appropriate aggregations and groupings
4. Considers business KPIs and metrics

Respond with JSON:
{{
    "sql": "SELECT statement with business-focused metrics",
    "explanation": "What business question this query answers",
    "expected_insights": ["List of business insights expected"],
    "confidence": 0.85,
    "business_kpis": ["List of KPIs this query measures"],
    "follow_up_questions": ["Questions this analysis might lead to"]
}}

Focus on business value, not just technical data retrieval.
"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=800,
                temperature=0.1,
                system="You are a business-focused SQL expert. Generate queries that provide actionable insights. Always respond with valid JSON only.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            return self._parse_json_response(content)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Query generation failed: {str(e)}",
                "sql": "SELECT 'Error generating query' as message",
                "explanation": "Fallback query due to generation error"
            }
    
    def analyze_query_results(self, query_results: List[Dict], step_context: str, 
                             business_question: str) -> Dict[str, any]:
        """Analyze query results and generate business insights"""
        
        # Summarize the data for analysis
        data_summary = self._create_data_summary(query_results)
        
        prompt = f"""
You are a business analyst interpreting data results.

ORIGINAL BUSINESS QUESTION: {business_question}
ANALYSIS STEP: {step_context}

DATA RESULTS SUMMARY:
{data_summary}

Analyze these results and provide:
{{
    "key_insights": ["3-5 most important business insights"],
    "data_patterns": ["Notable patterns or trends observed"],
    "business_implications": ["What this means for business decisions"],
    "confidence_level": 0.85,
    "recommended_actions": ["Specific actions based on findings"],
    "risks_opportunities": ["Risks to watch or opportunities to pursue"],
    "next_analysis_steps": ["What to investigate next"]
}}

Focus on actionable business intelligence, not just data description.
"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.2,
                system="You are a business analyst who turns data into actionable insights. Always respond with valid JSON only.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            return self._parse_json_response(content)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Results analysis failed: {str(e)}",
                "key_insights": ["Analysis engine encountered an error"],
                "confidence_level": 0.0
            }
    
    def synthesize_final_recommendations(self, all_step_results: List[Dict], 
                                       original_question: str) -> Dict[str, any]:
        """Synthesize insights from all analysis steps into final recommendations"""
        
        # Compile all insights
        all_insights = []
        all_actions = []
        
        for result in all_step_results:
            if result.get('insights'):
                all_insights.extend(result['insights'])
            if result.get('recommended_actions'):
                all_actions.extend(result['recommended_actions'])
        
        insights_summary = "\n".join([f"• {insight}" for insight in all_insights[:15]])
        actions_summary = "\n".join([f"• {action}" for action in all_actions[:10]])
        
        prompt = f"""
You are a senior business strategist synthesizing analysis findings.

ORIGINAL QUESTION: {original_question}

KEY INSIGHTS FROM ANALYSIS:
{insights_summary}

RECOMMENDED ACTIONS IDENTIFIED:
{actions_summary}

Create a comprehensive business recommendation:
{{
    "executive_summary": "2-3 sentence summary of key findings",
    "strategic_recommendations": ["3-5 high-impact strategic actions"],
    "immediate_actions": ["2-3 actions to take in next 30 days"], 
    "performance_metrics": ["KPIs to track success"],
    "risk_mitigation": ["Key risks and how to address them"],
    "investment_priorities": ["Where to focus resources"],
    "timeline": "Recommended implementation timeline",
    "expected_business_impact": "Quantified expected impact",
    "confidence_level": 0.88
}}

Focus on strategic value and measurable business outcomes.
"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1200,
                temperature=0.15,
                system="You are a senior business strategist providing executive-level recommendations. Always respond with valid JSON only.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            return self._parse_json_response(content)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Synthesis failed: {str(e)}",
                "executive_summary": "Unable to generate final recommendations due to processing error"
            }
    
    def _parse_json_response(self, content: str) -> Dict[str, any]:
        """Parse JSON response with error handling"""
        try:
            # Clean up markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
            
            return json.loads(content)
            
        except json.JSONDecodeError:
            # Try to extract JSON manually
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(content[start:end])
                except:
                    pass
            
            return {
                "success": False,
                "error": "Failed to parse JSON response",
                "raw_content": content[:500]
            }
    
    def _create_fallback_plan(self, question: str) -> List[Dict]:
        """Create a simple fallback analysis plan"""
        return [
            {
                "step_number": 1,
                "step_type": "discovery",
                "description": "Explore available data and key metrics",
                "query_focus": "Basic data overview"
            },
            {
                "step_number": 2,
                "step_type": "analysis", 
                "description": "Analyze main business dimensions",
                "query_focus": "Segmented analysis"
            },
            {
                "step_number": 3,
                "step_type": "conclusion",
                "description": "Summarize findings and insights",
                "query_focus": "Key takeaways"
            }
        ]
    
    def _summarize_previous_results(self, results: List[Dict]) -> str:
        """Create a brief summary of previous analysis results"""
        if not results or len(results) == 0:
            return "No previous results available"
        
        summary_points = []
        
        for result in results[-3:]:  # Last 3 results
            if result.get('key_insights'):
                summary_points.append(f"Found: {result['key_insights'][0]}")
        
        return "; ".join(summary_points)
    
    def _create_data_summary(self, query_results: List[Dict]) -> str:
        """Create a summary of query results for analysis"""
        if not query_results:
            return "No data returned"
        
        summary = f"Dataset contains {len(query_results)} records"
        
        if len(query_results) > 0:
            sample = query_results[0]
            columns = list(sample.keys())
            summary += f" with columns: {', '.join(columns[:5])}"
            
            # Add basic statistics for numeric columns
            numeric_cols = []
            for col in columns:
                try:
                    values = [float(r.get(col, 0)) for r in query_results[:10]]
                    if any(v != 0 for v in values):
                        numeric_cols.append(col)
                except:
                    continue
            
            if numeric_cols:
                summary += f". Numeric metrics: {', '.join(numeric_cols[:3])}"
        
        return summary


# Demo usage and test functions
def test_agentic_converter():
    """Test the agentic NL2SQL converter"""
    
    print("🧠 Testing Agentic NL2SQL Converter")
    print("=" * 50)
    
    # Mock schema context
    schema_context = """
    Gaming Analytics Database:
    - players: player demographics and activity
    - games: game sessions and performance
    - transactions: revenue and purchases
    - player_events: behavioral tracking
    """
    
    converter = AgenticNL2SQLConverter(schema_context=schema_context)
    
    # Test complex business question
    business_question = "What's driving our revenue growth and what risks should we watch out for?"
    
    print(f"📝 Business Question: {business_question}")
    print()
    
    # Generate analysis plan
    print("🎯 Generating Analysis Plan...")
    plan = converter.generate_analysis_plan(business_question)
    
    if plan.get('success', True):
        print(f"✅ Analysis Type: {plan.get('analysis_type', 'Unknown')}")
        print(f"📊 Complexity: {plan.get('complexity', 'Unknown')}")
        print(f"🎯 Business Impact: {plan.get('business_impact', 'Not specified')}")
        
        print("\n📋 Analysis Steps:")
        for step in plan.get('steps', []):
            print(f"  {step.get('step_number', '?')}. {step.get('description', 'No description')}")
            print(f"     💼 Business Value: {step.get('business_value', 'Not specified')}")
    else:
        print(f"❌ Plan generation failed: {plan.get('error', 'Unknown error')}")
    
    print("=" * 50)

if __name__ == "__main__":
    test_agentic_converter()

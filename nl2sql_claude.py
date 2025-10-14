"""
Natural Language to SQL Converter using Claude (Anthropic)
Specifically designed for AdTech analytics on the ad_performance table
"""

import os
import anthropic
from typing import Dict, List, Optional
import json
import re


class NL2SQLConverter:
    """Convert natural language questions to SQL queries for AdTech data"""
    
    def __init__(self, api_key: Optional[str] = None, schema_context: Optional[str] = None):
        """Initialize the NL2SQL converter with Claude API key and optional schema context"""
        # Try multiple sources for API key (no hardcoded fallback)
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided via environment variable or api_key parameter")
        
        # Initialize Claude client
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except Exception as e:
            print(f"Error initializing Claude client: {e}")
            raise
        
        # Dynamic schema context (from user's database)
        self.schema_context = schema_context
        
        # Default AdTech table schema for fallback
        self.table_schema = {
            "table_name": "ad_performance",
            "description": "AdTech performance data with events, financials, and campaign attributes",
            "columns": {
                # Primary Keys & IDs
                "event_id": "BIGINT - Unique event identifier",
                "campaign_id": "INTEGER - Campaign identifier", 
                "ad_id": "INTEGER - Ad identifier",
                
                # Time Dimensions
                "event_timestamp": "TIMESTAMP - Exact time of event",
                "event_date": "DATE - Date of event (partitioned)",
                "hour_of_day": "INTEGER - Hour of day (0-23)",
                
                # Event Data
                "event_type": "TEXT - Type of event (impression, click, conversion)",
                
                # Financial Metrics
                "bid_amount": "DECIMAL(15,4) - Bid amount in currency",
                "cost": "DECIMAL(15,4) - Actual cost paid",
                "revenue": "DECIMAL(15,4) - Revenue generated",
                
                # Campaign Attributes (denormalized)
                "campaign_name": "TEXT - Name of the campaign",
                "campaign_type": "TEXT - Type of campaign",
                "advertiser_name": "TEXT - Name of advertiser",
                "industry_vertical": "TEXT - Industry vertical",
                
                # Publisher Attributes (denormalized)
                "publisher_name": "TEXT - Name of publisher",
                "publisher_category": "TEXT - Category of publisher",
                "publisher_tier": "TEXT - Tier of publisher",
                
                # User/Device Context
                "device_type": "TEXT - Device type (mobile, desktop, tablet)",
                "browser": "TEXT - Browser used",
                "os": "TEXT - Operating system",
                
                # Geographic Data
                "country": "TEXT - Country code",
                "region": "TEXT - Region/state",
                "city": "TEXT - City name"
            },
            "sample_data": {
                "total_rows": "1,000,000 rows",
                "date_range": "Recent AdTech performance data",
                "common_values": {
                    "event_type": ["impression", "click", "conversion"],
                    "device_type": ["mobile", "desktop", "tablet"],
                    "countries": ["US", "GB", "DE", "FR", "CA", "AU", "BR", "JP"],
                    "campaign_types": ["display", "search", "social", "video"]
                }
            }
        }
        
        # Firebolt-specific AdTech analysis patterns
        self.example_queries = [
            {
                "question": "How many total events do we have?",
                "sql": "SELECT COUNT(*) as total_events FROM ad_performance"
            },
            {
                "question": "What's the revenue by device type for conversions?",
                "sql": "SELECT device_type, SUM(revenue) as total_revenue FROM ad_performance WHERE event_type = 'conversion' GROUP BY device_type ORDER BY total_revenue DESC"
            },
            {
                "question": "Show me the top countries by number of events",
                "sql": "SELECT country, COUNT(*) as events FROM ad_performance GROUP BY country ORDER BY events DESC LIMIT 10"
            },
            {
                "question": "What's the cost per click by campaign?",
                "sql": "SELECT campaign_name, SUM(cost) / NULLIF(COUNT(CASE WHEN event_type = 'click' THEN 1 END), 0) as cost_per_click FROM ad_performance GROUP BY campaign_name HAVING COUNT(CASE WHEN event_type = 'click' THEN 1 END) > 0 ORDER BY cost_per_click"
            },
            {
                "question": "Show daily revenue trends for last 7 days",
                "sql": "SELECT event_date, SUM(revenue) as daily_revenue FROM ad_performance WHERE event_type = 'conversion' AND event_date >= CURRENT_DATE - INTERVAL '7' DAY GROUP BY event_date ORDER BY event_date"
            }
        ]
    
    def update_schema_context(self, schema_context: str):
        """Update the schema context for the user's connected database"""
        self.schema_context = schema_context
    
    def generate_sql(self, natural_language_query: str) -> Dict[str, any]:
        """
        Convert natural language query to SQL
        
        Args:
            natural_language_query: User's question in natural language
            
        Returns:
            Dictionary with SQL query, explanation, and metadata
        """
        try:
            # Construct the prompt for OpenAI
            prompt = self._build_prompt(natural_language_query)
            
            # Call Claude API with parameters optimized for complex queries
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,  # Increased for complex business queries
                temperature=0.1,  # Slight creativity for complex queries
                system="You are a Firebolt SQL expert specializing in business analytics. Generate valid Firebolt SQL with proper JOINs and aggregations. Always respond with valid JSON only.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse the response
            response_content = response.content[0].text.strip()
            return self._parse_claude_response(response_content, natural_language_query)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Claude API error: {str(e)}",
                "sql": None,
                "explanation": None,
                "confidence": 0
            }
    
    def _build_prompt(self, user_question: str) -> str:
        """Build the prompt for Claude with schema and examples"""
        
        # Use dynamic schema if available, otherwise use default
        if self.schema_context:
            schema_text = self.schema_context
        else:
            schema_text = self._format_default_schema()
            
        # Get first table name for example (or default to ad_performance)
        first_table = "your_table"
        if self.schema_context and "##" in self.schema_context:
            # Try to extract first table name from schema context
            lines = self.schema_context.split('\n')
            for line in lines:
                if line.startswith('## ') and '(' in line:
                    first_table = line.split('## ')[1].split(' (')[0].strip()
                    break
        elif not self.schema_context:
            first_table = "ad_performance"
        
        prompt = f"""
You are a Firebolt SQL expert. Convert this natural language question into a SQL query using the provided database schema.

DATABASE SCHEMA:
{schema_text}

RULES:
- Use only tables/columns from the schema above
- Generate valid Firebolt SQL syntax
- Use appropriate JOINs for multi-table queries
- Always start with SELECT

USER QUESTION: {user_question}

CRITICAL: Respond with ONLY valid JSON format. Follow these rules strictly:
- Keep explanations SHORT (under 100 characters)
- Use \\n for newlines in SQL, not actual newlines
- Escape any quotes in strings with \\"
- No line breaks within the JSON structure

Use this EXACT format:
{{"sql": "SELECT columns FROM tables WHERE conditions", "explanation": "Brief description", "confidence": 0.95}}"""
        return prompt
    
    def _format_default_schema(self) -> str:
        """Format the default table schema for the prompt"""
        schema_lines = [f"Table: {self.table_schema['table_name']}"]
        schema_lines.append(f"Description: {self.table_schema['description']}")
        schema_lines.append("Columns:")
        
        for col_name, col_desc in self.table_schema['columns'].items():
            schema_lines.append(f"  - {col_name}: {col_desc}")
        
        return "\n".join(schema_lines)
    
    def _format_examples(self) -> str:
        """Format example queries for the prompt"""
        examples = []
        for i, example in enumerate(self.example_queries, 1):
            examples.append(f"{i}. Q: {example['question']}")
            examples.append(f"   A: {example['sql']}")
        
        return "\n".join(examples)
    
    def _parse_claude_response(self, response_content: str, original_question: str) -> Dict[str, any]:
        """Parse Claude response with robust JSON parsing for complex queries"""
        try:
            # Clean response content
            content = response_content.strip()
            
            # Remove any markdown code blocks if present
            if content.startswith("```"):
                lines = content.split('\n')
                content = '\n'.join(lines[1:-1]) if len(lines) > 2 else content
                content = content.strip()
            
            # Ensure we have JSON format
            if not content.startswith("{"):
                # Find JSON in response
                start = content.find("{")
                if start != -1:
                    end = content.rfind("}") + 1
                    content = content[start:end]
                else:
                    raise ValueError("No JSON found in response")
            
            # Parse JSON with multiple fallback strategies
            parsed = None
            
            # Strategy 1: Direct JSON parsing
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError as json_error:
                
                # Strategy 2: Fix common escaping issues
                try:
                    # Escape unescaped quotes and newlines more carefully
                    fixed_content = content
                    # Fix newlines in strings
                    fixed_content = re.sub(r'(?<!\\)\n', '\\n', fixed_content)
                    # Fix unescaped quotes in values (but not structure quotes)
                    fixed_content = re.sub(r':\s*"([^"]*)"([^"]*)"([^"]*)"', r': "\1\\\"\2\\\"\3"', fixed_content)
                    parsed = json.loads(fixed_content)
                except json.JSONDecodeError:
                    
                    # Strategy 3: Extract fields manually with improved regex
                    sql_pattern = r'"sql"\s*:\s*"((?:[^"\\]|\\.)*)(?:"(?:\s*,|\s*}))'
                    explanation_pattern = r'"explanation"\s*:\s*"((?:[^"\\]|\\.)*)(?:"(?:\s*,|\s*}))'
                    confidence_pattern = r'"confidence"\s*:\s*([0-9.]+)'
                    
                    sql_match = re.search(sql_pattern, content, re.DOTALL)
                    explanation_match = re.search(explanation_pattern, content, re.DOTALL)
                    confidence_match = re.search(confidence_pattern, content)
                    
                    if sql_match:
                        # Unescape the extracted SQL
                        sql_text = sql_match.group(1)
                        sql_text = sql_text.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
                        
                        explanation_text = "SQL query generated for complex business analysis"
                        if explanation_match:
                            explanation_text = explanation_match.group(1)
                            explanation_text = explanation_text.replace('\\"', '"').replace('\\n', ' ').replace('\\t', ' ')
                        
                        confidence_val = 0.8
                        if confidence_match:
                            try:
                                confidence_val = float(confidence_match.group(1))
                            except ValueError:
                                pass
                        
                        parsed = {
                            "sql": sql_text,
                            "explanation": explanation_text,
                            "confidence": confidence_val
                        }
                    else:
                        # Strategy 4: Look for any SQL-like content as fallback
                        sql_patterns = [
                            r'SELECT\s+.*?(?:FROM|$)',
                            r'WITH\s+.*?SELECT\s+.*',
                            r'(?:^|\n)\s*(SELECT[\s\S]*?)(?:\n\n|$|```)',
                        ]
                        
                        for pattern in sql_patterns:
                            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                            if match:
                                parsed = {
                                    "sql": match.group(1).strip() if match.groups() else match.group(0).strip(),
                                    "explanation": "Complex query extracted from response",
                                    "confidence": 0.7
                                }
                                break
                        
                        if not parsed:
                            raise ValueError(f"JSON parsing failed and no SQL found: {str(json_error)[:100]}")
            
            # Validate required fields
            if "sql" not in parsed:
                raise ValueError("Missing 'sql' field in response")
            
            sql_content = parsed["sql"].strip()
            
            # Validate SQL is analytical (read-only operations)
            sql_upper = sql_content.upper().strip()
            
            # Remove leading whitespace and comments
            sql_lines = []
            for line in sql_upper.split('\n'):
                line = line.strip()
                if line and not line.startswith('--') and not line.startswith('/*'):
                    sql_lines.append(line)
            
            if not sql_lines:
                raise ValueError("SQL query is empty or contains only comments")
            
            sql_clean = ' '.join(sql_lines).strip()
            
            # Valid analytical query patterns (read-only operations)
            valid_analytical_patterns = [
                'SELECT',           # Standard queries
                'WITH',             # Common Table Expressions
                'EXPLAIN',          # Query plan analysis
                'DESCRIBE', 'DESC', # Schema information
                'SHOW',             # Metadata queries
                'VALUES',           # Value lists for analysis
                '(SELECT',          # Parenthesized SELECT
                '(WITH'             # Parenthesized CTE
            ]
            
            # Check if SQL starts with any valid pattern (strict matching)
            is_valid_analytical = False
            for pattern in valid_analytical_patterns:
                if (sql_clean.startswith(pattern + ' ') or 
                    sql_clean == pattern or 
                    sql_clean.startswith(pattern + '(')):
                    is_valid_analytical = True
                    break
            
            if not is_valid_analytical:
                raise ValueError(f"SQL must be an analytical query (SELECT, WITH, EXPLAIN, DESCRIBE, SHOW, VALUES). Got: {sql_clean[:50]}...")
            
            # Basic SQL validation (removed hardcoded table requirement)
            if len(sql_content) < 10:
                raise ValueError("SQL query too short")
            
            return {
                "success": True,
                "sql": sql_content,
                "explanation": parsed.get("explanation", "Firebolt SQL query generated"),
                "confidence": parsed.get("confidence", 0.9),
                "assumptions": parsed.get("assumptions", []),
                "original_question": original_question,
                "raw_response": response_content
            }
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # For debugging complex queries, truncate raw response
            debug_response = response_content[:500] + "..." if len(response_content) > 500 else response_content
            
            return {
                "success": False,
                "error": f"Invalid response format: {str(e)}",
                "sql": None,
                "explanation": f"Error parsing response for complex query. Raw response preview: {debug_response[:100]}...",
                "confidence": 0,
                "original_question": original_question,
                "raw_response": debug_response
            }
    
    def _extract_sql_from_text(self, text: str) -> str:
        """Extract SQL query from unstructured text"""
        # First, try to extract from JSON if it's a JSON response
        if '{"sql":' in text or '"sql"' in text:
            try:
                # Find JSON and extract SQL from it
                if "{" in text and "}" in text:
                    start = text.find("{")
                    end = text.rfind("}") + 1
                    json_str = text[start:end]
                    parsed = json.loads(json_str)
                    sql_content = parsed.get("sql", "")
                    if sql_content and sql_content.strip().upper().startswith('SELECT'):
                        return sql_content.strip()
            except:
                pass
        
        # Look for SQL in code blocks
        if "```sql" in text:
            start = text.find("```sql") + 6
            end = text.find("```", start)
            if end != -1:
                return text[start:end].strip()
        
        # Look for SQL starting with SELECT
        lines = text.split('\n')
        sql_lines = []
        in_sql = False
        
        for line in lines:
            line = line.strip()
            if line.upper().startswith('SELECT'):
                in_sql = True
            
            if in_sql:
                sql_lines.append(line)
                if line.endswith(';'):
                    break
        
        return ' '.join(sql_lines) if sql_lines else text.strip()
    
    def validate_sql(self, sql_query: str) -> Dict[str, any]:
        """Basic validation of the generated SQL query"""
        issues = []
        
        # Basic checks
        if not sql_query.strip():
            issues.append("Empty SQL query")
        
        if not sql_query.upper().strip().startswith('SELECT'):
            issues.append("Query should start with SELECT")
        
        # Skip hardcoded table validation - using dynamic schema now
        
        # Check for potential SQL injection patterns
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
        for keyword in dangerous_keywords:
            if keyword in sql_query.upper():
                issues.append(f"Potentially dangerous keyword: {keyword}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "sql": sql_query
        }


def test_nl2sql():
    """Test the NL2SQL converter with sample questions"""
    converter = NL2SQLConverter()
    
    test_questions = [
        "How many total events are there?",
        "What's the revenue by device type?",
        "Show me the top 5 countries by clicks",
        "What's the average cost per click by campaign?",
        "Which advertisers have the highest conversion rates?"
    ]
    
    print("🧠 Testing NL2SQL Converter")
    print("=" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        
        # Generate SQL
        result = converter.generate_sql(question)
        
        if result['success']:
            print(f"✅ SQL: {result['sql']}")
            print(f"📝 Explanation: {result['explanation']}")
            print(f"🎯 Confidence: {result['confidence']:.2%}")
            
            # Validate
            validation = converter.validate_sql(result['sql'])
            if validation['valid']:
                print("✅ Validation: PASSED")
            else:
                print(f"⚠️ Validation issues: {', '.join(validation['issues'])}")
        else:
            print(f"❌ Error: {result['error']}")
        
        print("-" * 50)


if __name__ == "__main__":
    test_nl2sql()

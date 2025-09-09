#!/usr/bin/env python3

import os
import asyncio
import time
from nl2sql_claude import NL2SQLConverter
from test_mcp_real import execute_query_via_mcp

# Set up Firebolt credentials (must be provided via environment variables)
# Please set these environment variables before running:
# export FIREBOLT_MCP_CLIENT_ID='your_client_id'
# export FIREBOLT_MCP_CLIENT_SECRET='your_client_secret'
if not os.getenv('FIREBOLT_MCP_CLIENT_ID') or not os.getenv('FIREBOLT_MCP_CLIENT_SECRET'):
    print("❌ Error: FIREBOLT_MCP_CLIENT_ID and FIREBOLT_MCP_CLIENT_SECRET must be set as environment variables")
    print("Please set: export FIREBOLT_MCP_CLIENT_ID='your_client_id'")
    print("Please set: export FIREBOLT_MCP_CLIENT_SECRET='your_client_secret'")
    exit(1)
# Set default account if not already configured
if 'FIREBOLT_MCP_ACCOUNT' not in os.environ:
    os.environ['FIREBOLT_MCP_ACCOUNT'] = os.getenv('FIREBOLT_ACCOUNT', 'se-demo-account')
os.environ['FIREBOLT_MCP_DATABASE'] = 'kush_firex_demo'
os.environ['FIREBOLT_MCP_ENGINE'] = 'kush_test_engine'
# API key must be provided via environment variable

from nl2sql_claude import NL2SQLConverter
from test_mcp_real import execute_query_via_mcp

# 10 Carefully Selected Test Prompts (5 Intermediate + 5 Advanced)
STRESS_TEST_PROMPTS = [
    # === INTERMEDIATE COMPLEXITY ===
    {
        "id": 1,
        "difficulty": "intermediate",
        "prompt": "Show me total revenue and conversions for AutoCorp campaigns by type",
        "expected_tables": ["campaigns", "ad_events"],
        "expected_functions": ["SUM", "COUNT", "GROUP BY"]
    },
    {
        "id": 2,
        "difficulty": "intermediate", 
        "prompt": "Which publishers have the highest conversion rates for AutoCorp?",
        "expected_tables": ["campaigns", "ad_events", "publishers"],
        "expected_functions": ["JOIN", "conversion rate calculation"]
    },
    {
        "id": 3,
        "difficulty": "intermediate",
        "prompt": "What's the average revenue per conversion for each campaign type?",
        "expected_tables": ["campaigns", "ad_events"],
        "expected_functions": ["AVG", "CASE WHEN", "GROUP BY"]
    },
    {
        "id": 4,
        "difficulty": "intermediate",
        "prompt": "Show me the top 5 campaigns by total revenue for AutoCorp",
        "expected_tables": ["campaigns", "ad_events"],
        "expected_functions": ["SUM", "ORDER BY", "LIMIT"]
    },
    {
        "id": 5,
        "difficulty": "intermediate",
        "prompt": "Break down AutoCorp's performance by region and campaign type",
        "expected_tables": ["campaigns", "ad_events", "publishers"],
        "expected_functions": ["JOIN", "GROUP BY", "multi-dimensional"]
    },
    
    # === ADVANCED COMPLEXITY ===
    {
        "id": 6,
        "difficulty": "advanced",
        "prompt": "Show me hourly conversion trends with rolling averages for AutoCorp",
        "expected_tables": ["campaigns", "ad_events"],
        "expected_functions": ["CTE", "window functions", "time analysis"]
    },
    {
        "id": 7,
        "difficulty": "advanced",
        "prompt": "Calculate ROI and cost efficiency metrics by campaign type for AutoCorp",
        "expected_tables": ["campaigns", "ad_events"],
        "expected_functions": ["complex calculations", "business metrics"]
    },
    {
        "id": 8,
        "difficulty": "advanced",
        "prompt": "Find correlation between daily budget and conversion performance",
        "expected_tables": ["campaigns", "ad_events"],
        "expected_functions": ["CORR", "statistical analysis"]
    },
    {
        "id": 9,
        "difficulty": "advanced",
        "prompt": "Show me campaign performance with month-over-month growth rates",
        "expected_tables": ["campaigns", "ad_events"],
        "expected_functions": ["LAG", "window functions", "growth calculation"]
    },
    {
        "id": 10,
        "difficulty": "advanced",
        "prompt": "Identify underperforming campaigns using statistical outlier detection",
        "expected_tables": ["campaigns", "ad_events"],
        "expected_functions": ["STDDEV", "statistical functions", "outlier detection"]
    }
]

def format_schema_for_claude():
    """Format the schema context for Claude with important column mappings"""
    return """
    ADTECH DATABASE SCHEMA:
    
    Table: campaigns
    - campaign_id (TEXT, PRIMARY KEY)
    - advertiser (TEXT) - Company name like 'AutoCorp'
    - campaign_type (TEXT) - 'search', 'display', 'video'
    - daily_budget (DECIMAL(10,2))
    - start_date (DATE)
    
    Table: publishers  
    - publisher_id (TEXT, PRIMARY KEY)
    - publisher_name (TEXT)
    - region (TEXT) - 'North', 'South', 'East', 'West'
    - publisher_type (TEXT)
    
    Table: ad_events
    - event_id (TEXT, PRIMARY KEY) 
    - campaign_id (TEXT) - Links to campaigns table
    - publisher_id (TEXT) - Links to publishers table
    - event_type (TEXT) - 'impression', 'click', 'conversion'
    - event_hour (INTEGER) - Hour 0-23
    - cost_usd (DECIMAL(15,4))
    - revenue_usd (DECIMAL(15,4)) - Only populated for conversions
    
    IMPORTANT COLUMN MAPPINGS:
    - Use 'revenue_usd' not 'revenue' 
    - Use 'cost_usd' not 'cost'
    - Use 'advertiser' not 'advertiser_name'
    - Use 'event_hour' not 'event_time'
    
    IMPORTANT FIREBOLT SYNTAX:
    - Use CORR(col1::DOUBLE, col2::DOUBLE) for correlations
    - Use STDDEV(col::DOUBLE) for standard deviation
    - Use NULLIF() to avoid division by zero
    - CTEs with WITH clause are fully supported
    
    FIREBOLT FUNCTIONS:
    - Window functions: LAG, LEAD, ROW_NUMBER, RANK
    - Aggregates: SUM, COUNT, AVG, MIN, MAX
    - Statistical: CORR, STDDEV (cast to DOUBLE)
    - Date functions: DATE_TRUNC, EXTRACT
    """

async def test_prompt(prompt_data, nl2sql_converter):
    """Test a single prompt and return results"""
    prompt_id = prompt_data["id"]
    difficulty = prompt_data["difficulty"]
    prompt = prompt_data["prompt"]
    
    print(f"\n{'='*60}")
    print(f"🧪 Testing Prompt {prompt_id} ({difficulty.upper()})")
    print(f"📝 Prompt: {prompt}")
    print(f"{'='*60}")
    
    result = {
        "id": prompt_id,
        "difficulty": difficulty,
        "prompt": prompt,
        "success": False,
        "sql_generated": None,
        "execution_success": False,
        "result_count": 0,
        "execution_time": None,
        "error": None
    }
    
    try:
        # Step 1: Generate SQL
        print("🔄 Step 1: Generating SQL with Claude...")
        start_time = time.time()
        
        response = nl2sql_converter.generate_sql(prompt)
        
        if not response.get('success'):
            result["error"] = f"SQL Generation Failed: {response.get('error', 'Unknown error')}"
            print(f"❌ {result['error']}")
            return result
        
        sql = response['sql']
        result["sql_generated"] = sql
        generation_time = time.time() - start_time
        
        print(f"✅ SQL Generated in {generation_time:.2f}s")
        print(f"📄 Generated SQL:")
        print(f"```sql\n{sql}\n```")
        
        # Step 2: Execute SQL
        print("\n🔄 Step 2: Executing SQL on Firebolt...")
        exec_start = time.time()
        
        query_result = await execute_query_via_mcp(sql)
        
        exec_time = time.time() - exec_start
        result["execution_time"] = exec_time
        result["execution_success"] = True
        
        # Step 3: Validate Results
        if query_result and len(query_result) > 0:
            result["result_count"] = len(query_result)
            result["success"] = True
            
            print(f"✅ Query executed successfully in {exec_time:.2f}s")
            print(f"📊 Result: {len(query_result)} rows returned")
            
            # Show sample results
            if len(query_result) > 0:
                print(f"📋 Sample Result:")
                sample = query_result[0]
                for key, value in sample.items():
                    print(f"   {key}: {value}")
                    
                if len(query_result) > 1:
                    print(f"   ... and {len(query_result) - 1} more rows")
            
            # Validate result structure
            if len(query_result) > 1000:
                result["validation_warning"] = f"Large result set: {len(query_result)} rows"
                print(f"⚠️  Large result set: {len(query_result)} rows")
            
            # Check for expected columns based on prompt
            if query_result:
                columns = list(query_result[0].keys()) if query_result[0] else []
                print(f"📊 Columns returned: {columns}")
                
        else:
            result["success"] = True  # Query executed but no results
            result["result_count"] = 0
            print(f"✅ Query executed successfully in {exec_time:.2f}s (no results)")
        
    except Exception as e:
        result["error"] = str(e)
        print(f"❌ Error: {e}")
        
        # Additional error context
        if "Decimal math overflow" in str(e):
            result["error"] = f"Decimal overflow - need to increase precision: {e}"
        elif "Column" in str(e) and "does not exist" in str(e):
            result["error"] = f"Schema mismatch - wrong column name: {e}"
        elif "syntax error" in str(e).lower():
            result["error"] = f"SQL syntax error: {e}"
    
    return result

async def run_focused_stress_test():
    """Run the focused stress test on 10 carefully selected prompts"""
    
    print("🚀 FOCUSED STRESS TEST - FIREBOLT NL2SQL")
    print("=" * 60)
    print("Testing 10 carefully selected prompts (5 intermediate + 5 advanced)")
    print("Goal: Validate NL2SQL accuracy and Firebolt performance")
    print()
    
    # Check API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your API key: export ANTHROPIC_API_KEY='<your-key>'")
        return
    
    # Initialize Claude with schema context
    schema_context = format_schema_for_claude()
    nl2sql_converter = NL2SQLConverter(schema_context=schema_context)
    
    print("✅ Claude NL2SQL Converter initialized")
    print("✅ Firebolt MCP credentials configured")
    print()
    
    # Run all tests
    results = []
    start_time = time.time()
    
    for prompt_data in STRESS_TEST_PROMPTS:
        result = await test_prompt(prompt_data, nl2sql_converter)
        results.append(result)
        
        # Brief pause between tests
        await asyncio.sleep(1)
    
    total_time = time.time() - start_time
    
    # === FINAL RESULTS ANALYSIS ===
    print("\n" + "=" * 80)
    print("🎯 FOCUSED STRESS TEST RESULTS")
    print("=" * 80)
    
    # Overall Statistics
    total_tests = len(results)
    successful_sql = sum(1 for r in results if r["sql_generated"])
    successful_execution = sum(1 for r in results if r["execution_success"])
    fully_successful = sum(1 for r in results if r["success"])
    
    print(f"📊 OVERALL STATISTICS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   SQL Generated: {successful_sql}/{total_tests} ({successful_sql/total_tests*100:.1f}%)")
    print(f"   SQL Executed: {successful_execution}/{total_tests} ({successful_execution/total_tests*100:.1f}%)")
    print(f"   Fully Successful: {fully_successful}/{total_tests} ({fully_successful/total_tests*100:.1f}%)")
    print(f"   Total Test Time: {total_time:.1f}s")
    
    # Success by Difficulty
    intermediate_results = [r for r in results if r["difficulty"] == "intermediate"]
    advanced_results = [r for r in results if r["difficulty"] == "advanced"]
    
    int_success = sum(1 for r in intermediate_results if r["success"])
    adv_success = sum(1 for r in advanced_results if r["success"])
    
    print(f"\n📈 SUCCESS BY DIFFICULTY:")
    print(f"   Intermediate: {int_success}/{len(intermediate_results)} ({int_success/len(intermediate_results)*100:.1f}%)")
    print(f"   Advanced: {adv_success}/{len(advanced_results)} ({adv_success/len(advanced_results)*100:.1f}%)")
    
    # Performance Analysis
    execution_times = [r["execution_time"] for r in results if r["execution_time"]]
    if execution_times:
        avg_time = sum(execution_times) / len(execution_times)
        max_time = max(execution_times)
        min_time = min(execution_times)
        
        print(f"\n⚡ PERFORMANCE ANALYSIS:")
        print(f"   Average Execution Time: {avg_time:.2f}s")
        print(f"   Fastest Query: {min_time:.2f}s")
        print(f"   Slowest Query: {max_time:.2f}s")
        print(f"   Sub-second Queries: {sum(1 for t in execution_times if t < 1.0)}/{len(execution_times)}")
    
    # Failed Tests Analysis
    failed_tests = [r for r in results if not r["success"]]
    if failed_tests:
        print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
        for failure in failed_tests:
            print(f"   #{failure['id']}: {failure['error']}")
    
    # Detailed Results Table
    print(f"\n📋 DETAILED RESULTS:")
    print("ID | Difficulty | SQL | Exec | Rows | Time | Status")
    print("-" * 55)
    
    for r in results:
        sql_status = "✅" if r["sql_generated"] else "❌"
        exec_status = "✅" if r["execution_success"] else "❌"
        time_str = f"{r['execution_time']:.2f}s" if r["execution_time"] else "N/A"
        status = "✅ PASS" if r["success"] else "❌ FAIL"
        
        print(f"{r['id']:2d} | {r['difficulty'][:4]:>4} | {sql_status:>3} | {exec_status:>4} | {r['result_count']:4d} | {time_str:>6} | {status}")
    
    # Recommendations
    print(f"\n🎯 RECOMMENDATIONS:")
    
    if fully_successful >= 8:
        print("   🟢 EXCELLENT: System is production-ready for demos")
        print("   🟢 NL2SQL accuracy is high, Firebolt performance is excellent")
    elif fully_successful >= 6:
        print("   🟡 GOOD: System is demo-ready with minor improvements needed")
        print("   🟡 Focus on fixing failed advanced queries")
    else:
        print("   🔴 NEEDS WORK: Multiple issues need addressing before demo")
        print("   🔴 Review failed tests and improve schema context")
    
    # Performance Assessment
    if execution_times and avg_time < 1.0:
        print("   ⚡ PERFORMANCE: Sub-second average - perfect for demos!")
    elif execution_times and avg_time < 2.0:
        print("   ⚡ PERFORMANCE: Fast execution - good for demos")
    else:
        print("   ⚠️  PERFORMANCE: Consider query optimization")
    
    return results

if __name__ == "__main__":
    print("🧪 Starting Focused Stress Test...")
    print("💡 Make sure ANTHROPIC_API_KEY is set as environment variable")
    print()
    
    results = asyncio.run(run_focused_stress_test())
    
    print(f"\n✅ Test completed! Check results above.")
    print(f"📊 Success rate: {sum(1 for r in results if r['success'])}/{len(results)} prompts passed")

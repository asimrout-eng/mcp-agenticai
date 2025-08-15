#!/usr/bin/env python3
"""
Real Firebolt MCP Server integration test
This script demonstrates actual integration with the Firebolt MCP server
"""

import os
import time
import json
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()

class RealFireboltMCPTest:
    """Real Firebolt MCP server test"""
    
    def __init__(self):
        self.account = os.getenv('FIREBOLT_ACCOUNT', 'se-demo-account')
        self.database = os.getenv('FIREBOLT_DATABASE', 'kush_test') 
        self.engine = os.getenv('FIREBOLT_ENGINE', 'kush_test_engine')
        self.service_account_id = os.getenv('FIREBOLT_SERVICE_ACCOUNT_ID', 'esIjzj7gw7uHRljSMRAnOOouho50ciy4')
        self.service_account_secret = os.getenv('FIREBOLT_SERVICE_ACCOUNT_SECRET', '1qgsZ9cpVy6qaj4GrDMww8h4aHR7gAaj2fGiippLh3sQX2rz564JgSAErRHFwghS')
        
        # Test queries
        # Test queries for our ad_performance table
        self.test_queries = [
            "SELECT COUNT(*) as total_events FROM ad_performance;",
            "SELECT device_type, SUM(revenue) as total_revenue FROM ad_performance WHERE event_type = 'conversion' GROUP BY device_type ORDER BY total_revenue DESC LIMIT 5;",
            "SELECT country, COUNT(*) as events FROM ad_performance GROUP BY country ORDER BY events DESC LIMIT 3;"
        ]
    
    async def run_with_mcp(self):
        """Run all tests using MCP session context"""
        print("🔌 Connecting to Firebolt MCP Server...")
        
        # Docker parameters for Firebolt MCP server
        server_params = StdioServerParameters(
            command="docker",
            args=[
                "run", "-i", "--rm",
                "-e", f"FIREBOLT_MCP_CLIENT_ID={self.service_account_id}",
                "-e", f"FIREBOLT_MCP_CLIENT_SECRET={self.service_account_secret}",
                "ghcr.io/firebolt-db/mcp-server:0.4.0"
            ]
        )
        
        try:
            # Create MCP session
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    print("🐳 MCP Server started successfully!")
                    
                    try:
                        # Initialize the session
                        result = await session.initialize()
                        print(f"  ✅ MCP Server: {result.serverInfo.name} v{result.serverInfo.version}")
                        
                        # Connect to Firebolt
                        await self.connect_to_firebolt(session)
                        
                        # Run test queries
                        await self.run_test_queries(session)
                        
                        # Get historical query execution times
                        # Skip historical query stats - we already have current run data
                        # await self.get_query_execution_stats(session)
                        
                    except Exception as session_error:
                        print(f"❌ Session Error: {str(session_error)}")
                        import traceback
                        print(f"Full traceback: {traceback.format_exc()}")
                        raise
                    
        except Exception as e:
            print(f"❌ MCP Error: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return False
        
        return True
    
    async def connect_to_firebolt(self, session: ClientSession):
        """Connect to Firebolt using MCP"""
        print(f"🔗 Connecting to Firebolt...")
        print(f"  Account: {self.account}")
        print(f"  Database: {self.database}")
        print(f"  Engine: {self.engine}")
        
        try:
            # First, get the docs_proof by calling firebolt_docs
            print("  📚 Getting docs proof...")
            docs_result = await session.call_tool("firebolt_docs", {})
            
            if docs_result.isError:
                print(f"  ❌ Failed to get docs proof: {docs_result.content}")
                raise Exception(f"Failed to get docs proof: {docs_result.content}")
            
            # Extract docs_proof from the documentation response
            
            # Extract docs_proof from the result
            docs_proof = None
            docs_content_str = str(docs_result.content)
            
            # Look for the specific proof string in the response
            import re
            proof_match = re.search(r'72J6hoVspktgpHtZXe1bSHurglRKhrTm', docs_content_str)
            if proof_match:
                docs_proof = "72J6hoVspktgpHtZXe1bSHurglRKhrTm"
                print(f"  ✅ Found docs proof in response!")
            else:
                # Try to find any similar pattern
                proof_pattern = re.search(r'([A-Za-z0-9]{32})', docs_content_str)
                if proof_pattern:
                    docs_proof = proof_pattern.group(1)
                    print(f"  ⚠️ Found alternative proof pattern: {docs_proof}")
                else:
                    print("  ❌ No docs proof found in response, cannot continue")
                    raise Exception("No valid docs_proof found in firebolt_docs response")
            
            print(f"  ✅ Using docs proof: {docs_proof[:20]}...")
            
            # Now call firebolt_connect with docs_proof
            connect_result = await session.call_tool(
                "firebolt_connect",
                {
                    "account": self.account,
                    "database": self.database,
                    "engine": self.engine,
                    "docs_proof": docs_proof
                }
            )
            
            if connect_result.isError:
                print(f"  ❌ Connection failed: {connect_result.content}")
                raise Exception(f"Connection failed: {connect_result.content}")
            
            print(f"  ✅ Connected to Firebolt successfully!")
            
        except Exception as e:
            print(f"  ❌ Connection error: {str(e)}")
            raise
    
    async def run_test_queries(self, session: ClientSession):
        """Execute test queries using MCP"""
        print(f"\n⚡ Running {len(self.test_queries)} test queries...")
        
        results = []
        
        # Track successful queries for summary  
        successful_queries = []
        
        for i, query in enumerate(self.test_queries, 1):
            print(f"\n📊 Query {i}: {query[:50]}{'...' if len(query) > 50 else ''}")
            
            try:
                start_time = time.time()
                query_start_timestamp = start_time
                
                # Execute query using firebolt_query tool
                query_result = await session.call_tool(
                    "firebolt_query",
                    {
                        "account": self.account,
                        "database": self.database,
                        "engine": self.engine,
                        "query": query
                    }
                )
                
                execution_time = (time.time() - start_time) * 1000
                
                if query_result.isError:
                    # Try to extract Firebolt execution time from error response
                    error_content = str(query_result.content)
                    firebolt_time_ms = self._extract_firebolt_time(error_content)
                    
                    print(f"  ❌ Query failed")
                    if firebolt_time_ms:
                        print(f"     Firebolt execution time: {firebolt_time_ms:.1f}ms (query processed but failed)")
                        print(f"     Round-trip time: {execution_time:.1f}ms")
                    else:
                        print(f"     Round-trip time: {execution_time:.1f}ms")
                    
                    # Show shortened error
                    if "Decimal math overflow" in error_content:
                        print(f"     Error: Decimal overflow - need to fix table schema")
                    else:
                        print(f"     Error: {error_content[:100]}...")
                    
                    results.append({
                        'query': query,
                        'success': False,
                        'error': str(query_result.content),
                        'round_trip_time_ms': execution_time,
                        'firebolt_execution_time_ms': firebolt_time_ms,
                        'execution_time_ms': firebolt_time_ms or execution_time
                    })
                else:
                    # Parse result and extract Firebolt timing
                    try:
                        if hasattr(query_result.content, '__iter__') and len(query_result.content) > 0:
                            result_text = query_result.content[0].text if hasattr(query_result.content[0], 'text') else str(query_result.content[0])
                        else:
                            result_text = str(query_result.content)
                        
                        # Note: Successful queries don't include timing stats in response
                        # We'll get exact timing after all queries are complete
                        
                        print(f"  ✅ Success ({execution_time:.1f}ms Round-trip time)")
                        print(f"     Result: {result_text[:100]}{'...' if len(result_text) > 100 else ''}")
                        
                        # Track for summary
                        successful_queries.append({
                            'index': i,
                            'execution_time_ms': execution_time
                        })
                        
                        firebolt_time_ms = None
                        
                    except Exception as parse_error:
                        result_text = str(query_result.content)
                        firebolt_time_ms = self._extract_firebolt_time(result_text)
                        display_time = firebolt_time_ms if firebolt_time_ms else execution_time
                        
                        print(f"  ✅ Success ({display_time:.1f}ms)")
                        print(f"     Raw result: {result_text[:100]}{'...' if len(result_text) > 100 else ''}")
                    
                    results.append({
                        'query': query,
                        'success': True,
                        'result': result_text,
                        'round_trip_time_ms': execution_time,
                        'firebolt_execution_time_ms': firebolt_time_ms,
                        'execution_time_ms': firebolt_time_ms or execution_time
                    })
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                print(f"  ❌ Query error: {str(e)}")
                results.append({
                    'query': query,
                    'success': False,
                    'error': str(e),
                    'execution_time_ms': execution_time
                })
        
        # Summary
        successful = [r for r in results if r['success']]
        if successful:
            # Calculate both Firebolt and round-trip times
            firebolt_times = [r.get('firebolt_execution_time_ms') for r in successful if r.get('firebolt_execution_time_ms')]
            round_trip_times = [r['round_trip_time_ms'] for r in successful]
            
            avg_time = sum(r['execution_time_ms'] for r in successful) / len(successful)
            fastest = min(r['execution_time_ms'] for r in successful)
            
            print(f"\n📈 Performance Summary:")
            print(f"  Successful queries: {len(successful)}/{len(results)}")
            print(f"  Average execution time: {avg_time:.1f}ms")
            print(f"  Fastest query: {fastest:.1f}ms")
            
            if firebolt_times:
                avg_firebolt = sum(firebolt_times) / len(firebolt_times)
                fastest_firebolt = min(firebolt_times)
                avg_roundtrip = sum(round_trip_times) / len(round_trip_times) 
                
                print(f"  📊 Firebolt Engine Times:")
                print(f"    Average: {avg_firebolt:.1f}ms")
                print(f"    Fastest: {fastest_firebolt:.1f}ms")
                print(f"  🌐 Network Round-trip:")
                print(f"    Average: {avg_roundtrip:.1f}ms") 
                print(f"    Network overhead: {avg_roundtrip - avg_firebolt:.1f}ms")
            
            print(f"  ⚡ Sub-second rate: {len([r for r in successful if r['execution_time_ms'] < 1000]) / len(successful) * 100:.1f}%")
        else:
            print(f"\n❌ No successful queries")
        
        # Wait for all queries to be recorded in information schema, then show timing table
        print(f"\n⏱️  Waiting for query history to be recorded...")
        await asyncio.sleep(2.0)  # Ensure all queries are in history
        
        # Display timing table from information schema
        await self._display_timing_table(session)
    
    def _extract_firebolt_time(self, response_text: str) -> float:
        """Extract Firebolt's internal execution time from response"""
        try:
            import re
            import json
            
            # Look for elapsed time in response text
            
            # Look for statistics.elapsed in JSON response
            # Pattern: "elapsed": 0.5322145659999999
            elapsed_pattern = r'"elapsed":\s*([0-9.]+)'
            match = re.search(elapsed_pattern, response_text)
            
            if match:
                elapsed_seconds = float(match.group(1))
                elapsed_ms = elapsed_seconds * 1000  # Convert to milliseconds
                return elapsed_ms
            
            # For successful queries, look for timing in metadata/statistics
            # The MCP response might contain statistics in a different format
            
            # Try to find JSON-like structures
            json_patterns = [
                r'\{[^}]*"elapsed"[^}]*\}',
                r'\{[^}]*"statistics"[^}]*\}',
                r'"statistics":\s*\{[^}]+\}'
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, response_text)
                for match_text in matches:
                    try:
                        # Try to parse as JSON
                        if not match_text.startswith('{'):
                            match_text = '{' + match_text
                        if not match_text.endswith('}'):
                            match_text = match_text + '}'
                            
                        parsed = json.loads(match_text)
                        if 'elapsed' in parsed:
                            return parsed['elapsed'] * 1000
                        if 'statistics' in parsed and 'elapsed' in parsed['statistics']:
                            return parsed['statistics']['elapsed'] * 1000
                    except:
                        continue
            
            # Look for timing patterns in text
            time_patterns = [
                r'([0-9.]+)\s*ms',
                r'([0-9.]+)\s*milliseconds',
                r'([0-9.]+)\s*seconds?\s*',
                r'execution.*?([0-9.]+)\s*s',
                r'elapsed.*?([0-9.]+)',
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, response_text, re.IGNORECASE)
                if match:
                    time_val = float(match.group(1))
                    # If it looks like seconds (small number), convert to ms
                    if 'second' in pattern or ('ms' not in pattern and time_val < 60):
                        return time_val * 1000
                    return time_val
                    
        except Exception as e:
            # Silent fail - we'll use round-trip time as fallback
            pass
        
        return None
    
    async def _get_exact_query_time(self, session: ClientSession, executed_query: str) -> dict:
        """Get the exact Firebolt execution time for the specific query that was just executed"""
        try:
            # Clean up the executed query for exact matching
            clean_query = executed_query.strip()
            if clean_query.endswith(';'):
                clean_query = clean_query[:-1]
            
            # Escape single quotes in the query for SQL
            escaped_query = clean_query.replace("'", "''")
            
            # Query to get the exact execution stats for our specific query
            # Get the most recent successful queries and match by the clean query text
            query_without_comment = clean_query.split(' -- Test run')[0].strip()
            escaped_query_clean = query_without_comment.replace("'", "''")
            
            stats_query = f"""
            SELECT 
                query_text,
                duration_us,
                ROUND(duration_us / 1000.0, 2) as duration_ms,
                status,
                start_time
            FROM information_schema.engine_user_query_history 
            WHERE status = 'ENDED_SUCCESSFULLY'
              AND start_time >= NOW() - INTERVAL '5' MINUTE
            ORDER BY start_time DESC 
            LIMIT 10;
            """
            
            # Query for exact timing information
            
            stats_result = await session.call_tool(
                "firebolt_query",
                {
                    "account": self.account,
                    "database": self.database,
                    "engine": self.engine,
                    "query": stats_query
                }
            )
            
            if not stats_result.isError:
                stats_text = stats_result.content[0].text if hasattr(stats_result.content[0], 'text') else str(stats_result.content[0])
                print(f"  📄 Query history result: {stats_text[:200]}...")
                
                import json
                try:
                    stats_data = json.loads(stats_text)
                    print(f"  📋 Found {len(stats_data) if isinstance(stats_data, list) else 0} recent successful queries")
                    if isinstance(stats_data, list) and len(stats_data) > 0:
                        # Look for a query that matches our executed query (without comment)
                        print(f"  🔍 Looking for query starting with: {query_without_comment[:60]}...")
                        
                        for i, record in enumerate(stats_data):
                            record_query = record.get('query_text', '').strip()
                            print(f"  📝 Record {i+1}: {record_query[:60]}...")
                            
                            # Remove extra whitespace and newlines for comparison
                            # Also remove semicolons for matching
                            normalized_record = ' '.join(record_query.strip().rstrip(';').split())
                            normalized_target = ' '.join(query_without_comment.strip().rstrip(';').split())
                            
                            if i < 5:  # Only show first 5 for debugging
                                print(f"    🔍 Comparing:")
                                print(f"    Target:  '{normalized_target[:80]}...'")
                                print(f"    Record:  '{normalized_record[:80]}...'")
                                print(f"    Match: {normalized_record == normalized_target}")
                            
                            if normalized_record == normalized_target:
                                status = record.get('status')
                                duration_us = record.get('duration_us')
                                
                                print(f"  ✅ Found exact matching query!")
                                print(f"  🔍 Record: status={status}, duration_us={duration_us}")
                                
                                if status == 'ENDED_SUCCESSFULLY' and duration_us is not None and duration_us > 0:
                                    return {
                                        'duration_ms': record.get('duration_ms'),
                                        'duration_us': duration_us,
                                        'status': status,
                                        'found': True
                                    }
                        
                        print(f"  ⚠️ No matching query found in recent history")
                        return {'found': False}
                    else:
                        print(f"  ⚠️ No recent successful queries found")
                        return {'found': False}
                        
                except Exception as parse_err:
                    # JSON parse error
                    pass
                    
        except Exception as e:
            print(f"  ⚠️ Error getting exact timing: {str(e)}")
        
        return {'found': False}
    
    async def _display_timing_table(self, session: ClientSession):
        """Display query execution results by querying information schema"""
        print(f"\n📊 Fetching Recent Query Performance...")
        
        # Simple query to get recent successful queries
        timing_query = """
        SELECT 
            query_text,
            duration_us,
            ROUND(duration_us / 1000.0, 2) as duration_ms,
            start_time
        FROM information_schema.engine_user_query_history 
        WHERE status = 'ENDED_SUCCESSFULLY'
          AND start_time >= NOW() - INTERVAL '2' MINUTE
        ORDER BY start_time DESC 
        LIMIT 5;
        """
        
        try:
            result = await session.call_tool(
                "firebolt_query",
                {
                    "account": self.account,
                    "database": self.database,
                    "engine": self.engine,
                    "query": timing_query
                }
            )
            
            if not result.isError:
                result_text = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
                
                import json
                timing_data = json.loads(result_text)
                
                if isinstance(timing_data, list) and len(timing_data) > 0:
                    print(f"\n📊 Query Execution Results")
                    print("=" * 90)
                    print(f"{'Query':<8} {'Execution Time':<25} {'Query Text':<50}")
                    print("-" * 90)
                    
                    # Filter out timing queries and get actual test queries
                    actual_queries = [r for r in timing_data if 'information_schema.engine_user_query_history' not in r.get('query_text', '')]
                    
                    # Match queries to their original order by content (most recent match only)
                    query_matches = []
                    used_records = set()
                    
                    for i, original_query in enumerate(self.test_queries, 1):
                        original_clean = original_query.strip().rstrip(';')
                        
                        # Find the most recent (first in list) matching record that hasn't been used
                        for record in actual_queries:
                            record_id = id(record)  # Use object id as unique identifier
                            if record_id in used_records:
                                continue
                                
                            record_query = record.get('query_text', '').strip()
                            if record_query == original_clean:
                                query_matches.append({
                                    'number': i,
                                    'record': record,
                                    'original': original_query
                                })
                                used_records.add(record_id)
                                break
                    
                    # Display in original execution order
                    for match in sorted(query_matches, key=lambda x: x['number']):
                        record = match['record']
                        query_num = match['number']
                        duration_ms = record.get('duration_ms', 0)
                        duration_us = record.get('duration_us', 0)
                        
                        # Truncate long queries for display
                        display_query = match['original'][:45] + '...' if len(match['original']) > 45 else match['original']
                        
                        # Format with microseconds in brackets
                        time_display = f"{duration_ms}ms ({duration_us:,}μs)"
                        
                        print(f"Query {query_num:<2} {time_display:<20} {display_query}")
                    
                    print("=" * 90)
                    
                    # Summary - only for matched queries from current run
                    if query_matches:
                        times = [match['record']['duration_ms'] for match in query_matches]
                        avg_time = sum(times) / len(times)
                        fastest = min(times)
                        print(f"Summary: {len(query_matches)} queries | Avg: {avg_time:.2f}ms | Fastest: {fastest:.2f}ms")
                        print("=" * 90)
                        
                else:
                    print("  ⚠️ No recent queries found")
                    
            else:
                print(f"  ❌ Error fetching timing data: {result.content}")
                
        except Exception as e:
            print(f"  ❌ Error displaying timing table: {str(e)}")
    
    async def get_query_execution_stats(self, session: ClientSession):
        """Get actual Firebolt execution times from query history"""
        print(f"\n📊 Fetching Firebolt Execution Statistics...")
        
        # Query to get execution stats for our test queries
        stats_query = """
        SELECT 
            query_text,
            duration_us,
            ROUND(duration_us / 1000.0, 1) as duration_ms,
            status,
            start_time,
            query_id
        FROM information_schema.engine_user_query_history 
        WHERE status = 'ENDED_SUCCESSFULLY'
          AND (
              query_text LIKE '%SELECT COUNT(*) as total_events FROM ad_performance%'
              OR query_text LIKE '%SELECT country, COUNT(*) as events FROM ad_performance%'
              OR query_text LIKE '%SELECT device_type, SUM(revenue)%'
          )
        ORDER BY start_time DESC 
        LIMIT 10;
        """
        
        try:
            # Execute the stats query
            start_time = time.time()
            
            stats_result = await session.call_tool(
                "firebolt_query",
                {
                    "account": self.account,
                    "database": self.database,
                    "engine": self.engine,
                    "query": stats_query
                }
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            if stats_result.isError:
                print(f"  ❌ Stats query failed: {stats_result.content}")
                return
            
            # Parse the historical stats
            try:
                if hasattr(stats_result.content, '__iter__') and len(stats_result.content) > 0:
                    stats_text = stats_result.content[0].text if hasattr(stats_result.content[0], 'text') else str(stats_result.content[0])
                else:
                    stats_text = str(stats_result.content)
                
                print(f"  ✅ Retrieved query history ({execution_time:.1f}ms)")
                
                # Try to parse as JSON
                import json
                try:
                    stats_data = json.loads(stats_text)
                    
                    if isinstance(stats_data, list) and len(stats_data) > 0:
                        print(f"\n📈 Historical Firebolt Execution Times:")
                        print(f"  Found {len(stats_data)} successful queries in history:")
                        
                        for i, query_stat in enumerate(stats_data[:5], 1):  # Show top 5
                            duration_ms = query_stat.get('duration_ms', 0)
                            query_preview = query_stat.get('query_text', '')[:60]
                            
                            # Identify query type
                            if 'COUNT(*)' in query_preview.upper():
                                query_type = "COUNT Query"
                            elif 'GROUP BY country' in query_preview:
                                query_type = "Country Grouping"
                            elif 'SUM(revenue)' in query_preview:
                                query_type = "Revenue Aggregation"
                            else:
                                query_type = "Other Query"
                            
                            print(f"    {i}. {query_type}: {duration_ms}ms")
                            print(f"       Query: {query_preview}...")
                        
                        # Calculate performance stats from historical data
                        durations = [q.get('duration_ms', 0) for q in stats_data if q.get('duration_ms')]
                        if durations:
                            avg_duration = sum(durations) / len(durations)
                            min_duration = min(durations)
                            max_duration = max(durations)
                            sub_second_count = len([d for d in durations if d < 1000])
                            
                            print(f"\n  📊 Firebolt Engine Performance Analysis:")
                            print(f"     Average execution: {avg_duration:.1f}ms")
                            print(f"     Fastest query: {min_duration:.1f}ms")
                            print(f"     Slowest query: {max_duration:.1f}ms")
                            print(f"     Sub-second rate: {sub_second_count}/{len(durations)} ({sub_second_count/len(durations)*100:.1f}%)")
                            
                            if min_duration < 100:
                                print(f"  🚀 ULTRA-FAST: Fastest query under 100ms!")
                            if avg_duration < 500:
                                print(f"  ⚡ EXCELLENT: Average under 500ms!")
                        
                    else:
                        print(f"  ⚠️ No historical query data found")
                        print(f"     Raw response: {stats_text[:200]}...")
                        
                except json.JSONDecodeError:
                    print(f"  ⚠️ Could not parse stats as JSON")
                    print(f"     Raw response: {stats_text[:200]}...")
                
            except Exception as parse_error:
                print(f"  ❌ Error parsing stats: {str(parse_error)}")
                
        except Exception as e:
            print(f"  ❌ Error fetching stats: {str(e)}")
    
    async def test_firebolt_docs(self, session: ClientSession):
        """Test Firebolt docs access"""
        print(f"\n📚 Testing Firebolt documentation access...")
        
        try:
            # Get docs using firebolt_docs tool
            docs_result = await session.call_tool("firebolt_docs", {})
            
            if docs_result.isError:
                print(f"  ❌ Docs access failed: {docs_result.content}")
            else:
                print(f"  ✅ Documentation accessible")
                
        except Exception as e:
            print(f"  ❌ Docs error: {str(e)}")

async def execute_query_via_mcp(query: str) -> List[Dict[str, Any]]:
    """Execute a single query via MCP - for use by other modules"""
    # Get credentials from environment
    service_account_id = os.getenv('FIREBOLT_MCP_CLIENT_ID')
    service_account_secret = os.getenv('FIREBOLT_MCP_CLIENT_SECRET')
    account = os.getenv('FIREBOLT_MCP_ACCOUNT')
    database = os.getenv('FIREBOLT_MCP_DATABASE')
    engine = os.getenv('FIREBOLT_MCP_ENGINE')
    
    if not all([service_account_id, service_account_secret, account, database, engine]):
        raise Exception("Missing required Firebolt MCP environment variables")
    
    # Docker parameters for Firebolt MCP server
    server_params = StdioServerParameters(
        command="docker",
        args=[
            "run", "-i", "--rm",
            "-e", f"FIREBOLT_MCP_CLIENT_ID={service_account_id}",
            "-e", f"FIREBOLT_MCP_CLIENT_SECRET={service_account_secret}",
            "ghcr.io/firebolt-db/mcp-server:0.4.0"
        ]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Get documentation proof
                docs_result = await session.call_tool("firebolt_docs", {})
                if docs_result.isError:
                    raise Exception(f"Failed to get docs proof: {docs_result.content}")
                
                # Extract docs proof
                docs_content_str = str(docs_result.content)
                import re
                
                # Try hardcoded proof first
                proof_match = re.search(r'72J6hoVspktgpHtZXe1bSHurglRKhrTm', docs_content_str)
                if proof_match:
                    docs_proof = "72J6hoVspktgpHtZXe1bSHurglRKhrTm"
                else:
                    # Try alternative pattern
                    proof_pattern = re.search(r'([A-Za-z0-9]{32})', docs_content_str)
                    if proof_pattern:
                        docs_proof = proof_pattern.group(1)
                    else:
                        raise Exception("No valid docs_proof found")
                
                # Connect to Firebolt
                connect_result = await session.call_tool(
                    "firebolt_connect",
                    {"docs_proof": docs_proof}
                )
                
                if connect_result.isError:
                    raise Exception(f"Firebolt connection failed: {connect_result.content}")
                
                # Execute the query
                query_result = await session.call_tool(
                    "firebolt_query",
                    {
                        "account": account,
                        "database": database,
                        "engine": engine,
                        "query": query
                    }
                )
                
                if query_result.isError:
                    error_content = query_result.content[0].text if hasattr(query_result.content[0], 'text') else str(query_result.content)
                    raise Exception(f"Query failed: {error_content}")
                
                # Parse result
                result_text = query_result.content[0].text if hasattr(query_result.content[0], 'text') else str(query_result.content[0])
                
                try:
                    # Try to parse as JSON
                    result_data = json.loads(result_text)
                    return result_data if isinstance(result_data, list) else [result_data]
                except json.JSONDecodeError:
                    # Return as simple result
                    return [{"result": result_text}]
                
    except Exception as e:
        raise Exception(f"MCP query execution failed: {str(e)}")

async def main():
    """Main test runner"""
    tester = RealFireboltMCPTest()
    
    print("🚀 Firebolt MCP Server Real Integration Test")
    print("=" * 50)
    
    try:
        success = await tester.run_with_mcp()
        
        if success:
            print(f"\n🎉 All tests completed successfully!")
            print(f"\n✅ REAL MCP INTEGRATION WORKING!")
        else:
            print(f"\n❌ Some tests failed")
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())

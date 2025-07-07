#!/usr/bin/env python3
"""
Interactive CLI for Financial Data AI Agent

This script provides a command-line interface to interact with the Financial Data AI Agent API.
"""

import requests
import json
import argparse
import sys
from pathlib import Path
from typing import Optional


class FinancialDataCLI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.session_id: Optional[str] = None
    
    def check_health(self) -> bool:
        """Check if the API server is running"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False
    
    def upload_file(self, file_path: str) -> bool:
        """Upload a CSV/Excel file to the API"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ Error: File '{file_path}' not found")
            return False
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'text/csv')}
                response = requests.post(f"{self.api_base}/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                self.session_id = result['session_id']
                print(f"✅ Upload successful!")
                print(f"📋 Session ID: {self.session_id}")
                print(f"📊 Rows processed: {result['data_summary']['total_rows']}")
                return True
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Upload failed: {str(e)}")
            return False
    
    def query_data(self, query: str) -> bool:
        """Query the uploaded data"""
        if not self.session_id:
            print("❌ No active session. Please upload a file first.")
            return False
        
        try:
            query_data = {
                "session_id": self.session_id,
                "query": query
            }
            
            response = requests.post(f"{self.api_base}/query", json=query_data)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Query successful!")
                print(f"📝 Answer: {result['answer']}")
                print(f"🎯 Confidence: {result['confidence']}")
                if result['insights']:
                    print(f"💡 Insights: {len(result['insights'])} found")
                return True
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(f"Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Query failed: {str(e)}")
            return False
    
    def get_insights(self, session_id: Optional[str] = None) -> bool:
        """Get automatic insights for the current session or specified session"""
        # Use provided session_id or fall back to current session
        target_session_id = session_id or self.session_id
        
        if not target_session_id:
            print("❌ No session specified. Please provide a session ID or upload a file first.")
            return False
        
        try:
            response = requests.get(f"{self.api_base}/insights/{target_session_id}")
            
            if response.status_code == 200:
                insights = response.json()
                print(f"✅ Insights generated for session: {target_session_id}")
                if 'ai_summary' in insights:
                    print(f"🤖 AI Summary: {insights['ai_summary']}")
                
                # Show additional insights if available
                if 'basic_statistics' in insights:
                    stats = insights['basic_statistics']
                    if 'amount_statistics' in stats:
                        amount_stats = stats['amount_statistics']
                        print(f"\n📊 Financial Statistics:")
                        print(f"   💰 Total: {amount_stats.get('total', 'N/A')}")
                        print(f"   📈 Average: {amount_stats.get('mean', 'N/A')}")
                        print(f"   📉 Range: {amount_stats.get('min', 'N/A')} - {amount_stats.get('max', 'N/A')}")
                
                return True
            else:
                print(f"❌ Insights failed: {response.status_code}")
                print(f"Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Insights failed: {str(e)}")
            return False
    
    def get_session_info(self) -> bool:
        """Get information about the current session"""
        if not self.session_id:
            print("❌ No active session. Please upload a file first.")
            return False
        
        try:
            response = requests.get(f"{self.api_base}/session/{self.session_id}")
            
            if response.status_code == 200:
                info = response.json()
                print("✅ Session information:")
                print(f"📁 File: {info['file_info']['filename']}")
                print(f"📊 Rows: {info['data_summary']['total_rows']}")
                print(f"🔢 Columns: {info['data_summary']['total_columns']}")
                print(f"📅 Created: {info['created_at']}")
                print(f"🔄 Last accessed: {info['last_accessed']}")
                
                if info['data_summary']['date_range']:
                    print(f"📆 Date range: {info['data_summary']['date_range']['start']} to {info['data_summary']['date_range']['end']}")
                
                if info['data_summary']['total_amount']:
                    print(f"💰 Total amount: {info['data_summary']['total_amount']}")
                
                if info['data_summary']['categories']:
                    print(f"🏷️ Categories: {', '.join(info['data_summary']['categories'][:5])}")
                    if len(info['data_summary']['categories']) > 5:
                        print(f"   ... and {len(info['data_summary']['categories']) - 5} more")
                
                return True
            else:
                print(f"❌ Session info failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Session info failed: {str(e)}")
            return False
    
    def list_stored_sessions(self) -> bool:
        """List all stored sessions with detailed information"""
        try:
            response = requests.get(f"{self.api_base}/storage/sessions")
            
            if response.status_code == 200:
                result = response.json()
                sessions = result['stored_sessions']
                
                print("✅ Stored sessions:")
                if not sessions:
                    print("   No stored sessions found")
                else:
                    print(f"   Total: {result['total_count']} sessions")
                    print("   " + "="*80)
                    
                    # Get details for each session
                    for i, session_id in enumerate(sessions[:10], 1):  # Show first 10
                        try:
                            session_response = requests.get(f"{self.api_base}/session/{session_id}")
                            if session_response.status_code == 200:
                                session_info = session_response.json()
                                filename = session_info['file_info']['filename']
                                rows = session_info['data_summary']['total_rows']
                                created = session_info['created_at'][:10]  # Just the date
                                print(f"   {i:2d}. {session_id}")
                                print(f"       📁 File: {filename}")
                                print(f"       📊 Rows: {rows} | 📅 Created: {created}")
                            else:
                                print(f"   {i:2d}. {session_id} (details unavailable)")
                        except:
                            print(f"   {i:2d}. {session_id} (details unavailable)")
                        
                        if i < len(sessions[:10]):
                            print("   " + "-"*40)
                    
                    if len(sessions) > 10:
                        print(f"   ... and {len(sessions) - 10} more sessions")
                
                storage_stats = result['storage_stats']
                print(f"\n💾 Storage: {storage_stats['total_size_mb']} MB used")
                print("\n💡 Tip: Use 'insights <session_id>' to get insights for any session")
                return True
            else:
                print(f"❌ Failed to list sessions: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to list sessions: {str(e)}")
            return False
    
    def interactive_mode(self):
        """Start interactive mode"""
        print("🚀 Financial Data AI Agent - Interactive Mode")
        print("=" * 50)
        
        if not self.check_health():
            print("❌ API server is not running. Please start the server first.")
            print("Run: python main.py")
            return
        
        print("✅ API server is running")
        print("\nCommands:")
        print("  upload <file_path>  - Upload a CSV/Excel file")
        print("  query <question>    - Ask a question about your data")
        print("  insights [session_id] - Get automatic insights (current or specified session)")
        print("  info              - Show session information")
        print("  sessions          - List all stored sessions")
        print("  quit              - Exit the program")
        print()
        
        while True:
            try:
                command = input("🤖 > ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                elif command.startswith('upload '):
                    file_path = command[7:].strip()
                    self.upload_file(file_path)
                
                elif command.startswith('query '):
                    query = command[6:].strip()
                    if query:
                        self.query_data(query)
                    else:
                        print("❌ Please provide a query")
                
                elif command.startswith('insights'):
                    # Parse insights command: "insights" or "insights <session_id>"
                    parts = command.split()
                    if len(parts) == 1:
                        # No session ID provided, use current session
                        self.get_insights()
                    elif len(parts) == 2:
                        # Session ID provided
                        session_id = parts[1].strip()
                        self.get_insights(session_id)
                    else:
                        print("❌ Usage: insights [session_id]")
                
                elif command == 'info':
                    self.get_session_info()
                
                elif command == 'sessions':
                    self.list_stored_sessions()
                
                elif command == 'help':
                    print("\nCommands:")
                    print("  upload <file_path>     - Upload a CSV/Excel file")
                    print("  query <question>       - Ask a question about your data")
                    print("  insights [session_id]  - Get automatic insights (current or specified session)")
                    print("  info                   - Show session information")
                    print("  sessions               - List all stored sessions")
                    print("  quit                   - Exit the program")
                
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
                
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break


def main():
    parser = argparse.ArgumentParser(description="Financial Data AI Agent CLI")
    parser.add_argument("--url", default="http://localhost:8000", help="API server URL")
    parser.add_argument("--upload", help="Upload a file")
    parser.add_argument("--query", help="Query the data")
    parser.add_argument("--insights", nargs='?', const=True, help="Get insights (optionally specify session_id)")
    parser.add_argument("--info", action="store_true", help="Get session info")
    parser.add_argument("--sessions", action="store_true", help="List stored sessions")
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode")
    
    args = parser.parse_args()
    
    cli = FinancialDataCLI(args.url)
    
    # Check if server is running
    if not cli.check_health():
        print("❌ API server is not running. Please start the server first.")
        print("Run: python main.py")
        sys.exit(1)
    
    # Handle command line arguments
    if args.upload:
        cli.upload_file(args.upload)
    
    if args.query:
        cli.query_data(args.query)
    
    if args.insights:
        if isinstance(args.insights, str):
            # Session ID provided
            cli.get_insights(args.insights)
        else:
            # No session ID, use current session
            cli.get_insights()
    
    if args.info:
        cli.get_session_info()
    
    if args.sessions:
        cli.list_stored_sessions()
    
    # Start interactive mode if no specific command or if explicitly requested
    if args.interactive or not any([args.upload, args.query, args.insights, args.info, args.sessions]):
        cli.interactive_mode()


if __name__ == "__main__":
    main()
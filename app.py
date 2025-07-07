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
    
    def get_insights(self) -> bool:
        """Get automatic insights for the current session"""
        if not self.session_id:
            print("❌ No active session. Please upload a file first.")
            return False
        
        try:
            response = requests.get(f"{self.api_base}/insights/{self.session_id}")
            
            if response.status_code == 200:
                insights = response.json()
                print("✅ Insights generated!")
                if 'ai_summary' in insights:
                    print(f"🤖 AI Summary: {insights['ai_summary']}")
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
                return True
            else:
                print(f"❌ Session info failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Session info failed: {str(e)}")
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
        print("  insights           - Get automatic insights")
        print("  info              - Show session information")
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
                
                elif command == 'insights':
                    self.get_insights()
                
                elif command == 'info':
                    self.get_session_info()
                
                elif command == 'help':
                    print("\nCommands:")
                    print("  upload <file_path>  - Upload a CSV/Excel file")
                    print("  query <question>    - Ask a question about your data")
                    print("  insights           - Get automatic insights")
                    print("  info              - Show session information")
                    print("  quit              - Exit the program")
                
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
    parser.add_argument("--insights", action="store_true", help="Get insights")
    parser.add_argument("--info", action="store_true", help="Get session info")
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
        cli.get_insights()
    
    if args.info:
        cli.get_session_info()
    
    # Start interactive mode if no specific command or if explicitly requested
    if args.interactive or not any([args.upload, args.query, args.insights, args.info]):
        cli.interactive_mode()


if __name__ == "__main__":
    main()
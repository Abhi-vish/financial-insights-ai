"""
Startup script for the Financial Data AI Agent

This script sets up the environment and starts the server.
"""

import os
import sys
from pathlib import Path
import subprocess


def check_requirements():
    """Check if all requirements are installed"""
    try:
        import fastapi
        import uvicorn
        import pandas
        import google.generativeai
        import pydantic
        import numpy
        import openpyxl
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False


def setup_environment():
    """Set up the environment"""
    print("🔧 Setting up environment...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Creating from template...")
        template_file = Path(".env.template")
        if template_file.exists():
            import shutil
            shutil.copy(template_file, env_file)
            print("📝 Please edit .env file and add your GEMINI_API_KEY")
            return False
        else:
            print("❌ .env.template not found")
            return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if Gemini API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY not found in .env file")
        print("📝 Please add your Gemini API key to the .env file")
        return False
    
    print("✅ Environment setup complete")
    return True


def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Financial Data AI Agent server...")
    print("📊 Using Gemini 2.0 Flash for AI processing")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📖 API docs will be available at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    # Import and run the application
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {str(e)}")


def main():
    """Main startup function"""
    print("💰 Financial Data AI Agent Startup")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("\n📦 Installing requirements...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Requirements installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install requirements")
            print("💡 Please run: pip install -r requirements.txt")
            return
    
    # Setup environment
    if not setup_environment():
        return
    
    # Start server
    start_server()


if __name__ == "__main__":
    main()

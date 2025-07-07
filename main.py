"""
Financial Data AI Agent - Main Application Entry Point

A modular API-driven AI agent for financial data analysis using Gemini 2.0 Flash.
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from src.api.endpoints import router
from src.core.config import settings

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting Financial Data AI Agent...")
    print(f"📊 Using Gemini 2.0 Flash for AI processing")
    yield
    # Shutdown
    print("🛑 Shutting down Financial Data AI Agent...")

# Create FastAPI application
app = FastAPI(
    title="Financial Data AI Agent",
    description="A modular API-driven AI agent for financial data analysis using Gemini 2.0 Flash",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Financial Data AI Agent is running!",
        "version": "1.0.0",
        "status": "active",
        "ai_model": "Gemini 2.0 Flash"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "financial-data-ai-agent"}

if __name__ == "__main__":
    print("🔧 Starting development server...")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

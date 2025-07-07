"""
Pydantic models for request/response schemas
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime


class UploadResponse(BaseModel):
    """Response model for file upload"""
    message: str
    session_id: str
    file_info: Dict[str, Any]
    data_summary: Dict[str, Any]


class QueryRequest(BaseModel):
    """Request model for querying financial data"""
    session_id: str = Field(..., description="Session ID from file upload")
    query: str = Field(..., min_length=1, description="Natural language query about the financial data")


class QueryResponse(BaseModel):
    """Response model for data query"""
    query: str
    answer: str
    insights: List[str]
    data_points: Dict[str, Any]
    confidence: str
    limitations: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)


class FileInfo(BaseModel):
    """File information model"""
    filename: str
    file_size: int
    file_type: str
    upload_timestamp: datetime = Field(default_factory=datetime.now)


class DataSummary(BaseModel):
    """Data summary model"""
    total_rows: int
    columns: List[str]
    date_range: Optional[Dict[str, str]] = None
    total_amount: Optional[float] = None
    categories: Optional[List[str]] = None
    data_types: Dict[str, str]


class SessionInfo(BaseModel):
    """Session information model"""
    session_id: str
    file_info: FileInfo
    data_summary: DataSummary
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)

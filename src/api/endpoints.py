"""
API endpoints for the Financial Data AI Agent

This module contains all the REST API endpoints for file upload,
data querying, and analysis.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import tempfile
import os
from pathlib import Path
import logging
from datetime import datetime

from src.models.schemas import (
    UploadResponse, QueryRequest, QueryResponse, ErrorResponse,
    FileInfo, DataSummary
)
from src.services.data_processor import DataProcessor
from src.services.query_engine import QueryEngine
from src.utils.validators import data_validator
from src.utils.cache import session_cache
from src.utils.storage import data_storage
from src.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize services
data_processor = DataProcessor()
query_engine = QueryEngine()


@router.post("/upload", response_model=UploadResponse)
async def upload_financial_data(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload and process financial data file (CSV or Excel)
    
    Args:
        file: Uploaded file containing financial data
        background_tasks: Background tasks for cleanup
        
    Returns:
        UploadResponse with session ID and data summary
    """
    temp_file_path = None
    
    try:
        logger.info(f"📤 Uploading file: {file.filename}")
        
        # Validate file
        file_size = 0
        if hasattr(file, 'size'):
            file_size = file.size
        else:
            # Read file to get size
            content = await file.read()
            file_size = len(content)
            await file.seek(0)  # Reset file pointer
        
        is_valid, error_msg = data_validator.validate_file_upload(
            file.filename, file_size, file.content_type
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Create temporary file
        file_extension = Path(file.filename).suffix.lower()
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=file_extension,
            prefix="financial_data_"
        )
        temp_file_path = temp_file.name
        
        # Write uploaded content to temporary file
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        
        # Process the data
        logger.info("🔄 Processing uploaded data...")
        
        # Read and validate DataFrame
        df = data_processor.read_financial_data(temp_file_path)
        
        is_valid_df, error_msg, warnings = data_validator.validate_dataframe_structure(df)
        if not is_valid_df:
            raise HTTPException(status_code=400, detail=f"Invalid data structure: {error_msg}")
        
        # Clean and preprocess data
        processed_df, processing_summary = data_processor.clean_and_preprocess(df)
        
        # Generate data summary
        data_summary = data_processor.generate_data_summary(processed_df)
        
        # Create file info
        file_info = FileInfo(
            filename=file.filename,
            file_size=file_size,
            file_type=file_extension,
            upload_timestamp=datetime.now()
        )
        
        # Create session and cache data
        session_id = session_cache.create_session(file_info, data_summary, processed_df)
        
        # Schedule cleanup of temporary file
        background_tasks.add_task(cleanup_temp_file, temp_file_path)
        
        # Prepare response
        response = UploadResponse(
            message="File uploaded and processed successfully",
            session_id=session_id,
            file_info={
                "filename": file_info.filename,
                "file_size": file_info.file_size,
                "file_type": file_info.file_type,
                "upload_timestamp": file_info.upload_timestamp.isoformat(),
                "processing_warnings": warnings
            },
            data_summary={
                "total_rows": data_summary.total_rows,
                "columns": data_summary.columns,
                "date_range": data_summary.date_range,
                "total_amount": data_summary.total_amount,
                "categories": data_summary.categories[:10] if data_summary.categories else None,  # Limit to first 10
                "processing_summary": processing_summary
            }
        )
        
        logger.info(f"✅ File processed successfully. Session ID: {session_id}")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise
        
    except Exception as e:
        # Clean up temp file on error
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        
        logger.error(f"❌ Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def query_financial_data(request: QueryRequest):
    """
    Query financial data using natural language
    
    Args:
        request: Query request with session ID and natural language query
        
    Returns:
        QueryResponse with AI-generated insights
    """
    try:
        logger.info(f"🔍 Processing query: {request.query[:100]}...")
        
        # Validate inputs
        is_valid_session, session_error = data_validator.validate_session_id(request.session_id)
        if not is_valid_session:
            raise HTTPException(status_code=400, detail=session_error)
        
        is_valid_query, query_error = data_validator.validate_query_input(request.query)
        if not is_valid_query:
            raise HTTPException(status_code=400, detail=query_error)
        
        # Check if session exists
        session_data = session_cache.get_session_data(request.session_id)
        if not session_data:
            raise HTTPException(
                status_code=404, 
                detail="Session not found or expired. Please upload data again."
            )
        
        # Process query
        response = await query_engine.process_query(request.session_id, request.query)
        
        logger.info(f"✅ Query processed successfully with {response.confidence} confidence")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"❌ Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/insights/{session_id}")
async def get_automatic_insights(session_id: str):
    """
    Get automatic insights for uploaded financial data
    
    Args:
        session_id: Session identifier
        
    Returns:
        Automatic insights generated from the data
    """
    try:
        logger.info(f"💡 Generating insights for session: {session_id}")
        
        # Validate session ID
        is_valid_session, session_error = data_validator.validate_session_id(session_id)
        if not is_valid_session:
            raise HTTPException(status_code=400, detail=session_error)
        
        # Check if session exists
        session_data = session_cache.get_session_data(session_id)
        if not session_data:
            raise HTTPException(
                status_code=404, 
                detail="Session not found or expired. Please upload data again."
            )
        
        # Generate insights
        insights = await query_engine.generate_data_insights(session_id)
        
        logger.info("✅ Insights generated successfully")
        return JSONResponse(content=insights)
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"❌ Error generating insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")


@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """
    Get information about a session
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session information
    """
    try:
        # Validate session ID
        is_valid_session, session_error = data_validator.validate_session_id(session_id)
        if not is_valid_session:
            raise HTTPException(status_code=400, detail=session_error)
        
        # Get session data
        session_data = session_cache.get_session_data(session_id)
        if not session_data:
            raise HTTPException(
                status_code=404, 
                detail="Session not found or expired."
            )
        
        return {
            "session_id": session_data.session_id,
            "file_info": {
                "filename": session_data.file_info.filename,
                "file_size": session_data.file_info.file_size,
                "file_type": session_data.file_info.file_type,
                "upload_timestamp": session_data.file_info.upload_timestamp.isoformat()
            },
            "data_summary": {
                "total_rows": session_data.data_summary.total_rows,
                "total_columns": len(session_data.data_summary.columns),
                "columns": session_data.data_summary.columns,
                "date_range": session_data.data_summary.date_range,
                "total_amount": session_data.data_summary.total_amount,
                "categories": session_data.data_summary.categories
            },
            "created_at": session_data.created_at.isoformat(),
            "last_accessed": session_data.last_accessed.isoformat()
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"❌ Error getting session info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting session info: {str(e)}")


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session and its cached data
    
    Args:
        session_id: Session identifier
        
    Returns:
        Deletion confirmation
    """
    try:
        # Validate session ID
        is_valid_session, session_error = data_validator.validate_session_id(session_id)
        if not is_valid_session:
            raise HTTPException(status_code=400, detail=session_error)
        
        # Delete session
        deleted = session_cache.delete_session(session_id)
        
        if deleted:
            return {"message": f"Session {session_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"❌ Error deleting session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")


@router.get("/cache/stats")
async def get_cache_stats():
    """
    Get cache statistics (for monitoring/debugging)
    
    Returns:
        Cache statistics
    """
    try:
        stats = session_cache.get_cache_stats()
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error getting cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")


@router.post("/cache/cleanup")
async def cleanup_expired_sessions():
    """
    Manually trigger cleanup of expired sessions
    
    Returns:
        Cleanup confirmation
    """
    try:
        session_cache.cleanup_expired_sessions()
        
        # Also cleanup old storage files
        storage_cleaned = data_storage.cleanup_old_sessions(max_age_hours=24)
        
        stats = session_cache.get_cache_stats()
        
        return {
            "message": "Expired sessions cleaned up successfully",
            "storage_sessions_cleaned": storage_cleaned,
            "current_stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Error cleaning up sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error cleaning up sessions: {str(e)}")


@router.get("/storage/sessions")
async def list_stored_sessions():
    """
    List all sessions in persistent storage
    
    Returns:
        List of stored sessions
    """
    try:
        sessions = data_storage.list_sessions()
        storage_stats = data_storage.get_storage_stats()
        
        return {
            "stored_sessions": sessions,
            "total_count": len(sessions),
            "storage_stats": storage_stats
        }
        
    except Exception as e:
        logger.error(f"❌ Error listing stored sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing stored sessions: {str(e)}")


@router.get("/storage/stats")
async def get_storage_statistics():
    """
    Get detailed storage statistics
    
    Returns:
        Storage statistics
    """
    try:
        stats = data_storage.get_storage_stats()
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error getting storage stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting storage stats: {str(e)}")


# Background task functions
def cleanup_temp_file(file_path: str):
    """Background task to clean up temporary files"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            logger.info(f"🧹 Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.warning(f"⚠️ Could not clean up temporary file {file_path}: {str(e)}")

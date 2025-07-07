"""
Session caching utility for storing uploaded data

This module provides in-memory caching for user sessions and their data.
"""

import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import logging
from threading import Lock

from src.core.config import settings
from src.models.schemas import SessionInfo, FileInfo, DataSummary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SessionCache:
    """In-memory cache for user sessions and financial data"""
    
    def __init__(self):
        """Initialize the session cache"""
        self._sessions: Dict[str, SessionInfo] = {}
        self._dataframes: Dict[str, pd.DataFrame] = {}
        self._lock = Lock()
        logger.info("✅ Session cache initialized")
    
    def create_session(self, file_info: FileInfo, data_summary: DataSummary, df: pd.DataFrame) -> str:
        """
        Create a new session with uploaded data
        
        Args:
            file_info: Information about the uploaded file
            data_summary: Summary of the data
            df: The processed DataFrame
            
        Returns:
            Session ID
        """
        with self._lock:
            session_id = str(uuid.uuid4())
            
            session_info = SessionInfo(
                session_id=session_id,
                file_info=file_info,
                data_summary=data_summary,
                created_at=datetime.now(),
                last_accessed=datetime.now()
            )
            
            self._sessions[session_id] = session_info
            self._dataframes[session_id] = df.copy()
            
            logger.info(f"📦 Created session: {session_id}")
            return session_id
    
    def get_session_data(self, session_id: str) -> Optional[SessionInfo]:
        """
        Get session information
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionInfo if found, None otherwise
        """
        with self._lock:
            session_info = self._sessions.get(session_id)
            if session_info:
                # Check if session has expired
                if self._is_session_expired(session_info):
                    self._cleanup_session(session_id)
                    return None
                
                # Update last accessed time
                session_info.last_accessed = datetime.now()
                logger.info(f"📋 Retrieved session: {session_id}")
                return session_info
            
            logger.warning(f"⚠️ Session not found: {session_id}")
            return None
    
    def get_dataframe(self, session_id: str) -> Optional[pd.DataFrame]:
        """
        Get DataFrame for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            DataFrame if found, None otherwise
        """
        with self._lock:
            if session_id in self._sessions:
                session_info = self._sessions[session_id]
                
                # Check if session has expired
                if self._is_session_expired(session_info):
                    self._cleanup_session(session_id)
                    return None
                
                df = self._dataframes.get(session_id)
                if df is not None:
                    logger.info(f"📊 Retrieved DataFrame for session: {session_id}")
                    return df.copy()
            
            logger.warning(f"⚠️ DataFrame not found for session: {session_id}")
            return None
    
    def update_session_access(self, session_id: str):
        """
        Update the last accessed time for a session
        
        Args:
            session_id: Session identifier
        """
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].last_accessed = datetime.now()
                logger.debug(f"🔄 Updated access time for session: {session_id}")
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and its data
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if session_id in self._sessions:
                self._cleanup_session(session_id)
                logger.info(f"🗑️ Deleted session: {session_id}")
                return True
            return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions from cache"""
        with self._lock:
            expired_sessions = []
            
            for session_id, session_info in self._sessions.items():
                if self._is_session_expired(session_info):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                self._cleanup_session(session_id)
            
            if expired_sessions:
                logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_active_sessions_count(self) -> int:
        """Get the number of active sessions"""
        with self._lock:
            return len(self._sessions)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            return {
                "active_sessions": len(self._sessions),
                "cached_dataframes": len(self._dataframes),
                "cache_ttl_seconds": settings.CACHE_TTL,
                "timestamp": datetime.now().isoformat()
            }
    
    def _is_session_expired(self, session_info: SessionInfo) -> bool:
        """Check if a session has expired"""
        expiry_time = session_info.last_accessed + timedelta(seconds=settings.CACHE_TTL)
        return datetime.now() > expiry_time
    
    def _cleanup_session(self, session_id: str):
        """Clean up session data"""
        self._sessions.pop(session_id, None)
        self._dataframes.pop(session_id, None)


# Global session cache instance
session_cache = SessionCache()

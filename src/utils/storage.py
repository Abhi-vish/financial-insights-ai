"""
Storage utility for persistent data management

This module handles saving uploaded data and session information to disk.
"""

import pandas as pd
import json
import pickle
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import os

from src.models.schemas import SessionInfo, FileInfo, DataSummary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataStorage:
    """Storage manager for financial data and session information"""
    
    def __init__(self, base_path: str = "data"):
        """Initialize the storage manager"""
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        logger.info(f"✅ Data storage initialized at: {self.base_path.absolute()}")
    
    def create_session_directory(self, session_id: str) -> Path:
        """Create a directory for a session"""
        session_dir = self.base_path / session_id
        session_dir.mkdir(exist_ok=True)
        return session_dir
    
    def save_session_data(self, session_id: str, session_info: SessionInfo, df: pd.DataFrame) -> bool:
        """
        Save session data to disk
        
        Args:
            session_id: Session identifier
            session_info: Session information object
            df: DataFrame to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session_dir = self.create_session_directory(session_id)
            
            # Save session info as JSON
            session_info_path = session_dir / "session_info.json"
            session_data = {
                "session_id": session_info.session_id,
                "file_info": {
                    "filename": session_info.file_info.filename,
                    "file_size": session_info.file_info.file_size,
                    "file_type": session_info.file_info.file_type,
                    "upload_timestamp": session_info.file_info.upload_timestamp.isoformat()
                },
                "data_summary": {
                    "total_rows": session_info.data_summary.total_rows,
                    "columns": session_info.data_summary.columns,
                    "date_range": session_info.data_summary.date_range,
                    "total_amount": session_info.data_summary.total_amount,
                    "categories": session_info.data_summary.categories,
                    "data_types": session_info.data_summary.data_types
                },
                "created_at": session_info.created_at.isoformat(),
                "last_accessed": session_info.last_accessed.isoformat()
            }
            
            with open(session_info_path, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            # Save DataFrame as CSV
            csv_path = session_dir / "data.csv"
            df.to_csv(csv_path, index=False)
            
            # Save DataFrame as pickle for exact restoration
            pickle_path = session_dir / "data.pkl"
            df.to_pickle(pickle_path)
            
            # Save original file if it exists in temp
            original_file_path = session_dir / f"original_{session_info.file_info.filename}"
            
            logger.info(f"💾 Session data saved to: {session_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving session data: {str(e)}")
            return False
    
    def load_session_data(self, session_id: str) -> Optional[SessionInfo]:
        """
        Load session data from disk
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionInfo object if found, None otherwise
        """
        try:
            session_dir = self.base_path / session_id
            session_info_path = session_dir / "session_info.json"
            
            if not session_info_path.exists():
                return None
            
            with open(session_info_path, 'r') as f:
                session_data = json.load(f)
            
            # Reconstruct SessionInfo object
            file_info = FileInfo(
                filename=session_data["file_info"]["filename"],
                file_size=session_data["file_info"]["file_size"],
                file_type=session_data["file_info"]["file_type"],
                upload_timestamp=datetime.fromisoformat(session_data["file_info"]["upload_timestamp"])
            )
            
            data_summary = DataSummary(
                total_rows=session_data["data_summary"]["total_rows"],
                columns=session_data["data_summary"]["columns"],
                date_range=session_data["data_summary"]["date_range"],
                total_amount=session_data["data_summary"]["total_amount"],
                categories=session_data["data_summary"]["categories"],
                data_types=session_data["data_summary"]["data_types"]
            )
            
            session_info = SessionInfo(
                session_id=session_data["session_id"],
                file_info=file_info,
                data_summary=data_summary,
                created_at=datetime.fromisoformat(session_data["created_at"]),
                last_accessed=datetime.fromisoformat(session_data["last_accessed"])
            )
            
            logger.info(f"📂 Session data loaded from: {session_dir}")
            return session_info
            
        except Exception as e:
            logger.error(f"❌ Error loading session data: {str(e)}")
            return None
    
    def load_dataframe(self, session_id: str) -> Optional[pd.DataFrame]:
        """
        Load DataFrame from disk
        
        Args:
            session_id: Session identifier
            
        Returns:
            DataFrame if found, None otherwise
        """
        try:
            session_dir = self.base_path / session_id
            
            # Try to load from pickle first (preserves data types)
            pickle_path = session_dir / "data.pkl"
            if pickle_path.exists():
                df = pd.read_pickle(pickle_path)
                logger.info(f"📊 DataFrame loaded from pickle: {session_dir}")
                return df
            
            # Fallback to CSV
            csv_path = session_dir / "data.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                logger.info(f"📊 DataFrame loaded from CSV: {session_dir}")
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error loading DataFrame: {str(e)}")
            return None
    
    def delete_session_data(self, session_id: str) -> bool:
        """
        Delete session data from disk
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session_dir = self.base_path / session_id
            
            if session_dir.exists():
                import shutil
                shutil.rmtree(session_dir)
                logger.info(f"🗑️ Session data deleted: {session_dir}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error deleting session data: {str(e)}")
            return False
    
    def list_sessions(self) -> list:
        """
        List all stored sessions
        
        Returns:
            List of session IDs
        """
        try:
            sessions = []
            for item in self.base_path.iterdir():
                if item.is_dir() and (item / "session_info.json").exists():
                    sessions.append(item.name)
            
            logger.info(f"📋 Found {len(sessions)} stored sessions")
            return sessions
            
        except Exception as e:
            logger.error(f"❌ Error listing sessions: {str(e)}")
            return []
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics
        
        Returns:
            Storage statistics
        """
        try:
            sessions = self.list_sessions()
            total_size = 0
            
            for session_id in sessions:
                session_dir = self.base_path / session_id
                for file_path in session_dir.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
            
            return {
                "total_sessions": len(sessions),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "storage_path": str(self.base_path.absolute()),
                "sessions": sessions
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting storage stats: {str(e)}")
            return {"error": str(e)}
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up sessions older than specified hours
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of sessions cleaned up
        """
        try:
            cleaned_count = 0
            cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
            
            for session_id in self.list_sessions():
                session_dir = self.base_path / session_id
                
                # Check modification time of session directory
                if session_dir.stat().st_mtime < cutoff_time:
                    if self.delete_session_data(session_id):
                        cleaned_count += 1
            
            logger.info(f"🧹 Cleaned up {cleaned_count} old sessions")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up sessions: {str(e)}")
            return 0


# Global storage instance
data_storage = DataStorage()

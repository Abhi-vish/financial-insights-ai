"""
Data validation utilities

This module provides validation functions for financial data files and inputs.
"""

import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
import re
from pathlib import Path
import mimetypes
import logging

from src.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """Validator for financial data files and inputs"""
    
    def __init__(self):
        """Initialize the data validator"""
        self.supported_extensions = settings.ALLOWED_EXTENSIONS
        self.max_file_size = settings.MAX_FILE_SIZE
        logger.info("✅ Data validator initialized")
    
    def validate_file_upload(self, filename: str, file_size: int, content_type: str = None) -> Tuple[bool, str]:
        """
        Validate an uploaded file
        
        Args:
            filename: Name of the uploaded file
            file_size: Size of the file in bytes
            content_type: MIME type of the file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check filename
            if not filename:
                return False, "Filename is required"
            
            # Check file extension
            file_path = Path(filename)
            extension = file_path.suffix.lower()
            
            if extension not in self.supported_extensions:
                return False, f"Unsupported file format. Supported formats: {', '.join(self.supported_extensions)}"
            
            # Check file size
            if file_size <= 0:
                return False, "File appears to be empty"
            
            if file_size > self.max_file_size:
                max_size_mb = self.max_file_size / (1024 * 1024)
                return False, f"File size exceeds maximum limit of {max_size_mb:.1f}MB"
            
            # Check MIME type if provided
            if content_type:
                valid_mime_types = {
                    '.csv': ['text/csv', 'application/csv', 'text/plain'],
                    '.xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
                    '.xls': ['application/vnd.ms-excel']
                }
                
                expected_types = valid_mime_types.get(extension, [])
                if expected_types and content_type not in expected_types:
                    logger.warning(f"⚠️ MIME type mismatch: expected {expected_types}, got {content_type}")
                    # Don't fail on MIME type mismatch, just log it
            
            return True, "File validation passed"
            
        except Exception as e:
            logger.error(f"❌ File validation error: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    def validate_query_input(self, query: str) -> Tuple[bool, str]:
        """
        Validate user query input
        
        Args:
            query: User's natural language query
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if query is provided
            if not query:
                return False, "Query cannot be empty"
            
            # Check query length
            query = query.strip()
            if len(query) < 3:
                return False, "Query must be at least 3 characters long"
            
            if len(query) > 1000:
                return False, "Query cannot exceed 1000 characters"
            
            # Check for potentially malicious content
            suspicious_patterns = [
                r'<script.*?>.*?</script>',  # Script tags
                r'javascript:',              # JavaScript protocols
                r'vbscript:',               # VBScript protocols
                r'<iframe.*?>',             # Iframe tags
                r'<object.*?>',             # Object tags
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return False, "Query contains potentially unsafe content"
            
            return True, "Query validation passed"
            
        except Exception as e:
            logger.error(f"❌ Query validation error: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    def validate_session_id(self, session_id: str) -> Tuple[bool, str]:
        """
        Validate session ID format
        
        Args:
            session_id: Session identifier
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not session_id:
                return False, "Session ID is required"
            
            # Check UUID format (basic validation)
            uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            if not re.match(uuid_pattern, session_id, re.IGNORECASE):
                return False, "Invalid session ID format"
            
            return True, "Session ID validation passed"
            
        except Exception as e:
            logger.error(f"❌ Session ID validation error: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    def validate_dataframe_structure(self, df: pd.DataFrame) -> Tuple[bool, str, List[str]]:
        """
        Validate DataFrame structure for financial data
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, error_message, warnings)
        """
        try:
            warnings = []
            
            # Check if DataFrame is empty
            if df.empty:
                return False, "DataFrame is empty", []
            
            # Check minimum number of rows
            if len(df) < 1:
                return False, "DataFrame must have at least 1 row", []
            
            # Check maximum number of rows
            if len(df) > settings.MAX_ROWS_PROCESS:
                warnings.append(f"DataFrame has {len(df)} rows, will be truncated to {settings.MAX_ROWS_PROCESS}")
            
            # Check for reasonable number of columns
            if len(df.columns) == 0:
                return False, "DataFrame must have at least 1 column", []
            
            if len(df.columns) > 50:
                warnings.append(f"DataFrame has {len(df.columns)} columns, which is quite large")
            
            # Check for duplicate column names
            if df.columns.duplicated().any():
                duplicate_cols = df.columns[df.columns.duplicated()].tolist()
                warnings.append(f"Duplicate column names found: {duplicate_cols}")
            
            # Check for completely empty columns
            empty_cols = df.columns[df.isnull().all()].tolist()
            if empty_cols:
                warnings.append(f"Completely empty columns found: {empty_cols}")
            
            # Check data types
            self._validate_data_types(df, warnings)
            
            return True, "DataFrame validation passed", warnings
            
        except Exception as e:
            logger.error(f"❌ DataFrame validation error: {str(e)}")
            return False, f"Validation error: {str(e)}", []
    
    def _validate_data_types(self, df: pd.DataFrame, warnings: List[str]):
        """Validate data types in DataFrame"""
        try:
            # Check for object columns that might be numeric
            for col in df.select_dtypes(include=['object']).columns:
                # Try to convert to numeric
                numeric_values = pd.to_numeric(df[col], errors='coerce')
                non_null_count = numeric_values.count()
                total_count = len(df[col].dropna())
                
                if total_count > 0 and non_null_count / total_count > 0.8:
                    warnings.append(f"Column '{col}' appears to be numeric but stored as text")
            
            # Check for potential date columns
            for col in df.select_dtypes(include=['object']).columns:
                sample_values = df[col].dropna().head(10)
                date_like_count = 0
                
                for value in sample_values:
                    try:
                        pd.to_datetime(str(value))
                        date_like_count += 1
                    except:
                        pass
                
                if len(sample_values) > 0 and date_like_count / len(sample_values) > 0.7:
                    warnings.append(f"Column '{col}' appears to contain dates")
            
        except Exception as e:
            logger.warning(f"⚠️ Data type validation warning: {str(e)}")
    
    def suggest_column_mappings(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Suggest column mappings for financial data
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with suggested column mappings
        """
        suggestions = {
            'potential_date_columns': [],
            'potential_amount_columns': [],
            'potential_category_columns': [],
            'potential_description_columns': []
        }
        
        try:
            columns_lower = [col.lower() for col in df.columns]
            
            # Date column suggestions
            date_keywords = ['date', 'time', 'timestamp', 'day', 'month', 'year', 'created', 'transaction']
            for i, col_lower in enumerate(columns_lower):
                if any(keyword in col_lower for keyword in date_keywords):
                    suggestions['potential_date_columns'].append(df.columns[i])
            
            # Amount column suggestions
            amount_keywords = ['amount', 'value', 'price', 'cost', 'total', 'sum', 'balance', 'expense', 'income', 'debit', 'credit']
            for i, col_lower in enumerate(columns_lower):
                if any(keyword in col_lower for keyword in amount_keywords):
                    col_name = df.columns[i]
                    if pd.api.types.is_numeric_dtype(df[col_name]):
                        suggestions['potential_amount_columns'].append(col_name)
            
            # Category column suggestions
            category_keywords = ['category', 'type', 'class', 'group', 'tag', 'label', 'merchant', 'vendor']
            for i, col_lower in enumerate(columns_lower):
                if any(keyword in col_lower for keyword in category_keywords):
                    suggestions['potential_category_columns'].append(df.columns[i])
            
            # Description column suggestions
            desc_keywords = ['description', 'desc', 'detail', 'note', 'memo', 'comment', 'narrative', 'reference']
            for i, col_lower in enumerate(columns_lower):
                if any(keyword in col_lower for keyword in desc_keywords):
                    suggestions['potential_description_columns'].append(df.columns[i])
            
        except Exception as e:
            logger.warning(f"⚠️ Error generating column suggestions: {str(e)}")
        
        return suggestions


# Global validator instance
data_validator = DataValidator()

"""
Data processing service for financial data

This module handles CSV/Excel file processing, data cleaning,
and preparation for AI analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import re
from datetime import datetime
import logging
from pathlib import Path

from src.core.config import settings
from src.models.schemas import DataSummary, FileInfo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Service for processing financial data files"""
    
    def __init__(self):
        """Initialize the data processor"""
        self.supported_formats = {'.csv', '.xlsx', '.xls'}
        logger.info("✅ Data processor initialized")
    
    def validate_file(self, file_path: str, file_size: int) -> bool:
        """
        Validate uploaded file
        
        Args:
            file_path: Path to the uploaded file
            file_size: Size of the file in bytes
            
        Returns:
            True if file is valid, False otherwise
        """
        try:
            # Check file size
            if file_size > settings.MAX_FILE_SIZE:
                raise ValueError(f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE} bytes")
            
            # Check file extension
            file_extension = Path(file_path).suffix.lower()
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported file format. Supported formats: {self.supported_formats}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ File validation failed: {str(e)}")
            return False
    
    def read_financial_data(self, file_path: str) -> pd.DataFrame:
        """
        Read financial data from CSV or Excel file
        
        Args:
            file_path: Path to the data file
            
        Returns:
            Pandas DataFrame with the financial data
        """
        try:
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.csv':
                # Try different encodings and separators
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError("Could not read CSV file with any supported encoding")
                    
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            logger.info(f"✅ Successfully read file with {len(df)} rows and {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error reading file: {str(e)}")
            raise
    
    def detect_financial_columns(self, df: pd.DataFrame) -> Dict[str, Optional[str]]:
        """
        Detect financial-related columns in the DataFrame
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary mapping column types to column names
        """
        columns = df.columns.str.lower()
        detected = {
            'date': None,
            'amount': None,
            'category': None,
            'description': None
        }
        
        # Date column detection
        date_keywords = ['date', 'time', 'timestamp', 'day', 'month', 'year', 'created', 'transaction_date']
        for col in columns:
            if any(keyword in col for keyword in date_keywords):
                detected['date'] = df.columns[columns.get_loc(col)]
                break
        
        # Amount column detection
        amount_keywords = ['amount', 'value', 'price', 'cost', 'total', 'sum', 'balance', 'expense', 'income']
        for col in columns:
            if any(keyword in col for keyword in amount_keywords):
                # Check if column contains numeric data
                col_name = df.columns[columns.get_loc(col)]
                if pd.api.types.is_numeric_dtype(df[col_name]) or self._can_convert_to_numeric(df[col_name]):
                    detected['amount'] = col_name
                    break
        
        # Category column detection
        category_keywords = ['category', 'type', 'class', 'group', 'tag', 'label']
        for col in columns:
            if any(keyword in col for keyword in category_keywords):
                detected['category'] = df.columns[columns.get_loc(col)]
                break
        
        # Description column detection
        desc_keywords = ['description', 'desc', 'detail', 'note', 'memo', 'comment', 'narrative']
        for col in columns:
            if any(keyword in col for keyword in desc_keywords):
                detected['description'] = df.columns[columns.get_loc(col)]
                break
        
        logger.info(f"🔍 Detected columns: {detected}")
        return detected
    
    def clean_and_preprocess(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Clean and preprocess financial data
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Tuple of (cleaned DataFrame, processing summary)
        """
        try:
            original_rows = len(df)
            processing_summary = {
                'original_rows': original_rows,
                'columns_processed': [],
                'data_types_converted': {},
                'issues_found': []
            }
            
            # Detect financial columns
            detected_cols = self.detect_financial_columns(df)
            
            # Clean and convert date columns
            if detected_cols['date']:
                date_col = detected_cols['date']
                df[date_col] = self._clean_date_column(df[date_col])
                processing_summary['columns_processed'].append(f"Date: {date_col}")
                processing_summary['data_types_converted'][date_col] = 'datetime'
            
            # Clean and convert amount columns
            if detected_cols['amount']:
                amount_col = detected_cols['amount']
                df[amount_col] = self._clean_amount_column(df[amount_col])
                processing_summary['columns_processed'].append(f"Amount: {amount_col}")
                processing_summary['data_types_converted'][amount_col] = 'numeric'
            
            # Clean category columns
            if detected_cols['category']:
                category_col = detected_cols['category']
                df[category_col] = self._clean_category_column(df[category_col])
                processing_summary['columns_processed'].append(f"Category: {category_col}")
            
            # Remove rows with all NaN values
            df = df.dropna(how='all')
            
            # Limit rows if necessary
            if len(df) > settings.MAX_ROWS_PROCESS:
                df = df.head(settings.MAX_ROWS_PROCESS)
                processing_summary['issues_found'].append(f"Data truncated to {settings.MAX_ROWS_PROCESS} rows")
            
            processing_summary['final_rows'] = len(df)
            processing_summary['detected_columns'] = detected_cols
            
            logger.info(f"✅ Data preprocessing complete: {original_rows} → {len(df)} rows")
            return df, processing_summary
            
        except Exception as e:
            logger.error(f"❌ Error in data preprocessing: {str(e)}")
            raise
    
    def _clean_date_column(self, series: pd.Series) -> pd.Series:
        """Clean and convert date column"""
        try:
            # Try to parse dates with pandas
            return pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
        except Exception:
            return series
    
    def _clean_amount_column(self, series: pd.Series) -> pd.Series:
        """Clean and convert amount column"""
        try:
            # Remove currency symbols and commas
            if series.dtype == 'object':
                series = series.astype(str)
                series = series.str.replace(r'[$,€£¥]', '', regex=True)
                series = series.str.replace(',', '')
                series = series.str.strip()
            
            # Convert to numeric
            return pd.to_numeric(series, errors='coerce')
        except Exception:
            return series
    
    def _clean_category_column(self, series: pd.Series) -> pd.Series:
        """Clean category column"""
        try:
            return series.astype(str).str.strip().str.title()
        except Exception:
            return series
    
    def _can_convert_to_numeric(self, series: pd.Series) -> bool:
        """Check if a series can be converted to numeric"""
        try:
            pd.to_numeric(series.astype(str).str.replace(r'[$,€£¥]', '', regex=True), errors='raise')
            return True
        except:
            return False
    
    def generate_data_summary(self, df: pd.DataFrame) -> DataSummary:
        """
        Generate a summary of the processed data
        
        Args:
            df: Processed DataFrame
            
        Returns:
            DataSummary object
        """
        try:
            detected_cols = self.detect_financial_columns(df)
            
            # Basic info
            total_rows = len(df)
            columns = df.columns.tolist()
            data_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
            
            # Date range
            date_range = None
            if detected_cols['date'] and detected_cols['date'] in df.columns:
                date_col = df[detected_cols['date']]
                if pd.api.types.is_datetime64_any_dtype(date_col):
                    date_range = {
                        'start': str(date_col.min()),
                        'end': str(date_col.max())
                    }
            
            # Total amount
            total_amount = None
            if detected_cols['amount'] and detected_cols['amount'] in df.columns:
                amount_col = df[detected_cols['amount']]
                if pd.api.types.is_numeric_dtype(amount_col):
                    total_amount = float(amount_col.sum())
            
            # Categories
            categories = None
            if detected_cols['category'] and detected_cols['category'] in df.columns:
                categories = df[detected_cols['category']].dropna().unique().tolist()
            
            summary = DataSummary(
                total_rows=total_rows,
                columns=columns,
                date_range=date_range,
                total_amount=total_amount,
                categories=categories,
                data_types=data_types
            )
            
            logger.info(f"📊 Generated data summary: {total_rows} rows, {len(columns)} columns")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating data summary: {str(e)}")
            raise
    
    def convert_to_text_summary(self, df: pd.DataFrame) -> str:
        """
        Convert DataFrame to text summary for AI processing
        
        Args:
            df: Processed DataFrame
            
        Returns:
            Text summary of the data
        """
        try:
            detected_cols = self.detect_financial_columns(df)
            
            summary_parts = []
            
            # Basic statistics
            summary_parts.append(f"Financial Data Summary ({len(df)} records):")
            summary_parts.append("=" * 50)
            
            # Column information
            summary_parts.append(f"Columns: {', '.join(df.columns.tolist())}")
            
            # Date range
            if detected_cols['date'] and detected_cols['date'] in df.columns:
                date_col = df[detected_cols['date']]
                if pd.api.types.is_datetime64_any_dtype(date_col):
                    summary_parts.append(f"Date Range: {date_col.min()} to {date_col.max()}")
            
            # Amount statistics
            if detected_cols['amount'] and detected_cols['amount'] in df.columns:
                amount_col = df[detected_cols['amount']]
                if pd.api.types.is_numeric_dtype(amount_col):
                    summary_parts.append(f"Total Amount: {amount_col.sum():.2f}")
                    summary_parts.append(f"Average Amount: {amount_col.mean():.2f}")
                    summary_parts.append(f"Min Amount: {amount_col.min():.2f}")
                    summary_parts.append(f"Max Amount: {amount_col.max():.2f}")
            
            # Category breakdown
            if detected_cols['category'] and detected_cols['category'] in df.columns:
                category_col = detected_cols['category']
                category_summary = df.groupby(category_col).agg({
                    detected_cols['amount']: ['count', 'sum'] if detected_cols['amount'] else ['count']
                }).round(2)
                
                summary_parts.append("\nCategory Breakdown:")
                summary_parts.append(str(category_summary))
            
            # Sample records
            summary_parts.append(f"\nSample Records (first 5):")
            summary_parts.append(df.head().to_string())
            
            text_summary = "\n".join(summary_parts)
            
            # Truncate if too long
            if len(text_summary) > 8000:  # Keep reasonable length for AI processing
                text_summary = text_summary[:8000] + "\n... (truncated)"
            
            logger.info(f"📝 Generated text summary ({len(text_summary)} characters)")
            return text_summary
            
        except Exception as e:
            logger.error(f"❌ Error converting to text summary: {str(e)}")
            raise

"""
Query engine for processing financial data queries

This module orchestrates the data processing and AI analysis pipeline.
"""

import pandas as pd
from typing import Dict, Any, Optional
import logging
from datetime import datetime
from typing import List

from src.core.gemini_client import gemini_client
from src.services.data_processor import DataProcessor
from src.services.prompt_templates import PromptBuilder
from src.services.code_executor import CodeExecutor
from src.models.schemas import QueryResponse
from src.utils.cache import session_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryEngine:
    """Engine for processing financial data queries using AI"""
    
    def __init__(self):
        """Initialize the query engine"""
        self.data_processor = DataProcessor()
        self.prompt_builder = PromptBuilder()
        self.code_executor = CodeExecutor()
        logger.info("✅ Query engine initialized")
    
    async def process_query(self, session_id: str, query: str) -> QueryResponse:
        """
        Process a natural language query against financial data
        
        Args:
            session_id: Session identifier for cached data
            query: Natural language query from user
            
        Returns:
            QueryResponse with analysis results
        """
        try:
            logger.info(f"🔍 Processing query: {query[:100]}...")
            
            # Get cached data
            session_data = session_cache.get_session_data(session_id)
            if not session_data:
                raise ValueError(f"No data found for session {session_id}")
            
            # Get the processed DataFrame
            df = session_cache.get_dataframe(session_id)
            if df is None:
                raise ValueError(f"No DataFrame found for session {session_id}")
            
            # Check if this query requires code execution
            if self.code_executor.is_code_query(query):
                logger.info("🔧 Query requires code execution - generating and executing code")
                return await self._process_code_query(session_id, query, df)
            else:
                logger.info("🤖 Query uses AI analysis - generating text summary")
                return await self._process_ai_query(session_id, query, df)
                
        except Exception as e:
            logger.error(f"❌ Error processing query: {str(e)}")
            # Return error response
            return QueryResponse(
                query=query,
                answer=f"Error processing query: {str(e)}",
                insights=[],
                data_points={},
                confidence="low",
                limitations=f"Processing error: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def _process_code_query(self, session_id: str, query: str, df: pd.DataFrame) -> QueryResponse:
        """Process queries that require code execution"""
        try:
            # Get the CSV file path from storage
            from src.utils.storage import data_storage
            csv_file_path = data_storage.base_path / session_id / "data.csv"
            
            if not csv_file_path.exists():
                raise ValueError(f"CSV file not found for session {session_id}")
            
            # Convert path to string with proper formatting (avoid encoding issues)
            csv_file_path_str = str(csv_file_path).replace('\\', '/')
            logger.info(f"🔍 Using CSV file path: {csv_file_path_str}")
            
            # Generate code using Gemini
            code = self.code_executor.generate_code_from_query(query, df, csv_file_path_str)
            
            # Execute the code
            output, success = self.code_executor.execute_code(code)
            
            # Format response - only show output
            answer = self.code_executor.format_code_response(query, output, success)
            confidence = self.code_executor.get_code_confidence(query, success)
            
            # Extract insights from code execution
            insights = []
            if success and output:
                insights.append(f"Executed code analysis on complete dataset")
                insights.append(f"Data loaded from: {csv_file_path}")
                if "found" in output.lower():
                    insights.append("Specific records found in dataset")
            
            # Update session last accessed time
            session_cache.update_session_access(session_id)
            
            return QueryResponse(
                query=query,
                answer=answer,
                insights=insights,
                data_points={"execution_success": success, "code_generated": True},
                confidence=confidence,
                limitations="Analysis performed on complete dataset" if success else "Code execution failed",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Error in code query processing: {str(e)}")
            return QueryResponse(
                query=query,
                answer=f"Error in code execution: {str(e)}",
                insights=[],
                data_points={},
                confidence="low",
                limitations=f"Code execution error: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def _process_ai_query(self, session_id: str, query: str, df: pd.DataFrame) -> QueryResponse:
        """Process queries using AI analysis"""
        try:
            # Generate text summary of data for AI analysis
            data_text_summary = self.data_processor.convert_to_text_summary(df)
            
            # Build the prompt for AI analysis
            analysis_prompt = self.prompt_builder.build_analysis_prompt(data_text_summary, query)
            
            # Get AI analysis
            ai_response = await gemini_client.analyze_financial_data(data_text_summary, query)
            
            # Create response object
            response = QueryResponse(
                query=query,
                answer=ai_response.get('answer', 'Unable to generate answer'),
                insights=ai_response.get('insights', []),
                data_points=ai_response.get('data_points', {}),
                confidence=ai_response.get('confidence', 'medium'),
                limitations=ai_response.get('limitations'),
                timestamp=datetime.now()
            )
            
            # Update session last accessed time
            session_cache.update_session_access(session_id)
            
            logger.info(f"✅ AI query processed successfully with {response.confidence} confidence")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in AI query processing: {str(e)}")
            return QueryResponse(
                query=query,
                answer=f"Error in AI analysis: {str(e)}",
                insights=[],
                data_points={},
                confidence="low",
                limitations=f"AI processing error: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def generate_data_insights(self, session_id: str) -> Dict[str, Any]:
        """
        Generate automatic insights from financial data
        
        Args:
            session_id: Session identifier for cached data
            
        Returns:
            Dictionary containing various insights
        """
        try:
            logger.info(f"💡 Generating insights for session: {session_id}")
            
            # Get cached data
            session_data = session_cache.get_session_data(session_id)
            if not session_data:
                raise ValueError(f"No data found for session {session_id}")
            
            df = session_cache.get_dataframe(session_id)
            if df is None:
                raise ValueError(f"No DataFrame found for session {session_id}")
            
            # Generate text summary
            data_text_summary = self.data_processor.convert_to_text_summary(df)
            
            # Generate automatic insights using AI
            insights_prompt = self.prompt_builder.build_summary_prompt(data_text_summary)
            ai_summary = await gemini_client.generate_response(insights_prompt)
            
            # Calculate basic statistics
            detected_cols = self.data_processor.detect_financial_columns(df)
            basic_stats = self._calculate_basic_statistics(df, detected_cols)
            
            # Combine AI insights with statistical analysis
            insights = {
                'ai_summary': ai_summary,
                'basic_statistics': basic_stats,
                'data_quality': self._assess_data_quality(df, detected_cols),
                'recommendations': self._generate_recommendations(df, detected_cols),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("✅ Insights generated successfully")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error generating insights: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_basic_statistics(self, df: pd.DataFrame, detected_cols: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Calculate basic statistical measures"""
        stats = {}
        
        try:
            # Amount statistics
            if detected_cols['amount'] and detected_cols['amount'] in df.columns:
                amount_col = df[detected_cols['amount']]
                if pd.api.types.is_numeric_dtype(amount_col):
                    stats['amount_statistics'] = {
                        'total': float(amount_col.sum()),
                        'mean': float(amount_col.mean()),
                        'median': float(amount_col.median()),
                        'std': float(amount_col.std()),
                        'min': float(amount_col.min()),
                        'max': float(amount_col.max()),
                        'count': int(amount_col.count())
                    }
            
            # Category statistics
            if detected_cols['category'] and detected_cols['category'] in df.columns:
                category_col = df[detected_cols['category']]
                category_counts = category_col.value_counts()
                stats['category_statistics'] = {
                    'total_categories': len(category_counts),
                    'top_categories': category_counts.head(5).to_dict(),
                    'category_distribution': category_counts.to_dict()
                }
            
            # Date statistics
            if detected_cols['date'] and detected_cols['date'] in df.columns:
                date_col = df[detected_cols['date']]
                if pd.api.types.is_datetime64_any_dtype(date_col):
                    # Convert Period objects to strings for JSON serialization
                    monthly_counts = df.groupby(date_col.dt.to_period('M')).size()
                    monthly_counts_dict = {str(period): int(count) for period, count in monthly_counts.items()}
                    
                    stats['date_statistics'] = {
                        'earliest_date': str(date_col.min()),
                        'latest_date': str(date_col.max()),
                        'date_range_days': int((date_col.max() - date_col.min()).days),
                        'transactions_per_month': monthly_counts_dict
                    }
            
        except Exception as e:
            logger.warning(f"⚠️ Error calculating statistics: {str(e)}")
            stats['error'] = str(e)
        
        return stats
    
    def _assess_data_quality(self, df: pd.DataFrame, detected_cols: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Assess the quality of the financial data"""
        quality = {
            'total_rows': len(df),
            'missing_data': {},
            'data_types': {},
            'issues': []
        }
        
        try:
            # Check for missing data
            for col in df.columns:
                missing_count = df[col].isnull().sum()
                if missing_count > 0:
                    quality['missing_data'][col] = {
                        'count': int(missing_count),
                        'percentage': float(missing_count / len(df) * 100)
                    }
            
            # Check data types
            for col, dtype in df.dtypes.items():
                quality['data_types'][col] = str(dtype)
            
            # Identify potential issues
            if not detected_cols['amount']:
                quality['issues'].append("No amount column detected")
            if not detected_cols['date']:
                quality['issues'].append("No date column detected")
            if not detected_cols['category']:
                quality['issues'].append("No category column detected")
            
            # Check for duplicates
            duplicate_count = df.duplicated().sum()
            if duplicate_count > 0:
                quality['issues'].append(f"{duplicate_count} duplicate rows found")
            
        except Exception as e:
            logger.warning(f"⚠️ Error assessing data quality: {str(e)}")
            quality['error'] = str(e)
        
        return quality
    
    def _generate_recommendations(self, df: pd.DataFrame, detected_cols: Dict[str, Optional[str]]) -> List[str]:
        """Generate recommendations based on data analysis"""
        recommendations = []
        
        try:
            # Data completeness recommendations
            if not detected_cols['amount']:
                recommendations.append("Consider adding an 'amount' column for better financial analysis")
            if not detected_cols['date']:
                recommendations.append("Consider adding a 'date' column to track temporal patterns")
            if not detected_cols['category']:
                recommendations.append("Consider adding a 'category' column for expense categorization")
            
            # Data quality recommendations
            missing_data_threshold = 0.1  # 10%
            for col in df.columns:
                missing_pct = df[col].isnull().sum() / len(df)
                if missing_pct > missing_data_threshold:
                    recommendations.append(f"Column '{col}' has {missing_pct:.1%} missing data - consider data cleaning")
            
            # Analysis recommendations based on data size
            if len(df) < 10:
                recommendations.append("Dataset is very small - insights may be limited")
            elif len(df) > 1000:
                recommendations.append("Large dataset detected - consider time-based analysis for trends")
            
        except Exception as e:
            logger.warning(f"⚠️ Error generating recommendations: {str(e)}")
            recommendations.append(f"Error generating recommendations: {str(e)}")
        
        return recommendations

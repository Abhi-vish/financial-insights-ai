"""
Prompt templates for financial data analysis

This module contains pre-built prompt templates for common
financial data analysis tasks.
"""

from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptTemplates:
    """Collection of prompt templates for financial analysis"""
    
    @staticmethod
    def get_summary_template() -> str:
        """Template for generating general financial data summaries"""
        return """
Analyze the following financial data and provide a comprehensive summary.

INSTRUCTIONS:
- Summarize the total number of transactions
- Identify the date range covered
- Calculate total amounts (income vs expenses if distinguishable)
- List main categories and their totals
- Identify notable patterns, trends, or anomalies
- Highlight any data quality issues if found

FINANCIAL DATA:
{data_summary}

Please provide a clear, structured summary that gives stakeholders key insights about this financial data.
"""
    
    @staticmethod
    def get_category_analysis_template() -> str:
        """Template for category-based analysis"""
        return """
Analyze the spending categories in the provided financial data.

TASK: Provide detailed category analysis including:
1. Top spending categories by total amount
2. Category-wise transaction counts
3. Average transaction amount per category
4. Identify any unusual spending patterns
5. Suggest areas for potential cost optimization

FINANCIAL DATA:
{data_summary}

USER QUERY: {query}

Provide actionable insights about spending categories.
"""
    
    @staticmethod
    def get_time_analysis_template() -> str:
        """Template for time-based analysis"""
        return """
Analyze the temporal patterns in the provided financial data.

TASK: Provide time-based analysis including:
1. Monthly/weekly spending trends
2. Seasonal patterns if visible
3. Peak spending periods
4. Growth or decline trends over time
5. Irregular transaction patterns

FINANCIAL DATA:
{data_summary}

USER QUERY: {query}

Focus on temporal patterns and trends in the financial behavior.
"""
    
    @staticmethod
    def get_comparison_template() -> str:
        """Template for comparative analysis"""
        return """
Perform comparative analysis on the provided financial data.

TASK: Compare different aspects as requested:
1. Period-to-period comparisons
2. Category comparisons
3. Identify winners and losers
4. Percentage changes and growth rates
5. Relative performance metrics

FINANCIAL DATA:
{data_summary}

USER QUERY: {query}

Provide clear comparative insights with specific numbers and percentages.
"""
    
    @staticmethod
    def get_top_items_template() -> str:
        """Template for finding top/bottom items"""
        return """
Identify and analyze the top/bottom items in the financial data.

TASK: Find and analyze:
1. Highest/lowest amounts
2. Most frequent categories
3. Top spending days/periods
4. Outliers and anomalies
5. Ranking with clear metrics

FINANCIAL DATA:
{data_summary}

USER QUERY: {query}

Provide a ranked list with clear explanations and context.
"""
    
    @staticmethod
    def get_general_query_template() -> str:
        """Template for general financial queries"""
        return """
You are a financial data analyst AI. Answer the user's query about their financial data with precision and insight.

GUIDELINES:
1. Base your analysis ONLY on the provided data
2. Provide specific numbers, percentages, and calculations
3. Identify patterns and trends where relevant
4. If the query cannot be fully answered with available data, explain limitations
5. Offer actionable insights when possible

FINANCIAL DATA:
{data_summary}

USER QUERY: {query}

Provide a comprehensive answer that addresses the user's specific question.
"""
    
    @staticmethod
    def get_code_execution_template() -> str:
        """Template for queries that require code execution"""
        return """
You are a financial data analyst AI that can write and execute pandas code to answer specific questions.

TASK: The user is asking for specific information that requires searching the complete dataset.

GUIDELINES:
1. You will write pandas code to search the full dataset
2. Look for specific transactions, dates, or records
3. Use exact matching when possible
4. Provide clear, specific answers based on the actual data
5. If nothing is found, clearly state that

FINANCIAL DATA CONTEXT:
{data_summary}

USER QUERY: {query}

Write pandas code to find the specific information requested. The DataFrame is available as 'df'.
"""

    @staticmethod
    def detect_query_type(query: str) -> str:
        """
        Detect the type of query to select appropriate template
        
        Args:
            query: User's natural language query
            
        Returns:
            Query type identifier
        """
        query_lower = query.lower()
        
        # Code execution queries (specific data lookups)
        if any(word in query_lower for word in ['transaction id', 'transaction', 'T100', 'specific', 'exact', 'find', 'search', 'lookup', 'when did', 'what date', 'which date']):
            return 'code_execution'
        
        # Category-related queries
        elif any(word in query_lower for word in ['category', 'categories', 'type', 'types', 'spend on', 'spending on']):
            return 'category'
        
        # Time-related queries
        elif any(word in query_lower for word in ['month', 'monthly', 'week', 'weekly', 'year', 'yearly', 'time', 'trend', 'over time', 'seasonal']):
            return 'time'
        
        # Comparison queries
        elif any(word in query_lower for word in ['compare', 'comparison', 'vs', 'versus', 'difference', 'higher', 'lower', 'more', 'less']):
            return 'comparison'
        
        # Top/bottom queries
        elif any(word in query_lower for word in ['top', 'bottom', 'highest', 'lowest', 'most', 'least', 'maximum', 'minimum', 'best', 'worst']):
            return 'top_items'
        
        # Summary queries
        elif any(word in query_lower for word in ['summary', 'summarize', 'overview', 'total', 'overall']):
            return 'summary'
        
        # Default to general query
        else:
            return 'general'
    
    @staticmethod
    def get_template_for_query(query: str) -> str:
        """
        Get the appropriate template based on query type
        
        Args:
            query: User's natural language query
            
        Returns:
            Appropriate prompt template
        """
        query_type = PromptTemplates.detect_query_type(query)
        
        templates = {
            'code_execution': PromptTemplates.get_code_execution_template(),
            'category': PromptTemplates.get_category_analysis_template(),
            'time': PromptTemplates.get_time_analysis_template(),
            'comparison': PromptTemplates.get_comparison_template(),
            'top_items': PromptTemplates.get_top_items_template(),
            'summary': PromptTemplates.get_summary_template(),
            'general': PromptTemplates.get_general_query_template()
        }
        
        template = templates.get(query_type, PromptTemplates.get_general_query_template())
        logger.info(f"🎯 Selected template type: {query_type}")
        
        return template
    
    @staticmethod
    def format_prompt(template: str, data_summary: str, query: str = "") -> str:
        """
        Format a template with actual data
        
        Args:
            template: The prompt template
            data_summary: Financial data summary
            query: User query (if applicable)
            
        Returns:
            Formatted prompt
        """
        try:
            formatted_prompt = template.format(
                data_summary=data_summary,
                query=query
            )
            return formatted_prompt
        except KeyError as e:
            logger.warning(f"⚠️ Template formatting issue: {str(e)}")
            # Fallback to simple replacement
            formatted_prompt = template.replace('{data_summary}', data_summary)
            if query:
                formatted_prompt = formatted_prompt.replace('{query}', query)
            return formatted_prompt


class PromptBuilder:
    """Helper class for building custom prompts"""
    
    def __init__(self):
        self.templates = PromptTemplates()
    
    def build_analysis_prompt(self, data_summary: str, query: str) -> str:
        """
        Build a comprehensive analysis prompt
        
        Args:
            data_summary: Text summary of financial data
            query: User's natural language query
            
        Returns:
            Complete prompt for AI analysis
        """
        # Get appropriate template
        template = self.templates.get_template_for_query(query)
        
        # Format with data
        prompt = self.templates.format_prompt(template, data_summary, query)
        
        logger.info(f"🔨 Built analysis prompt ({len(prompt)} characters)")
        return prompt
    
    def build_summary_prompt(self, data_summary: str) -> str:
        """
        Build a summary prompt
        
        Args:
            data_summary: Text summary of financial data
            
        Returns:
            Summary prompt
        """
        template = self.templates.get_summary_template()
        prompt = self.templates.format_prompt(template, data_summary)
        
        logger.info(f"📋 Built summary prompt ({len(prompt)} characters)")
        return prompt

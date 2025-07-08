"""
Code execution module for financial data analysis

This module enables the AI agent to write and execute pandas code
for specific data queries that require full dataset access.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
import logging
import sys
from io import StringIO
import traceback
import re
from datetime import datetime
import warnings
import google.generativeai as genai
from src.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress pandas warnings for cleaner output
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)


class CodeExecutor:
    """Execute pandas code safely for financial data analysis"""
    
    def __init__(self):
        """Initialize the code executor"""
        self.allowed_imports = {
            'pandas': 'pd',
            'numpy': 'np',
            'datetime': 'datetime',
            're': 're'
        }
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        logger.info("✅ Code executor initialized")
    
    def is_code_query(self, query: str) -> bool:
        """
        Determine if a query requires code execution
        
        Args:
            query: User's natural language query
            
        Returns:
            True if query needs code execution
        """
        # Keywords that indicate specific data lookups
        code_indicators = [
            'specific', 'exact', 'find', 'search', 'lookup', 'locate', 
            'when did', 'what date', 'which date', 'on what date',
            'ID', 'reference', 'record', 'row', 'entry', 'item', 'individual',
            'show me', 'get me', 'retrieve', 'fetch', 'customer_id', 'customer id',
            'transaction_id', 'transaction id', 'this customer', 'this transaction',
            'of this', 'for this', 'spent amount', 'spending by'
        ]
        
        query_lower = query.lower()
        
        # Check for specific patterns that indicate code queries
        specific_patterns = [
            r'customer[_\s]+id[_\s]+[A-Z0-9]+',  # customer_id C356
            r'transaction[_\s]+id[_\s]+[A-Z0-9]+',  # transaction_id T100008
            r'id[_\s]+[A-Z0-9]+',  # ID C356
            r'[A-Z]\d+',  # C356, T100008
            r'this\s+customer',  # this customer
            r'this\s+transaction',  # this transaction
        ]
        
        # Check for keyword indicators
        has_keyword = any(indicator in query_lower for indicator in code_indicators)
        
        # Check for specific patterns using regex
        import re
        has_pattern = any(re.search(pattern, query_lower) for pattern in specific_patterns)
        
        result = has_keyword or has_pattern
        logger.info(f"🔍 Query analysis: '{query}' -> {'CODE' if result else 'AI'} (keyword: {has_keyword}, pattern: {has_pattern})")
        
        return result
    
    def generate_code_from_query(self, query: str, df: pd.DataFrame, file_path: str) -> str:
        """
        Generate complete pandas code using Gemini LLM for the given query.

        Args:
            query: User's natural language query
            df: DataFrame to analyze (for structure reference)
            file_path: Path to the CSV file

        Returns:
            Complete self-contained pandas code
        """
        try:
            # Create a dynamic prompt for Gemini
            code_prompt = f"""
    You are an expert Python data analyst and pandas programmer. 
    Your task is to carefully read the user's query and generate Python code that precisely answers it using pandas.

    IMPORTANT GUIDELINES:
    1. Always begin by importing pandas and loading the dataset:
        import pandas as pd
        df = pd.read_csv("{file_path}")
    2. Use ONLY print() statements to display final outputs. Avoid return statements or unnecessary intermediate prints.
    3. Dynamically determine which columns or values to search based on:
    - The query content
    - The provided DataFrame columns and sample data
    4. Handle edge cases gracefully (e.g., if no matching data is found, print a friendly message).
    5. Do NOT assume any hardcoded column names. Infer everything from the DataFrame.

    DATAFRAME INFORMATION:
    - Shape: {df.shape}
    - Columns: {list(df.columns)}
    - Sample data:
    {df.head(3).to_string()}

    USER QUERY:
    \"\"\"{query}\"\"\"

    YOUR TASK:
    - Analyze the query carefully to understand exactly what data needs to be retrieved.
    - Use the DataFrame's structure to determine appropriate columns and filtering logic.
    - Generate complete Python code that:
        a) Loads the CSV into a DataFrame
        b) Processes the data to fulfill the user's query
        c) Prints the results clearly
    - Ensure the code handles cases like missing columns or no matching rows.

    OUTPUT FORMAT:
    - Provide ONLY the complete executable Python code (no explanations, comments, or markdown).

    Now write the code below:
    """
            
            # Use Gemini to generate code
            response = self.model.generate_content(code_prompt)
            
            if response and hasattr(response, 'text') and response.text:
                # Clean up the generated code
                generated_code = response.text.strip()
                logger.info(f"🔍 Generated code from Gemini: {generated_code[:100]}...")  # Log first 100 chars
                
                # Remove markdown code blocks if present
                if generated_code.startswith('```'):
                    lines = generated_code.split('\n')
                    start_idx = 1 if lines[0].startswith('```') else 0
                    end_idx = len(lines) - 1 if lines[-1].strip() == '```' else len(lines)
                    generated_code = '\n'.join(lines[start_idx:end_idx])
                
                # Replace placeholder with actual file path (use raw string for Windows)
                # Normalize the path to handle Windows paths properly
                normalized_path = file_path.replace('\\', '/')
                generated_code = generated_code.replace('"file_path.csv"', f'r"{file_path}"')
                generated_code = generated_code.replace("'file_path.csv'", f"r'{file_path}'")
                
                logger.info(f"✅ Generated complete code using Gemini ({len(generated_code)} characters)")
                return generated_code
            
            else:
                logger.warning("❌ Gemini failed to generate code, using fallback")
                return self._generate_fallback_code(query, file_path)
                
        except Exception as e:
            logger.error(f"❌ Code generation error: {str(e)}")
            return self._generate_fallback_code(query, file_path)
    
    def _generate_fallback_code(self, query: str, file_path: str) -> str:
        """
        Generates fallback pandas code when the LLM is unable to understand or generate
        code for the provided query. This ensures there is always some output.

        Args:
            query: The original user query
            file_path: Path to the CSV file

        Returns:
            A simple Python pandas code string that loads and displays the data,
            prompting the user for more specific instructions.
        """
        fallback_code = f'''
        import pandas as pd

        df = pd.read_csv("{file_path}")

        print("Showing a preview of the data:")
        print(df.head())

        print("\\nCould not automatically generate code for the query: '{query}'.")
        print("Please clarify your request or specify the exact columns and filters you want.")
        '''

        return fallback_code

    def execute_code(self, code: str) -> Tuple[str, bool]:
        """
        Execute complete pandas code with file loading
        
        Args:
            code: Complete Python code to execute
            
        Returns:
            Tuple of (output, success)
        """
        try:
            if code.startswith('```'):
                lines = code.split('\n')
                start_idx = 1 if lines[0].startswith('```') else 0
                end_idx = len(lines) - 1 if lines[-1].strip() == '```' else len(lines)
                code = '\n'.join(lines[start_idx:end_idx])
            # Redirect stdout to capture print statements
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            # Create safe execution environment with all necessary built-ins
            safe_builtins = {
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'print': print,
                'min': min,
                'max': max,
                'sum': sum,
                'abs': abs,
                'round': round,
                'type': type,
                'isinstance': isinstance,
                'getattr': getattr,
                'hasattr': hasattr,
                'open': open,
                '__import__': __import__,  # Allow imports
            }
            
            # Allow pandas and numpy to be imported
            safe_globals = {
                '__builtins__': safe_builtins,
                'pd': pd,  # Make pandas available
                'np': np,  # Make numpy available
            }
            
            # Execute the complete code
            exec(code, safe_globals)
            
            # Restore stdout
            sys.stdout = old_stdout
            
            # Get the output
            output = captured_output.getvalue()
            
            if not output.strip():
                output = "Code executed successfully but no output was generated."
            
            logger.info(f"✅ Code executed successfully")
            return output, True
            
        except Exception as e:
            # Restore stdout
            sys.stdout = old_stdout
            
            error_msg = f"Execution error: {str(e)}"
            logger.error(f"❌ Code execution failed: {str(e)}")
            return error_msg, False
    
    def format_code_response(self, query: str, output: str, success: bool) -> str:
        """
        Format the response for code-based queries - show only output
        
        Args:
            query: Original query
            output: Execution output
            success: Whether execution was successful
            
        Returns:
            Formatted response (output only)
        """
        if success:
            return output.strip()
        else:
            return f"I couldn't process your query due to an error: {output}"
    
    def get_code_confidence(self, query: str, success: bool) -> str:
        """
        Determine confidence level for code-based queries
        
        Args:
            query: Original query
            success: Whether code execution was successful
            
        Returns:
            Confidence level
        """
        if not success:
            return "low"
        
        # High confidence for specific lookups
        if any(word in query.lower() for word in ['specific', 'exact', 'find', 'search']):
            return "high"
        
        # Medium confidence for general queries
        return "medium"

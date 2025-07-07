"""
Gemini AI Client for financial data analysis

This module provides the interface to Google's Gemini 2.0 Flash model
for processing financial data queries and generating insights.
"""

import google.generativeai as genai
from typing import Dict, Any, Optional
import json
import logging
from src.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Google's Gemini 2.0 Flash model"""
    
    def __init__(self):
        """Initialize the Gemini client"""
        try:
            # Configure the Gemini API
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            
            # Generation configuration for consistent outputs
            self.generation_config = {
                "temperature": 0.1,  # Lower temperature for more consistent financial analysis
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            logger.info(f"✅ Gemini client initialized with model: {settings.GEMINI_MODEL}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini client: {str(e)}")
            raise
    
    async def generate_response(self, prompt: str) -> str:
        """
        Generate a response from Gemini model
        
        Args:
            prompt: The input prompt for the model
            
        Returns:
            Generated response text
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                raise ValueError("Empty response from Gemini model")
                
        except Exception as e:
            logger.error(f"❌ Error generating response: {str(e)}")
            raise
    
    async def analyze_financial_data(self, data_summary: str, query: str) -> Dict[str, Any]:
        """
        Analyze financial data based on a summary and user query
        
        Args:
            data_summary: Text summary of the financial data
            query: User's natural language query
            
        Returns:
            Structured analysis results
        """
        try:
            # Create a comprehensive prompt for financial analysis
            prompt = self._create_analysis_prompt(data_summary, query)
            
            # Generate response
            response = await self.generate_response(prompt)
            
            # Parse the response to extract structured data
            analysis_result = self._parse_analysis_response(response, query)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing financial data: {str(e)}")
            raise
    
    def _create_analysis_prompt(self, data_summary: str, query: str) -> str:
        """Create a structured prompt for financial data analysis"""
        
        prompt = f"""
You are a financial data analyst AI. Analyze the provided financial data summary and answer the user's query with precision and clarity.

FINANCIAL DATA SUMMARY:
{data_summary}

USER QUERY: {query}

INSTRUCTIONS:
1. Analyze the data thoroughly to answer the user's query
2. Provide specific numbers, percentages, and trends where applicable
3. If the query asks for comparisons, provide clear comparative analysis
4. If trends are requested, identify patterns and explain them
5. Always base your analysis ONLY on the provided data
6. If the query cannot be answered with the available data, clearly state this

RESPONSE FORMAT:
Provide your response in the following JSON structure:
{{
    "query": "The original user query",
    "answer": "Direct answer to the query",
    "insights": [
        "Key insight 1",
        "Key insight 2",
        "Key insight 3"
    ],
    "data_points": {{
        "key_metric_1": "value",
        "key_metric_2": "value"
    }},
    "confidence": "high/medium/low",
    "limitations": "Any limitations in the analysis based on available data"
}}

Ensure your response is valid JSON and contains accurate financial analysis.
"""
        return prompt
    
    def _parse_analysis_response(self, response: str, original_query: str) -> Dict[str, Any]:
        """Parse the AI response into structured data"""
        try:
            # Try to extract JSON from the response
            # Look for JSON content between ```json and ``` or just parse the whole response
            response_clean = response.strip()
            
            # Handle cases where response is wrapped in markdown code blocks
            if "```json" in response_clean:
                start = response_clean.find("```json") + 7
                end = response_clean.find("```", start)
                if end != -1:
                    response_clean = response_clean[start:end].strip()
            elif response_clean.startswith("```") and response_clean.endswith("```"):
                response_clean = response_clean[3:-3].strip()
            
            # Try to parse as JSON
            try:
                parsed_response = json.loads(response_clean)
                return parsed_response
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response
                return {
                    "query": original_query,
                    "answer": response_clean,
                    "insights": [],
                    "data_points": {},
                    "confidence": "medium",
                    "limitations": "Response could not be parsed as structured data"
                }
                
        except Exception as e:
            logger.warning(f"⚠️ Error parsing response: {str(e)}")
            # Return a fallback structure
            return {
                "query": original_query,
                "answer": response,
                "insights": [],
                "data_points": {},
                "confidence": "low",
                "limitations": f"Error parsing response: {str(e)}"
            }
    
    async def summarize_financial_data(self, data_text: str) -> str:
        """
        Generate a summary of financial data
        
        Args:
            data_text: Raw financial data in text format
            
        Returns:
            Summary of the financial data
        """
        prompt = f"""
Analyze and summarize the following financial data. Provide a concise overview including:
1. Total number of transactions
2. Date range of the data
3. Total amounts (income vs expenses if applicable)
4. Main categories and their totals
5. Notable patterns or trends

FINANCIAL DATA:
{data_text}

Provide a clear, structured summary in paragraph form.
"""
        
        try:
            return await self.generate_response(prompt)
        except Exception as e:
            logger.error(f"❌ Error summarizing financial data: {str(e)}")
            raise


# Global Gemini client instance
gemini_client = GeminiClient()

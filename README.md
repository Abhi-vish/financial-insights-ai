# Financial Data AI Agent

A modular API-driven AI agent that processes financial data and provides intelligent insights using Google's Gemini 2.0 Flash model.

## Features

- Upload CSV/Excel files with financial data
- Natural language querying of financial data
- Structured JSON insights and summaries
- Data validation and preprocessing
- Session-based data caching
- RESTful API endpoints

## Project Structure

```
├── main.py                 # FastAPI application entry point
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py    # API route handlers
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py       # Configuration settings
│   │   └── gemini_client.py # Gemini AI client
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py      # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_processor.py # Data processing logic
│   │   ├── prompt_templates.py # LLM prompt templates
│   │   └── query_engine.py  # Query processing engine
│   └── utils/
│       ├── __init__.py
│       ├── validators.py   # Data validation utilities
│       └── cache.py        # Session caching
├── requirements.txt
└── README.md
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with your Gemini API key:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

3. Run the application:
```bash
python main.py
```

## API Endpoints

### POST /upload
Upload a CSV or Excel file with financial data.

### POST /query
Query the uploaded data using natural language.

## Example Usage

1. Upload financial data via `/upload` endpoint
2. Query with natural language: "Which month had the highest spending?"
3. Receive structured JSON insights

## Data Format

Expected columns in financial data:
- Date (various formats supported)
- Amount (numeric)
- Category (text)
- Description (optional, text)

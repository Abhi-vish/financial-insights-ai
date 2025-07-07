# Financial Data AI Agent - Implementation Guide

## 🎯 Project Overview

A modular API-driven AI agent that processes financial data (CSV/Excel) and provides intelligent insights using Google's Gemini 2.0 Flash model. Built with core Python libraries without using pre-built frameworks like LangChain or CrewAI.

## 🏗️ Architecture

### Core Components

1. **FastAPI Application (`main.py`)**
   - REST API server with CORS support
   - Health checks and endpoint routing
   - Async request handling

2. **Configuration Management (`src/core/config.py`)**
   - Environment variable management
   - Application settings and defaults
   - API key validation

3. **Gemini AI Client (`src/core/gemini_client.py`)**
   - Direct integration with Gemini 2.0 Flash
   - Prompt engineering and response parsing
   - Financial data analysis optimization

4. **Data Processing (`src/services/data_processor.py`)**
   - CSV/Excel file parsing and validation
   - Automatic column detection (date, amount, category)
   - Data cleaning and preprocessing

5. **Query Engine (`src/services/query_engine.py`)**
   - Natural language query processing
   - RAG implementation (data → text → prompt → LLM)
   - Statistical analysis integration

6. **Prompt Templates (`src/services/prompt_templates.py`)**
   - Pre-built prompts for common financial queries
   - Intelligent query type detection
   - Template formatting and customization

7. **Session Management (`src/utils/cache.py`)**
   - In-memory data caching per session
   - Automatic session expiry and cleanup
   - Thread-safe operations

8. **Data Validation (`src/utils/validators.py`)**
   - File format and size validation
   - Query input sanitization
   - DataFrame structure validation

## 🚀 Quick Start

### 1. Installation

```bash
# Clone/setup the project
cd e:\vcs_project

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

The `.env` file is already configured with your Gemini API key. If needed, you can modify:

```env
GEMINI_API_KEY=your_key_here
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### 3. Start the Server

```bash
# Option 1: Direct start
python main.py

# Option 2: Using startup script
python start.py

# Option 3: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test the API

```bash
# Run the test script
python test_api.py
```

## 📊 API Endpoints

### Upload Financial Data
```http
POST /api/v1/upload
Content-Type: multipart/form-data

# Upload CSV or Excel file
```

**Response:**
```json
{
    "message": "File uploaded and processed successfully",
    "session_id": "uuid-here",
    "file_info": {
        "filename": "data.csv",
        "file_size": 1024,
        "file_type": ".csv",
        "upload_timestamp": "2024-01-01T12:00:00"
    },
    "data_summary": {
        "total_rows": 100,
        "columns": ["Date", "Amount", "Category"],
        "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
        "total_amount": 15000.50,
        "categories": ["Groceries", "Rent", "Transportation"]
    }
}
```

### Query Financial Data
```http
POST /api/v1/query
Content-Type: application/json

{
    "session_id": "uuid-from-upload",
    "query": "Which month had the highest spending?"
}
```

**Response:**
```json
{
    "query": "Which month had the highest spending?",
    "answer": "Based on the data analysis, March had the highest spending...",
    "insights": [
        "March spending was 25% higher than average",
        "Main contributors were housing and transportation"
    ],
    "data_points": {
        "highest_month": "March",
        "amount": 2500.00,
        "percentage_above_average": 25
    },
    "confidence": "high",
    "timestamp": "2024-01-01T12:00:00"
}
```

### Get Automatic Insights
```http
GET /api/v1/insights/{session_id}
```

### Session Management
```http
GET /api/v1/session/{session_id}      # Get session info
DELETE /api/v1/session/{session_id}   # Delete session
GET /api/v1/cache/stats               # Cache statistics
```

## 💡 Sample Queries

The system handles various types of financial queries:

### Category Analysis
- "Which category had the highest spending?"
- "Show me spending breakdown by category"
- "What percentage of my budget went to groceries?"

### Time-based Analysis
- "Which month had the highest expenses?"
- "Show me spending trends over time"
- "Compare spending between Q1 and Q2"

### Comparative Analysis
- "Compare dining out vs groceries spending"
- "Which week had unusual spending patterns?"
- "Show me top 5 highest transactions"

### Summary Queries
- "Summarize my total expenses"
- "Give me an overview of my financial data"
- "What are the main spending patterns?"

## 🔧 Technical Implementation Details

### RAG Implementation
1. **Data Conversion**: DataFrame → structured text summary
2. **Prompt Injection**: Text summary + user query → comprehensive prompt
3. **LLM Processing**: Gemini 2.0 Flash analysis
4. **Response Parsing**: JSON extraction and validation

### Column Detection Algorithm
The system automatically detects financial columns using keyword matching:

- **Date columns**: date, time, timestamp, day, month, year
- **Amount columns**: amount, value, price, cost, total, expense, income
- **Category columns**: category, type, class, group, tag, label
- **Description columns**: description, detail, note, memo, comment

### Data Preprocessing Pipeline
1. File validation (format, size, content type)
2. DataFrame loading with encoding detection
3. Column type detection and conversion
4. Data cleaning (currency symbols, date parsing)
5. Missing data handling
6. Summary statistics generation

### Prompt Engineering
Templates are dynamically selected based on query analysis:

- **Category queries** → Category analysis template
- **Time queries** → Temporal analysis template
- **Comparison queries** → Comparative analysis template
- **Top/bottom queries** → Ranking template
- **General queries** → Flexible analysis template

### Session Management
- UUID-based session identifiers
- Configurable TTL (default: 1 hour)
- Thread-safe operations
- Automatic cleanup of expired sessions
- Memory usage optimization

## 🧪 Testing

### Sample Data
Use the included `sample_financial_data.csv` for testing:
- 29 transactions across 2 months
- Multiple categories (Groceries, Rent, Transportation, etc.)
- Various amounts and patterns

### Test Script
The `test_api.py` script performs comprehensive testing:
1. Health check
2. File upload
3. Query processing
4. Insights generation
5. Session management

## 🔒 Security Features

- Input validation and sanitization
- File type and size restrictions
- Query content filtering
- Session-based data isolation
- Temporary file cleanup
- No persistent data storage

## 🚀 Production Deployment

### Environment Variables
```env
GEMINI_API_KEY=your_production_key
HOST=0.0.0.0
PORT=8000
DEBUG=False
MAX_FILE_SIZE=10485760
CACHE_TTL=3600
MAX_ROWS_PROCESS=10000
```

### Performance Considerations
- File size limits (10MB default)
- Row processing limits (10,000 default)
- Session TTL configuration
- Memory usage monitoring
- Response time optimization

### Monitoring Endpoints
- `/health` - Application health check
- `/api/v1/cache/stats` - Cache statistics
- Built-in FastAPI metrics

## 🔄 Extension Points

### Custom Prompt Templates
Add new templates in `src/services/prompt_templates.py`:

```python
@staticmethod
def get_custom_template() -> str:
    return """
    Custom analysis prompt template...
    """
```

### Additional File Formats
Extend `DataProcessor` to support new formats:

```python
def read_custom_format(self, file_path: str) -> pd.DataFrame:
    # Implementation for new file format
    pass
```

### Enhanced AI Models
The Gemini client can be extended to support:
- Different model versions
- Custom generation parameters
- Multi-modal inputs (images, charts)

## 📝 API Documentation

When the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐛 Troubleshooting

### Common Issues

1. **GEMINI_API_KEY not found**
   - Check `.env` file exists and contains the key
   - Verify the key is valid

2. **File upload fails**
   - Check file format (CSV, Excel only)
   - Verify file size under 10MB
   - Ensure file contains data

3. **Query returns low confidence**
   - Data might be insufficient
   - Query might be too vague
   - Try more specific questions

4. **Session not found**
   - Sessions expire after 1 hour
   - Re-upload the file to create a new session

### Logs and Debugging
- All services use Python logging
- Check console output for detailed error messages
- Enable DEBUG=True for verbose logging

## 🎉 Success! 

Your Financial Data AI Agent is now ready to process financial data and provide intelligent insights using Gemini 2.0 Flash. The system is fully modular, built with core Python libraries, and provides a complete RAG implementation for financial data analysis.

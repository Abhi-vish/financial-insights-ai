# 🌐 Financial Data AI Agent - API Documentation

## Overview

The Financial Data AI Agent provides a comprehensive REST API built with FastAPI for financial data analysis using Google's Gemini 2.0 Flash model. This documentation covers all available endpoints, request/response formats, and usage examples.

## 📍 Base URL

```
http://localhost:8000
```

## 🔐 Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible on the local server.

## 📋 Content Type

All API requests expect and return JSON content unless specified otherwise.

```
Content-Type: application/json
```

## 🛠️ API Endpoints

### 📤 Data Upload & Management

#### Upload Financial Data
```http
POST /api/v1/upload
```

**Description**: Upload and process financial data files (CSV or Excel)

**Request**:
- **Content-Type**: `multipart/form-data`
- **Body**: 
  - `file` (required): Binary file data (CSV/Excel)

**Response**:
```json
{
  "message": "File uploaded and processed successfully",
  "session_id": "abc123-def456-ghi789",
  "file_info": {
    "filename": "financial_data.csv",
    "size": 1024000,
    "type": "text/csv",
    "upload_time": "2025-01-15T10:30:00Z"
  },
  "data_summary": {
    "rows": 1000,
    "columns": 5,
    "date_range": "2024-01-01 to 2024-12-31",
    "detected_columns": {
      "date": "Date",
      "amount": "Amount",
      "category": "Category"
    }
  }
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@financial_data.csv"
```

#### Get Session Information
```http
GET /api/v1/session/{session_id}
```

**Description**: Retrieve detailed information about a specific session

**Parameters**:
- `session_id` (path): Unique session identifier

**Response**:
```json
{
  "session_id": "abc123-def456-ghi789",
  "created_at": "2025-01-15T10:30:00Z",
  "file_info": {
    "filename": "financial_data.csv",
    "size": 1024000,
    "type": "text/csv"
  },
  "data_summary": {
    "rows": 1000,
    "columns": 5,
    "memory_usage": "2.5 MB"
  },
  "queries_count": 5,
  "last_accessed": "2025-01-15T11:45:00Z"
}
```

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/session/abc123-def456-ghi789"
```

#### Delete Session
```http
DELETE /api/v1/session/{session_id}
```

**Description**: Remove a session and all associated data

**Parameters**:
- `session_id` (path): Unique session identifier

**Response**:
```json
{
  "message": "Session deleted successfully",
  "session_id": "abc123-def456-ghi789",
  "deleted_files": ["data.csv", "data.pkl", "session_info.json"]
}
```

**Example**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/session/abc123-def456-ghi789"
```

### 🔍 Query & Analysis

#### Natural Language Query
```http
POST /api/v1/query
```

**Description**: Ask questions about your financial data using natural language

**Request Body**:
```json
{
  "question": "What is the total spending amount?",
  "session_id": "abc123-def456-ghi789"
}
```

**Response**:
```json
{
  "answer": "The total spending amount is $25,450.00 across all transactions.",
  "query_type": "ai_analysis",
  "session_id": "abc123-def456-ghi789",
  "execution_time": 1.23,
  "data_source": "summary",
  "insights": {
    "total_amount": 25450.00,
    "transaction_count": 1000,
    "average_transaction": 25.45
  }
}
```

**Code Execution Response** (for specific queries):
```json
{
  "answer": "Customer C356 spent $1,234.56 in total.",
  "query_type": "code_execution",
  "session_id": "abc123-def456-ghi789",
  "execution_time": 0.87,
  "data_source": "full_dataset",
  "code_generated": "df[df['customer_id'] == 'C356']['amount'].sum()",
  "code_result": 1234.56,
  "insights": {
    "customer_transactions": 15,
    "average_per_transaction": 82.30
  }
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "What is the total spending amount?",
       "session_id": "abc123-def456-ghi789"
     }'
```

#### Generate Automatic Insights
```http
GET /api/v1/insights/{session_id}
```

**Description**: Get comprehensive AI-generated insights for uploaded data

**Parameters**:
- `session_id` (path): Unique session identifier

**Response**:
```json
{
  "session_id": "abc123-def456-ghi789",
  "insights": {
    "summary": "Analysis of 1000 financial transactions from 2024",
    "key_metrics": {
      "total_amount": 25450.00,
      "transaction_count": 1000,
      "average_transaction": 25.45,
      "date_range": "2024-01-01 to 2024-12-31"
    },
    "patterns": [
      "Highest spending in December (holiday season)",
      "Regular weekly grocery spending pattern",
      "Monthly salary deposits of $4,200"
    ],
    "anomalies": [
      "Unusually high transaction of $2,500 on 2024-06-15",
      "No transactions recorded for the week of 2024-08-10"
    ],
    "recommendations": [
      "Consider budgeting for holiday expenses",
      "Review irregular large transactions",
      "Set up automated savings for consistent amounts"
    ]
  },
  "generated_at": "2025-01-15T11:45:00Z",
  "generation_time": 3.45
}
```

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/insights/abc123-def456-ghi789"
```

### 💾 Storage & Cache Management

#### List All Stored Sessions
```http
GET /api/v1/storage/sessions
```

**Description**: Get a list of all stored sessions with metadata

**Response**:
```json
{
  "sessions": [
    {
      "session_id": "abc123-def456-ghi789",
      "filename": "financial_data.csv",
      "created_at": "2025-01-15T10:30:00Z",
      "size": "2.5 MB",
      "rows": 1000,
      "last_accessed": "2025-01-15T11:45:00Z"
    },
    {
      "session_id": "xyz789-uvw456-rst123",
      "filename": "expenses_2024.xlsx",
      "created_at": "2025-01-14T14:20:00Z",
      "size": "1.8 MB",
      "rows": 750,
      "last_accessed": "2025-01-14T15:30:00Z"
    }
  ],
  "total_sessions": 2,
  "total_storage": "4.3 MB"
}
```

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/storage/sessions"
```

#### Get Storage Statistics
```http
GET /api/v1/storage/stats
```

**Description**: View storage usage and statistics

**Response**:
```json
{
  "storage_stats": {
    "total_sessions": 2,
    "total_files": 6,
    "total_size_mb": 4.3,
    "disk_usage": {
      "csv_files": "2.1 MB",
      "pickle_files": "1.8 MB",
      "json_files": "0.4 MB"
    }
  },
  "oldest_session": "2025-01-14T14:20:00Z",
  "newest_session": "2025-01-15T10:30:00Z",
  "data_directory": "/app/data"
}
```

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/storage/stats"
```

#### Get Cache Statistics
```http
GET /api/v1/cache/stats
```

**Description**: View memory cache usage and performance metrics

**Response**:
```json
{
  "cache_stats": {
    "active_sessions": 2,
    "memory_usage_mb": 15.7,
    "hit_rate": 0.85,
    "total_requests": 150,
    "cache_hits": 127,
    "cache_misses": 23
  },
  "performance": {
    "avg_response_time": 0.45,
    "fastest_query": 0.12,
    "slowest_query": 2.34
  }
}
```

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/cache/stats"
```

#### Cleanup Expired Sessions
```http
POST /api/v1/cache/cleanup
```

**Description**: Remove expired sessions from cache and storage

**Response**:
```json
{
  "message": "Cleanup completed successfully",
  "results": {
    "sessions_cleaned": 3,
    "memory_freed_mb": 8.2,
    "storage_freed_mb": 12.5,
    "files_deleted": 9
  },
  "remaining_sessions": 2,
  "cleanup_time": 1.45
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/cache/cleanup"
```

### 🔧 System Management

#### Health Check
```http
GET /health
```

**Description**: Check if the API server is running and healthy

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": "2 hours 34 minutes",
  "system": {
    "cpu_usage": 15.3,
    "memory_usage": 45.7,
    "disk_usage": 23.1
  },
  "services": {
    "gemini_api": "connected",
    "database": "healthy",
    "cache": "active"
  },
  "timestamp": "2025-01-15T12:00:00Z"
}
```

**Example**:
```bash
curl -X GET "http://localhost:8000/health"
```

#### Root Endpoint
```http
GET /
```

**Description**: Welcome message and API information

**Response**:
```json
{
  "message": "Welcome to Financial Data AI Agent API",
  "version": "1.0.0",
  "description": "A modular API-driven AI agent for financial data analysis using Gemini 2.0 Flash",
  "endpoints": {
    "documentation": "/docs",
    "openapi": "/openapi.json",
    "health": "/health"
  }
}
```

**Example**:
```bash
curl -X GET "http://localhost:8000/"
```

## 🚨 Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Invalid request format"
}
```

#### 404 Not Found
```json
{
  "detail": "Session not found"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "session_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error occurred"
}
```

## 📊 Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Default limit**: 100 requests per minute per IP
- **Upload limit**: 10 file uploads per hour per IP
- **Heavy queries**: 20 AI queries per minute per session

## 🔗 Integration Examples

### Python with requests
```python
import requests

# Upload file
files = {'file': open('financial_data.csv', 'rb')}
response = requests.post('http://localhost:8000/api/v1/upload', files=files)
session_id = response.json()['session_id']

# Query data
query_data = {
    'question': 'What is the total spending?',
    'session_id': session_id
}
response = requests.post('http://localhost:8000/api/v1/query', json=query_data)
print(response.json()['answer'])
```

### JavaScript with fetch
```javascript
// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('http://localhost:8000/api/v1/upload', {
  method: 'POST',
  body: formData
});

const uploadData = await uploadResponse.json();
const sessionId = uploadData.session_id;

// Query data
const queryResponse = await fetch('http://localhost:8000/api/v1/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    question: 'What is the total spending?',
    session_id: sessionId
  })
});

const queryData = await queryResponse.json();
console.log(queryData.answer);
```

### cURL Scripts
```bash
#!/bin/bash
# Upload and query script

# Upload file
echo "Uploading file..."
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@financial_data.csv")

# Extract session ID
SESSION_ID=$(echo $RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['session_id'])")

echo "Session ID: $SESSION_ID"

# Query data
echo "Querying data..."
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What is the total spending?\", \"session_id\": \"$SESSION_ID\"}"
```

## 📚 OpenAPI Specification

The complete OpenAPI 3.1 specification is available at:
- **Interactive Documentation**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **JSON Specification**: `http://localhost:8000/openapi.json`

## 🛠️ Development Tools

### Testing Endpoints
Use the built-in FastAPI testing interface at `/docs` to:
- Test endpoints interactively
- View request/response schemas
- Generate client code
- Export API specifications

### Monitoring
- **Health checks**: `/health` endpoint
- **Performance metrics**: `/api/v1/cache/stats`
- **Storage monitoring**: `/api/v1/storage/stats`

## 🔄 Versioning

Current API version: `v1`

All endpoints are prefixed with `/api/v1/` to support future versioning.


# AI Decision Service

AI-powered request analysis service for API Gateway.

## Features

- ✅ Request frequency analysis
- ✅ Bot detection via user agent
- ✅ Burst pattern detection
- ✅ Endpoint access pattern analysis
- ✅ Confidence scoring
- ✅ Threat level classification

## Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

## Running
```bash
# Development
python -m app.main

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /predict` - Analyze request and return decision
- `GET /health` - Health check
- `GET /stats` - Service statistics
- `GET /docs` - Interactive API documentation

## Testing
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "ipAddress": "192.168.1.100",
    "userAgent": "Mozilla/5.0",
    "method": "GET",
    "endpoint": "/api/products",
    "requestPath": "/api/products?page=1",
    "requestCount": 5,
    "timestamp": "2025-03-21T10:30:00"
  }'
```
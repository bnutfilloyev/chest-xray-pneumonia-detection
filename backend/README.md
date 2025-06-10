# Pneumonia Detection Backend

FastAPI-based backend for pneumonia detection using ONNX model inference.

## Requirements

- Python 3.11+
- PostgreSQL 13+
- ONNX Runtime

## Installation

```bash
pip install -r requirements.txt
```

## Environment Setup

Copy `.env.example` to `.env` and configure your environment variables.

## Database Setup

```bash
alembic upgrade head
```

## Running the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Features

- ONNX-based pneumonia detection
- Patient management
- Medical image processing
- Prediction history tracking
- User authentication and authorization
- HIPAA-compliant data handling

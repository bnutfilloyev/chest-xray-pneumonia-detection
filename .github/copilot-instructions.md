# Copilot Instructions for Pneumonia Detection Application

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is a medical AI application for pneumonia detection using chest X-ray images. The system consists of:

- **Backend**: FastAPI-based REST API with ONNX model inference
- **Frontend**: React-based web application for medical professionals
- **Database**: PostgreSQL for patient data and prediction history
- **ML Model**: ONNX optimized EfficientNetB0 for pneumonia detection

## Code Guidelines

### Backend Development
- Use FastAPI for REST API endpoints
- Follow async/await patterns for better performance
- Implement proper error handling and logging
- Use Pydantic models for request/response validation
- Follow HIPAA compliance guidelines for medical data
- Use SQLAlchemy for database operations
- Implement proper authentication and authorization

### Frontend Development
- Use React with TypeScript for type safety
- Follow Material-UI design patterns for medical applications
- Implement proper error boundaries and loading states
- Use React Query for server state management
- Follow accessibility guidelines (WCAG 2.1)
- Implement proper form validation
- Use secure file upload patterns for medical images

### Machine Learning
- Use ONNX Runtime for model inference
- Implement proper image preprocessing pipelines
- Follow medical AI best practices for model outputs
- Include confidence scores and uncertainty quantification
- Implement proper model validation and monitoring

### Security & Compliance
- Follow HIPAA compliance requirements
- Implement proper data encryption
- Use secure authentication (JWT tokens)
- Follow medical device software guidelines
- Implement audit logging for all medical decisions

### Testing
- Write comprehensive unit tests for all components
- Implement integration tests for API endpoints
- Include model performance tests
- Follow TDD practices for critical medical functionality

## Architecture Patterns
- Use dependency injection for service management
- Implement proper separation of concerns
- Follow clean architecture principles
- Use proper error handling and logging patterns
- Implement health checks and monitoring

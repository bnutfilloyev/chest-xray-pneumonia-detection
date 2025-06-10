#!/bin/bash

# Pneumonia Detection App - Verification Script
# This script verifies that the consolidated application is working correctly

echo "🔍 Pneumonia Detection App - Verification Started"
echo "=================================================="

# Check if backend is running
echo "📡 Checking Backend..."
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
    
    # Test API endpoints
    echo "📋 Testing API endpoints..."
    
    # Test health
    echo "  - Health endpoint:"
    curl -s http://localhost:8000/health | jq '.' 2>/dev/null || echo "    Response: $(curl -s http://localhost:8000/health)"
    
    # Test patients
    echo "  - Patients endpoint:"
    PATIENT_COUNT=$(curl -s http://localhost:8000/api/v1/patients/ | jq 'length' 2>/dev/null || echo "0")
    echo "    Current patients: $PATIENT_COUNT"
    
    # Test predictions
    echo "  - Predictions endpoint:"
    curl -s http://localhost:8000/api/v1/predictions/health | jq '.' 2>/dev/null || echo "    Response: $(curl -s http://localhost:8000/api/v1/predictions/health)"
    
else
    echo "❌ Backend is not running on http://localhost:8000"
fi

# Check if frontend is running
echo ""
echo "🌐 Checking Frontend..."
if curl -s http://localhost:3000/ > /dev/null; then
    echo "✅ Frontend is running on http://localhost:3000"
else
    echo "❌ Frontend is not running on http://localhost:3000"
fi

echo ""
echo "🔍 Verification Complete"
echo "======================="
echo "📖 For full details, see: CONSOLIDATION_COMPLETE.md"
echo "🚀 Access the app at: http://localhost:3000"

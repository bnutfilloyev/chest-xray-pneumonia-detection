#!/bin/bash

# Test script for Docker Compose setup
set -e

# pull from git
echo "🔄 Pulling latest changes from Git..."
git pull origin master || { echo "❌ Git pull failed"; exit 1; }

echo "🐳 Testing Docker Compose Setup..."

# Function to check if service is running
check_service() {
    local service=$1
    local port=$2
    local max_attempts=30
    local attempt=0
    
    echo "Checking $service on port $port..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:$port > /dev/null 2>&1; then
            echo "✅ $service is running on port $port"
            return 0
        fi
        
        echo "⏳ Waiting for $service... ($((attempt + 1))/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    echo "❌ $service failed to start on port $port"
    return 1
}

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose.dev.yml up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Test database
echo "🗄️  Testing database connection..."
docker-compose -f docker-compose.dev.yml exec -T db pg_isready -U postgres

# Test backend
echo "🔧 Testing backend API..."
check_service "Backend API" 8000

# Test frontend
echo "🖥️  Testing frontend..."
check_service "Frontend" 3000

# Test API endpoints
echo "🔍 Testing API endpoints..."
echo "Health check:"
curl -s http://localhost:8000/health || echo "❌ Health check failed"

echo "API docs:"
curl -s http://localhost:8000/docs > /dev/null && echo "✅ API docs accessible" || echo "❌ API docs failed"

# Display service status
echo "📊 Service Status:"
docker-compose -f docker-compose.dev.yml ps

echo "✅ All tests completed!"
echo ""
echo "📱 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📋 To stop services:"
echo "   docker-compose -f docker-compose.dev.yml down"

#!/bin/bash

# Comprehensive test script for Docker Compose setup with database initialization
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# pull from git
print_status "Pulling latest changes from Git..."
git pull origin master || { print_error "Git pull failed"; exit 1; }

print_status "Testing Docker Compose Setup with Database Initialization..."

# Function to check if service is running
check_service() {
    local service=$1
    local port=$2
    local max_attempts=30
    local attempt=0
    
    print_status "Checking $service on port $port..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:$port > /dev/null 2>&1; then
            print_success "$service is running on port $port"
            return 0
        fi
        
        echo "⏳ Waiting for $service... ($((attempt + 1))/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    print_error "$service failed to start on port $port"
    return 1
}

# Function to wait for database to be ready
wait_for_database() {
    local max_attempts=30
    local attempt=0
    
    print_status "Waiting for database to be ready..."
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f docker-compose.dev.yml exec -T db pg_isready -U postgres > /dev/null 2>&1; then
            print_success "Database is ready"
            return 0
        fi
        
        echo "⏳ Waiting for database... ($((attempt + 1))/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    print_error "Database failed to be ready"
    return 1
}

# Function to initialize database
initialize_database() {
    print_status "Initializing database tables..."
    
    if docker-compose -f docker-compose.dev.yml exec -T backend python scripts/init_db.py; then
        print_success "Database tables created successfully"
    else
        print_error "Failed to create database tables"
        return 1
    fi
}

# Function to generate mock data
generate_mock_data() {
    print_status "Generating mock data..."
    
    if docker-compose -f docker-compose.dev.yml exec -T backend python scripts/generate_mock_data.py; then
        print_success "Mock data generated successfully"
    else
        print_warning "Mock data generation failed, continuing anyway..."
    fi
}

# Start services
print_status "Starting services..."
docker-compose -f docker-compose.dev.yml up -d --build

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 15

# Wait for database to be ready
wait_for_database

# Initialize database
initialize_database

# Generate mock data
generate_mock_data

# Test backend
print_status "Testing backend API..."
check_service "Backend API" 8000

# Test frontend
print_status "Testing frontend..."
check_service "Frontend" 3000

# Test API endpoints
print_status "Testing API endpoints..."

echo "Health check:"
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    print_success "Health check passed"
else
    print_error "Health check failed"
fi

echo "API docs:"
if curl -s http://localhost:8000/docs > /dev/null; then
    print_success "API docs accessible"
else
    print_error "API docs failed"
fi

# Test specific API endpoints
print_status "Testing database API endpoints..."

echo "Testing patients endpoint:"
if curl -s http://localhost:8000/api/v1/patients/ > /dev/null; then
    print_success "Patients API working"
else
    print_warning "Patients API may not be ready yet"
fi

echo "Testing predictions endpoint:"
if curl -s http://localhost:8000/api/v1/predictions/predictions > /dev/null; then
    print_success "Predictions API working"
else
    print_warning "Predictions API may not be ready yet"
fi

echo "Testing stats endpoint:"
if curl -s http://localhost:8000/api/v1/stats/weekly?weeks=4 > /dev/null; then
    print_success "Stats API working"
else
    print_warning "Stats API may not be ready yet"
fi

# Display service status
print_status "Service Status:"
docker-compose -f docker-compose.dev.yml ps

# Show database stats
print_status "Database Statistics:"
echo "Patients count:"
docker-compose -f docker-compose.dev.yml exec -T db psql -U postgres -d pneumonia_detection -c "SELECT COUNT(*) FROM patients;" 2>/dev/null || echo "  Database query failed"

echo "Predictions count:"
docker-compose -f docker-compose.dev.yml exec -T db psql -U postgres -d pneumonia_detection -c "SELECT COUNT(*) FROM predictions;" 2>/dev/null || echo "  Database query failed"

echo "Tables in database:"
docker-compose -f docker-compose.dev.yml exec -T db psql -U postgres -d pneumonia_detection -c "\dt" 2>/dev/null || echo "  Database query failed"

print_success "All tests completed!"
echo ""
print_status "Access your application:"
echo "   🌐 Frontend: http://localhost:3000"
echo "   🔧 Backend API: http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo "   🗄️  Database: localhost:5432 (pneumonia_detection)"
echo ""
print_status "Useful commands:"
echo "   📊 View logs: docker-compose -f docker-compose.dev.yml logs -f [service]"
echo "   � Restart service: docker-compose -f docker-compose.dev.yml restart [service]"
echo "   🛑 Stop services: docker-compose -f docker-compose.dev.yml down"
echo "   🗑️  Reset everything: docker-compose -f docker-compose.dev.yml down -v"
echo ""
print_status "To regenerate mock data:"
echo "   docker-compose -f docker-compose.dev.yml exec backend python scripts/generate_mock_data.py"

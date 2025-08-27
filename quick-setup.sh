#!/bin/bash

# Quick Setup Script for Pneumonia Detection Application
# This script will quickly start the application with mock data

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "   🩺 Pneumonia Detection Application Setup"
    echo "=================================================="
    echo -e "${NC}"
}

print_status() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_header

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_success "Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose not found. Please install docker-compose."
    exit 1
fi

print_success "docker-compose is available"

# Stop any existing containers
print_status "Stopping any existing containers..."
docker-compose -f docker-compose.dev.yml down -v > /dev/null 2>&1 || true

# Start services
print_status "Starting all services (this may take a few minutes)..."
docker-compose -f docker-compose.dev.yml up -d --build

# Wait for services
print_status "Waiting for services to be ready..."
sleep 20

# Check if database is ready
print_status "Checking database connection..."
for i in {1..30}; do
    if docker-compose -f docker-compose.dev.yml exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        print_success "Database is ready"
        break
    fi
    echo "  Waiting for database... ($i/30)"
    sleep 2
done

# Initialize database
print_status "Setting up database tables..."
docker-compose -f docker-compose.dev.yml exec -T backend python scripts/init_db.py

# Install faker for mock data (if not already installed)
print_status "Installing required packages..."
docker-compose -f docker-compose.dev.yml exec -T backend pip install faker > /dev/null 2>&1

# Generate mock data
print_status "Generating mock data..."
docker-compose -f docker-compose.dev.yml exec -T -e DOCKER_ENV=true backend python scripts/generate_mock_data.py

# Test API endpoints
print_status "Testing API endpoints..."
sleep 5

# Check backend health
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend API is responsive"
        break
    fi
    echo "  Waiting for backend... ($i/10)"
    sleep 2
done

# Check frontend
for i in {1..10}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend is responsive"
        break
    fi
    echo "  Waiting for frontend... ($i/10)"
    sleep 2
done

# Show final status
echo ""
echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Application Statistics:${NC}"

# Get database stats
patients_count=$(docker-compose -f docker-compose.dev.yml exec -T db psql -U postgres -d pneumonia_detection -c "SELECT COUNT(*) FROM patients;" -t 2>/dev/null | tr -d ' ' || echo "Unknown")
predictions_count=$(docker-compose -f docker-compose.dev.yml exec -T db psql -U postgres -d pneumonia_detection -c "SELECT COUNT(*) FROM predictions;" -t 2>/dev/null | tr -d ' ' || echo "Unknown")

echo "   • Patients: $patients_count"
echo "   • Predictions: $predictions_count"
echo ""

echo -e "${BLUE}🌐 Access your application:${NC}"
echo "   • Frontend:     http://localhost:3000"
echo "   • Backend API:  http://localhost:8000"
echo "   • API Docs:     http://localhost:8000/docs"
echo "   • Database:     localhost:5432 (pneumonia_detection)"
echo ""

echo -e "${BLUE}🛠️  Useful commands:${NC}"
echo "   • View logs:           docker-compose -f docker-compose.dev.yml logs -f [service]"
echo "   • Restart service:     docker-compose -f docker-compose.dev.yml restart [service]"
echo "   • Stop all:            docker-compose -f docker-compose.dev.yml down"
echo "   • Full reset:          docker-compose -f docker-compose.dev.yml down -v"
echo "   • Add more mock data:  docker-compose -f docker-compose.dev.yml exec backend python scripts/generate_mock_data.py"
echo ""

echo -e "${YELLOW}💡 Tips:${NC}"
echo "   • The database persists data between restarts"
echo "   • Use 'docker-compose -f docker-compose.dev.yml down -v' to reset everything"
echo "   • Check 'docker-compose -f docker-compose.dev.yml ps' to see service status"
echo ""

print_success "Ready to use! 🚀"

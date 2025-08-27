#!/bin/bash

# Status checker for Pneumonia Detection Application
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "   🏥 Pneumonia Detection Application Status"
    echo "=================================================="
    echo -e "${NC}"
}

print_section() {
    echo ""
    echo -e "${BLUE}📊 $1${NC}"
    echo "----------------------------------------"
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

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_header

# Check Docker services
print_section "Docker Services Status"

if command -v docker-compose &> /dev/null; then
    services=$(docker-compose -f docker-compose.dev.yml ps --services 2>/dev/null || echo "")
    if [ -n "$services" ]; then
        docker-compose -f docker-compose.dev.yml ps
    else
        print_warning "No Docker services running"
        echo "Run './quick-setup.sh' to start all services"
    fi
else
    print_error "docker-compose not found"
fi

# Check API endpoints
print_section "API Health Status"

# Backend health check
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    health_status=$(curl -s http://localhost:8000/health | jq -r '.status' 2>/dev/null || echo "unknown")
    print_success "Backend API: $health_status"
else
    print_error "Backend API: Not responding"
fi

# Frontend check
if curl -s http://localhost:3000 >/dev/null 2>&1; then
    print_success "Frontend: Responding"
else
    print_error "Frontend: Not responding"
fi

# Database check
if docker-compose -f docker-compose.dev.yml exec -T db pg_isready -U postgres >/dev/null 2>&1; then
    print_success "Database: Ready"
else
    print_error "Database: Not ready"
fi

# Check database content
print_section "Database Statistics"

if docker-compose -f docker-compose.dev.yml exec -T db psql -U postgres -d pneumonia_detection -c "SELECT 1;" >/dev/null 2>&1; then
    patients=$(docker-compose -f docker-compose.dev.yml exec -T db psql -U postgres -d pneumonia_detection -c "SELECT COUNT(*) FROM patients;" -t 2>/dev/null | tr -d ' ' || echo "0")
    predictions=$(docker-compose -f docker-compose.dev.yml exec -T db psql -U postgres -d pneumonia_detection -c "SELECT COUNT(*) FROM predictions;" -t 2>/dev/null | tr -d ' ' || echo "0")
    audit_logs=$(docker-compose -f docker-compose.dev.yml exec -T db psql -U postgres -d pneumonia_detection -c "SELECT COUNT(*) FROM audit_logs;" -t 2>/dev/null | tr -d ' ' || echo "0")
    
    echo "   • Patients: $patients"
    echo "   • Predictions: $predictions"
    echo "   • Audit Logs: $audit_logs"
    
    if [ "$patients" -gt 0 ] && [ "$predictions" -gt 0 ]; then
        print_success "Mock data is present"
    else
        print_warning "No mock data found"
        echo "   Run: docker-compose -f docker-compose.dev.yml exec backend python scripts/generate_mock_data.py"
    fi
else
    print_error "Cannot connect to database"
fi

# Check API endpoints functionality
print_section "API Endpoints Test"

endpoints=(
    "/health:Health Check"
    "/api/v1/patients/?limit=1:Patients API"
    "/api/v1/predictions/stats/overview:Stats API"
    "/docs:API Documentation"
)

for endpoint_info in "${endpoints[@]}"; do
    IFS=':' read -r endpoint name <<< "$endpoint_info"
    if curl -s "http://localhost:8000$endpoint" >/dev/null 2>&1; then
        print_success "$name"
    else
        print_error "$name"
    fi
done

# Access URLs
print_section "Access URLs"
echo "   🌐 Frontend:     http://localhost:3000"
echo "   🔧 Backend API:  http://localhost:8000"
echo "   📚 API Docs:     http://localhost:8000/docs"
echo "   🗄️  Database:     localhost:5432 (pneumonia_detection)"

# Useful commands
print_section "Useful Commands"
echo "   📊 Check status:         ./status.sh"
echo "   🚀 Quick setup:          ./quick-setup.sh"
echo "   🧪 Full test:            ./test-docker-setup.sh"
echo "   📋 View logs:            docker-compose -f docker-compose.dev.yml logs -f [service]"
echo "   🔄 Restart service:      docker-compose -f docker-compose.dev.yml restart [service]"
echo "   🛑 Stop all:             docker-compose -f docker-compose.dev.yml down"
echo "   🗑️  Reset everything:     docker-compose -f docker-compose.dev.yml down -v"

echo ""
if curl -s http://localhost:8000/health >/dev/null 2>&1 && curl -s http://localhost:3000 >/dev/null 2>&1; then
    print_success "Application is running and ready to use! 🎉"
else
    print_warning "Application is not fully running. Run './quick-setup.sh' to start."
fi

echo ""

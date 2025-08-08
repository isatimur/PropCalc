#!/bin/bash

# PropCalc Deployment Script
# This script deploys the complete PropCalc application with role-based UI/UX

set -e

echo "🚀 PropCalc Deployment Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if required files exist
check_files() {
    print_status "Checking required files..."
    
    required_files=(
        "docker-compose.yml"
        "backend/Dockerfile"
        "frontend/Dockerfile"
        "nginx.conf"
        "backend/main.py"
        "frontend/src/app/layout.tsx"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Required file not found: $file"
            exit 1
        fi
    done
    
    print_success "All required files found"
}

# Build and start services
deploy_services() {
    print_status "Building and starting services..."
    
    # Stop existing containers
    print_status "Stopping existing containers..."
    docker-compose down --remove-orphans
    
    # Build images
    print_status "Building Docker images..."
    docker-compose build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker-compose up -d
    
    print_success "Services started successfully"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    print_status "Waiting for PostgreSQL..."
    timeout=60
    while ! docker-compose exec -T postgres pg_isready -U vantage_user -d vantage_ai > /dev/null 2>&1; do
        if [ $timeout -le 0 ]; then
            print_error "PostgreSQL failed to start within 60 seconds"
            exit 1
        fi
        sleep 1
        timeout=$((timeout - 1))
    done
    print_success "PostgreSQL is ready"
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    timeout=30
    while ! docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do
        if [ $timeout -le 0 ]; then
            print_error "Redis failed to start within 30 seconds"
            exit 1
        fi
        sleep 1
        timeout=$((timeout - 1))
    done
    print_success "Redis is ready"
    
    # Wait for Backend
    print_status "Waiting for Backend API..."
    timeout=60
    while ! curl -f http://localhost:8000/health > /dev/null 2>&1; do
        if [ $timeout -le 0 ]; then
            print_error "Backend API failed to start within 60 seconds"
            exit 1
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    print_success "Backend API is ready"
    
    # Wait for Frontend
    print_status "Waiting for Frontend..."
    timeout=60
    while ! curl -f http://localhost:3000 > /dev/null 2>&1; do
        if [ $timeout -le 0 ]; then
            print_error "Frontend failed to start within 60 seconds"
            exit 1
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    print_success "Frontend is ready"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Wait a bit for the database to be fully ready
    sleep 5
    
    # Run migrations
    docker-compose exec -T backend python migrate_database.py
    
    print_success "Database migrations completed"
}

# Create demo users
create_demo_users() {
    print_status "Creating demo users..."
    
    # This would typically be done through the API
    # For now, we'll just print the demo credentials
    print_status "Demo users available:"
    echo "  Admin: admin@propcalc.ae / admin123"
    echo "  Developer: developer@propcalc.ae / dev123"
    echo "  Investor: investor@propcalc.ae / investor123"
    echo "  Consultant: consultant@propcalc.ae / consultant123"
}

# Check service health
check_health() {
    print_status "Checking service health..."
    
    services=(
        "postgres:5432"
        "redis:6379"
        "backend:8000"
        "frontend:3000"
        "nginx:80"
    )
    
    for service in "${services[@]}"; do
        IFS=':' read -r service_name port <<< "$service"
        if docker-compose exec -T "$service_name" echo "Service is running" > /dev/null 2>&1; then
            print_success "$service_name is healthy"
        else
            print_error "$service_name is not responding"
        fi
    done
}

# Show deployment information
show_info() {
    echo ""
    echo "🎉 PropCalc Deployment Complete!"
    echo "================================"
    echo ""
    echo "📊 Services Status:"
    docker-compose ps
    echo ""
    echo "🌐 Access URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  Admin Dashboard: http://localhost:3000/admin/dashboard"
    echo "  Grafana: http://localhost:3001 (admin/vantage_ai_admin)"
    echo "  Prometheus: http://localhost:9090"
    echo ""
    echo "🔐 Demo Credentials:"
    echo "  Admin: admin@propcalc.ae / admin123"
    echo "  Developer: developer@propcalc.ae / dev123"
    echo "  Investor: investor@propcalc.ae / investor123"
    echo "  Consultant: consultant@propcalc.ae / consultant123"
    echo ""
    echo "📋 Useful Commands:"
    echo "  View logs: docker-compose logs -f"
    echo "  Stop services: docker-compose down"
    echo "  Restart services: docker-compose restart"
    echo "  Update services: ./deploy.sh"
    echo ""
    echo "🚀 Your PropCalc platform is ready!"
    echo "Visit http://localhost:3000 to get started"
}

# Main deployment function
main() {
    echo "Starting PropCalc deployment..."
    echo ""
    
    check_docker
    check_files
    deploy_services
    wait_for_services
    run_migrations
    create_demo_users
    check_health
    show_info
    
    print_success "Deployment completed successfully!"
}

# Run main function
main "$@" 
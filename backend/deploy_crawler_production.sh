#!/bin/bash

# PropCalc Property Crawler Production Deployment Script
# Deploys the crawler system to production with comprehensive setup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="PropCalc Property Crawler"
VERSION="2.1.0"
ENVIRONMENT="production"

# Logging
LOG_FILE="crawler_deployment_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo -e "${BLUE}🚀 $PROJECT_NAME Production Deployment v$VERSION${NC}"
echo -e "${BLUE}================================================${NC}"
echo "📅 Deployment started: $(date)"
echo "🌍 Environment: $ENVIRONMENT"
echo "📁 Log file: $LOG_FILE"
echo ""

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "info") echo -e "${BLUE}ℹ️  $message${NC}" ;;
        "success") echo -e "${GREEN}✅ $message${NC}" ;;
        "warning") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        "error") echo -e "${RED}❌ $message${NC}" ;;
    esac
}

# Function to check prerequisites
check_prerequisites() {
    print_status "info" "Checking prerequisites..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_status "success" "Python $PYTHON_VERSION found"
    else
        print_status "error" "Python 3.11+ is required but not installed"
        exit 1
    fi
    
    # Check uv
    if command -v uv &> /dev/null; then
        print_status "success" "uv package manager found"
    else
        print_status "error" "uv package manager is required but not installed"
        exit 1
    fi
    
    # Check Docker
    if command -v docker &> /dev/null; then
        print_status "success" "Docker found"
    else
        print_status "warning" "Docker not found - some features may be limited"
    fi
    
    # Check environment file
    if [ -f ".env" ]; then
        print_status "success" "Environment file found"
    else
        print_status "warning" "No .env file found - using defaults"
    fi
}

# Function to install dependencies
install_dependencies() {
    print_status "info" "Installing Python dependencies..."
    
    if uv sync; then
        print_status "success" "Dependencies installed successfully"
    else
        print_status "error" "Failed to install dependencies"
        exit 1
    fi
}

# Function to run tests
run_tests() {
    print_status "info" "Running test suite..."
    
    # Run basic tests
    if uv run python -c "from propcalc.core.crawlers import CrawlerManager; print('✅ Basic imports working')"; then
        print_status "success" "Basic tests passed"
    else
        print_status "error" "Basic tests failed"
        exit 1
    fi
    
    # Run configuration tests
    if uv run python src/propcalc/config/crawler_config.py; then
        print_status "success" "Configuration tests passed"
    else
        print_status "error" "Configuration tests failed"
        exit 1
    fi
}

# Function to setup database
setup_database() {
    print_status "info" "Setting up database..."
    
    # Check if PostgreSQL is running
    if pg_isready -h localhost -p 5433 -U vantage_user -d vantage_ai &> /dev/null; then
        print_status "success" "PostgreSQL connection successful"
    else
        print_status "warning" "PostgreSQL not accessible - please start the database service"
        print_status "info" "You can start it with: docker-compose up -d postgres"
        return 1
    fi
    
    # Run Alembic migrations
    print_status "info" "Running database migrations..."
    if uv run alembic upgrade head; then
        print_status "success" "Database migrations completed"
    else
        print_status "error" "Database migrations failed"
        return 1
    fi
}

# Function to setup Redis
setup_redis() {
    print_status "info" "Setting up Redis..."
    
    # Check if Redis is running
    if redis-cli -h localhost -p 6380 ping &> /dev/null; then
        print_status "success" "Redis connection successful"
    else
        print_status "warning" "Redis not accessible - please start the Redis service"
        print_status "info" "You can start it with: docker-compose up -d redis"
        return 1
    fi
}

# Function to configure production settings
configure_production() {
    print_status "info" "Configuring production settings..."
    
    # Create production environment file
    if [ ! -f ".env.production" ]; then
        cat > .env.production << EOF
# PropCalc Production Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=vantage_ai
POSTGRES_USER=vantage_user
POSTGRES_PASSWORD=vantage_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6380
REDIS_DB=0

# Crawler Settings
CRAWLER_MAX_CONCURRENT_CRAWLERS=3
CRAWLER_REQUEST_DELAY_MIN=3.0
CRAWLER_REQUEST_DELAY_MAX=7.0
CRAWLER_MAX_RETRIES=5
CRAWLER_SESSION_TIMEOUT=1800
CRAWLER_MAX_PAGES_PER_SESSION=50
CRAWLER_MIN_DATA_QUALITY_SCORE=70.0

# Security
SECRET_KEY=$(openssl rand -hex 32)
EOF
        print_status "success" "Production environment file created"
    else
        print_status "info" "Production environment file already exists"
    fi
    
    # Create production configuration
    if [ ! -f "crawler_production.conf" ]; then
        cat > crawler_production.conf << EOF
[production]
max_concurrent_crawlers = 3
request_delay_min = 3.0
request_delay_max = 7.0
max_retries = 5
session_timeout = 1800
max_pages_per_session = 50
min_data_quality_score = 70.0
user_agent_rotation = true
proxy_rotation = false
captcha_handling = true
respect_robots_txt = true
max_requests_per_hour = 1000
crawl_during_business_hours = false
EOF
        print_status "success" "Production configuration file created"
    else
        print_status "info" "Production configuration file already exists"
    fi
}

# Function to setup monitoring
setup_monitoring() {
    print_status "info" "Setting up monitoring..."
    
    # Create monitoring directory
    mkdir -p monitoring/crawler
    
    # Create Prometheus configuration for crawler metrics
    cat > monitoring/crawler/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'propcalc-crawler'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s
EOF
    
    # Create Grafana dashboard configuration
    cat > monitoring/crawler/grafana-dashboard.json << EOF
{
  "dashboard": {
    "title": "PropCalc Crawler Metrics",
    "panels": [
      {
        "title": "Crawler Success Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(crawler_requests_total{status=\"success\"}[5m]) / rate(crawler_requests_total[5m]) * 100"
          }
        ]
      },
      {
        "title": "Properties Collected",
        "type": "stat",
        "targets": [
          {
            "expr": "crawler_properties_collected_total"
          }
        ]
      },
      {
        "title": "Data Quality Score",
        "type": "gauge",
        "targets": [
          {
            "expr": "crawler_data_quality_score_average"
          }
        ]
      }
    ]
  }
}
EOF
    
    print_status "success" "Monitoring configuration created"
}

# Function to create systemd service
create_systemd_service() {
    print_status "info" "Creating systemd service..."
    
    # Get current directory
    CURRENT_DIR=$(pwd)
    
    # Create systemd service file
    sudo tee /etc/systemd/system/propcalc-crawler.service > /dev/null << EOF
[Unit]
Description=PropCalc Property Crawler Service
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/.venv/bin
ExecStart=$CURRENT_DIR/.venv/bin/python -m uvicorn propcalc.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable propcalc-crawler.service
    
    print_status "success" "Systemd service created and enabled"
}

# Function to start services
start_services() {
    print_status "info" "Starting services..."
    
    # Start PostgreSQL and Redis if using Docker
    if command -v docker &> /dev/null; then
        print_status "info" "Starting Docker services..."
        docker-compose up -d postgres redis
        
        # Wait for services to be ready
        print_status "info" "Waiting for services to be ready..."
        sleep 10
        
        # Check service health
        if docker-compose ps | grep -q "healthy"; then
            print_status "success" "Docker services started successfully"
        else
            print_status "warning" "Some Docker services may not be healthy"
        fi
    fi
    
    # Start the crawler service
    print_status "info" "Starting crawler service..."
    if sudo systemctl start propcalc-crawler.service; then
        print_status "success" "Crawler service started"
    else
        print_status "warning" "Failed to start systemd service - you may need to start manually"
    fi
}

# Function to verify deployment
verify_deployment() {
    print_status "info" "Verifying deployment..."
    
    # Wait for service to start
    sleep 5
    
    # Check if service is running
    if curl -s http://localhost:8000/health > /dev/null; then
        print_status "success" "Crawler API is responding"
    else
        print_status "error" "Crawler API is not responding"
        return 1
    fi
    
    # Check crawler health endpoint
    if curl -s http://localhost:8000/api/v1/crawler/health > /dev/null; then
        print_status "success" "Crawler health endpoint is working"
    else
        print_status "error" "Crawler health endpoint is not working"
        return 1
    fi
    
    # Check database connection
    if uv run python -c "
from propcalc.infrastructure.database.postgres_db import PostgresDB
import asyncio
async def test():
    db = PostgresDB()
    await db.init_connection_pool()
    print('Database connection successful')
asyncio.run(test())
"; then
        print_status "success" "Database connection verified"
    else
        print_status "error" "Database connection failed"
        return 1
    fi
}

# Function to show deployment info
show_deployment_info() {
    print_status "info" "Deployment completed successfully!"
    echo ""
    echo -e "${GREEN}🎉 $PROJECT_NAME is now running in production!${NC}"
    echo ""
    echo "📊 Service Information:"
    echo "   • API Endpoint: http://localhost:8000"
    echo "   • API Documentation: http://localhost:8000/docs"
    echo "   • Crawler Health: http://localhost:8000/api/v1/crawler/health"
    echo "   • Monitoring: Prometheus + Grafana configured"
    echo ""
    echo "🔧 Management Commands:"
    echo "   • Start service: sudo systemctl start propcalc-crawler"
    echo "   • Stop service: sudo systemctl stop propcalc-crawler"
    echo "   • Restart service: sudo systemctl restart propcalc-crawler"
    echo "   • Check status: sudo systemctl status propcalc-crawler"
    echo "   • View logs: sudo journalctl -u propcalc-crawler -f"
    echo ""
    echo "📁 Configuration Files:"
    echo "   • Environment: .env.production"
    echo "   • Crawler Config: crawler_production.conf"
    echo "   • Monitoring: monitoring/crawler/"
    echo ""
    echo "📈 Next Steps:"
    echo "   1. Configure your production database credentials"
    echo "   2. Set up monitoring dashboards"
    echo "   3. Configure backup and alerting"
    echo "   4. Test crawler functionality"
    echo "   5. Monitor performance and adjust settings"
    echo ""
}

# Main deployment function
main() {
    echo -e "${BLUE}🚀 Starting $PROJECT_NAME Production Deployment${NC}"
    echo ""
    
    # Run deployment steps
    check_prerequisites
    install_dependencies
    run_tests
    setup_database
    setup_redis
    configure_production
    setup_monitoring
    create_systemd_service
    start_services
    verify_deployment
    show_deployment_info
    
    echo -e "${GREEN}✅ Deployment completed successfully at $(date)${NC}"
    echo "📄 Log file: $LOG_FILE"
}

# Run main function
main "$@"

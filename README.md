# PropCalc - Real Estate Analytics Platform

PropCalc is a comprehensive real estate analytics platform that provides market analysis, property valuation, and investment insights using advanced AI and machine learning techniques.

## 🏗️ Project Structure

```
PropCalc/
├── backend/                 # FastAPI backend with AI/ML capabilities
│   ├── src/propcalc/       # Main application code
│   ├── tests/              # Backend tests
│   ├── alembic/            # Database migrations
│   └── scripts/            # Utility scripts
├── frontend/               # Next.js React frontend
│   ├── src/app/            # Next.js app router pages
│   ├── src/components/     # React components
│   └── src/lib/            # Utility functions
├── monitoring/             # Grafana dashboards and Prometheus config
├── docker-compose.yml      # Development environment
└── deploy.sh              # Deployment script
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install uv
   uv sync
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run database migrations:**
   ```bash
   uv run alembic upgrade head
   ```

5. **Start the backend server:**
   ```bash
   uv run python -m uvicorn src.propcalc.main:app --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

### Docker Setup

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🎯 Features

### Backend Features
- **AI-Powered Analytics**: Machine learning models for property valuation
- **Real-time Data Processing**: Live market data ingestion and analysis
- **Geospatial Analysis**: KML data processing and mapping
- **Performance Optimization**: Caching, connection pooling, and rate limiting
- **Comprehensive Testing**: Unit, integration, and performance tests

### Frontend Features
- **Modern UI**: Built with Next.js, TypeScript, and Tailwind CSS
- **Real-time Dashboards**: Interactive charts and analytics
- **Responsive Design**: Mobile-first approach
- **Error Monitoring**: Sentry integration for production monitoring

### Key Components
- **Vantage Score Algorithm**: Advanced property scoring system
- **DLD Integration**: Dubai Land Department data processing
- **Market Analytics**: Comprehensive market analysis tools
- **Developer Analytics**: Developer performance tracking
- **KML Processing**: Geospatial data visualization

## 🛠️ Development

### Code Quality
- **Backend**: Ruff for linting, Black for formatting
- **Frontend**: ESLint and Prettier
- **Testing**: pytest for backend, Jest for frontend

### Database
- **Primary**: PostgreSQL with async support
- **Caching**: Redis for performance optimization
- **Migrations**: Alembic for schema management

### Monitoring
- **Application**: Sentry for error tracking
- **Infrastructure**: Grafana dashboards with Prometheus
- **Performance**: Custom metrics and monitoring

## 📊 API Documentation

The API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

### Backend Tests
```bash
cd backend
uv run pytest tests/ -v --cov=src
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up -d
```

## 🚀 Deployment

### Production Deployment
```bash
./deploy.sh
```

### Environment Variables
Required environment variables are documented in `.env.example` files in both backend and frontend directories.

## 📈 Performance

- **Backend**: Optimized with async/await, connection pooling, and caching
- **Frontend**: Next.js with optimized builds and lazy loading
- **Database**: Indexed queries and connection pooling
- **Monitoring**: Real-time performance metrics and alerts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For support and questions, please contact the development team.

---

**Note**: This repository has been cleaned to exclude large data files, virtual environments, and build artifacts. The repository size is optimized for GitHub upload while maintaining all essential source code and configuration files. 
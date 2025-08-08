# PropCalc Backend

Advanced Real Estate Analytics Platform with AI-powered insights.

## Features

- **DLD Integration**: Real-time Dubai Land Department data processing
- **KML Geographic Data**: Precise area mapping and boundaries
- **Market Analytics**: Comprehensive real estate market analysis
- **AI-Powered Insights**: Machine learning for market predictions
- **Modern API**: FastAPI with async support and comprehensive documentation

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Redis (optional, for caching)

### Installation

1. Install dependencies:
```bash
uv sync
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the application:
```bash
uv run python main.py
```

## API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development

### Running Tests
```bash
uv run pytest
```

### Code Quality
```bash
uv run black src/
uv run ruff check src/
uv run mypy src/
```

## Architecture

- **FastAPI**: Modern async web framework
- **SQLAlchemy 2.0**: Type-safe ORM with async support
- **Alembic**: Database migrations
- **Pydantic**: Data validation and serialization
- **Repository Pattern**: Clean data access layer
- **Dependency Injection**: Testable and maintainable code

## License

MIT License - see LICENSE file for details.

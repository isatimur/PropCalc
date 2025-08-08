"""
PropCalc Backend - Modern FastAPI Application
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from propcalc.api.v1 import router as api_v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting PropCalc Backend...")
    print("📊 DLD-KML Integration Active")
    print("🗺️  Geographic Data Processing Ready")
    print("📈 Market Analytics Engine Online")
    yield
    # Shutdown
    print("🛑 Shutting down PropCalc Backend...")

def create_app() -> FastAPI:
    """Create FastAPI application with modern configuration"""
    app = FastAPI(
        title="PropCalc Backend",
        version="2.0.0",
        description="Advanced Real Estate Analytics Platform with AI-powered insights",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:8080"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to PropCalc Backend", 
            "version": "2.0.0",
            "features": [
                "DLD Integration",
                "KML Geographic Data",
                "Market Analytics",
                "AI-Powered Insights"
            ]
        }
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "PropCalc Backend"}
    
    # Include API v1 router
    app.include_router(api_v1_router, prefix="/api/v1")
    
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

"""
Property Crawler API Endpoints
Provides REST API for managing property website crawlers
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from pydantic import BaseModel, Field

from ..core.crawlers import CrawlerManager
from ..domain.models.property_models import Property
from ..core.performance.connection_pool import get_pool_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/crawler", tags=["Property Crawler"])

# Pydantic models for API requests/responses
class CrawlRequest(BaseModel):
    """Request model for starting a crawl"""
    sources: List[str] = Field(default=["propertyfinder", "bayut"], description="Sources to crawl")
    max_pages_per_source: int = Field(default=5, ge=1, le=50, description="Maximum pages to crawl per source")
    background: bool = Field(default=True, description="Run crawl in background")

class CrawlResponse(BaseModel):
    """Response model for crawl operations"""
    session_id: str
    status: str
    message: str
    sources: List[str]
    max_pages: int
    started_at: datetime

class CrawlStatusResponse(BaseModel):
    """Response model for crawl status"""
    session_id: str
    status: str
    progress: Dict[str, Any]
    started_at: datetime
    estimated_completion: Optional[datetime]

class PropertySearchRequest(BaseModel):
    """Request model for property search"""
    location: Optional[str] = None
    property_type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_area_sqft: Optional[float] = None
    max_area_sqft: Optional[float] = None
    source: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

class PropertyResponse(BaseModel):
    """Response model for property data"""
    id: int
    source: str
    source_id: str
    title: str
    price: Optional[float]
    price_currency: str
    location: str
    property_type: str
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    area_sqft: Optional[float]
    area_sqm: Optional[float]
    developer: Optional[str]
    completion_date: Optional[str]
    description: Optional[str]
    amenities: List[str]
    images: List[str]
    latitude: Optional[float]
    longitude: Optional[float]
    listing_date: Optional[str]
    agent_name: Optional[str]
    agent_phone: Optional[str]
    agent_email: Optional[str]
    verification_status: str
    data_quality_score: Optional[float]
    crawled_at: datetime
    url: str

class SimilarPropertyRequest(BaseModel):
    """Request model for finding similar properties"""
    property_id: int
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    limit: int = Field(default=10, ge=1, le=50)

class MarketTrendsResponse(BaseModel):
    """Response model for market trends"""
    location: str
    property_type: str
    analysis_date: datetime
    avg_price: Optional[float]
    median_price: Optional[float]
    min_price: Optional[float]
    max_price: Optional[float]
    price_per_sqft: Optional[float]
    total_listings: int
    new_listings: int
    price_changes: int
    market_activity_score: Optional[float]
    price_volatility: Optional[float]

# Global crawler manager instance
_crawler_manager: Optional[CrawlerManager] = None

def get_crawler_manager() -> CrawlerManager:
    """Get or create crawler manager instance"""
    global _crawler_manager
    if _crawler_manager is None:
        _crawler_manager = CrawlerManager()
    return _crawler_manager

# Background task for crawling
async def run_crawl_task(sources: List[str], max_pages: int, session_id: str):
    """Background task for running property crawls"""
    try:
        crawler_manager = get_crawler_manager()
        
        # Start crawl session tracking
        logger.info(f"Starting background crawl session {session_id}")
        
        # Run the crawl
        results = await crawler_manager.crawl_all_sources(max_pages)
        
        # Aggregate data
        aggregated_data = await crawler_manager.aggregate_data()
        
        logger.info(f"Background crawl session {session_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Background crawl session {session_id} failed: {e}")

@router.post("/start", response_model=CrawlResponse)
async def start_crawl(
    request: CrawlRequest,
    background_tasks: BackgroundTasks,
    crawler_manager: CrawlerManager = Depends(get_crawler_manager)
):
    """Start a new property crawling session"""
    try:
        # Validate sources
        valid_sources = ["propertyfinder", "bayut"]
        invalid_sources = [s for s in request.sources if s not in valid_sources]
        if invalid_sources:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid sources: {invalid_sources}. Valid sources: {valid_sources}"
            )
        
        # Generate session ID
        session_id = f"crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if request.background:
            # Add to background tasks
            background_tasks.add_task(
                run_crawl_task, 
                request.sources, 
                request.max_pages_per_source, 
                session_id
            )
            
            return CrawlResponse(
                session_id=session_id,
                status="started",
                message="Crawl started in background",
                sources=request.sources,
                max_pages=request.max_pages_per_source,
                started_at=datetime.now()
            )
        else:
            # Run synchronously
            results = await crawler_manager.crawl_all_sources(request.max_pages_per_source)
            
            return CrawlResponse(
                session_id=session_id,
                status="completed",
                message=f"Crawl completed. Found {sum(len(props) for props in results.values())} properties",
                sources=request.sources,
                max_pages=request.max_pages_per_source,
                started_at=datetime.now()
            )
            
    except Exception as e:
        logger.error(f"Error starting crawl: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{session_id}", response_model=CrawlStatusResponse)
async def get_crawl_status(
    session_id: str,
    crawler_manager: CrawlerManager = Depends(get_crawler_manager)
):
    """Get status of a crawling session"""
    try:
        # For now, return basic status
        # In a real implementation, you'd track session progress
        return CrawlStatusResponse(
            session_id=session_id,
            status="running",  # This would be dynamic
            progress={
                "sources_completed": 0,
                "total_sources": len(crawler_manager.crawlers),
                "properties_found": 0
            },
            started_at=datetime.now(),
            estimated_completion=None
        )
    except Exception as e:
        logger.error(f"Error getting crawl status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources", response_model=Dict[str, Any])
async def get_crawler_sources(
    crawler_manager: CrawlerManager = Depends(get_crawler_manager)
):
    """Get available crawler sources and their status"""
    try:
        return {
            "available_sources": list(crawler_manager.crawlers.keys()),
            "crawler_status": crawler_manager.get_crawler_status(),
            "data_summary": crawler_manager.get_data_summary()
        }
    except Exception as e:
        logger.error(f"Error getting crawler sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crawl-single", response_model=Dict[str, Any])
async def crawl_single_source(
    source: str = Query(..., description="Source to crawl"),
    max_pages: int = Query(default=5, ge=1, le=20, description="Maximum pages to crawl"),
    crawler_manager: CrawlerManager = Depends(get_crawler_manager)
):
    """Crawl a single property source"""
    try:
        if source not in crawler_manager.crawlers:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown source: {source}. Available: {list(crawler_manager.crawlers.keys())}"
            )
        
        properties = await crawler_manager.crawl_single_source(source, max_pages)
        
        return {
            "source": source,
            "properties_found": len(properties),
            "status": "completed",
            "message": f"Successfully crawled {len(properties)} properties from {source}"
        }
        
    except Exception as e:
        logger.error(f"Error crawling single source {source}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/properties", response_model=List[PropertyResponse])
async def search_properties(
    request: PropertySearchRequest = Depends(),
    crawler_manager: CrawlerManager = Depends(get_crawler_manager)
):
    """Search and filter crawled properties"""
    try:
        # For now, return empty list - in real implementation, query database
        # This would integrate with the database models we created
        
        # Placeholder response
        return []
        
    except Exception as e:
        logger.error(f"Error searching properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/similar", response_model=List[PropertyResponse])
async def find_similar_properties(
    request: SimilarPropertyRequest,
    crawler_manager: CrawlerManager = Depends(get_crawler_manager)
):
    """Find similar properties based on a target property"""
    try:
        # For now, return empty list - in real implementation, use similarity algorithm
        # This would integrate with the PropertySimilarity model
        
        # Placeholder response
        return []
        
    except Exception as e:
        logger.error(f"Error finding similar properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-trends", response_model=List[MarketTrendsResponse])
async def get_market_trends(
    location: Optional[str] = Query(None, description="Filter by location"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum results to return")
):
    """Get market trends and statistics"""
    try:
        # For now, return empty list - in real implementation, query MarketTrends table
        
        # Placeholder response
        return []
        
    except Exception as e:
        logger.error(f"Error getting market trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data-quality", response_model=Dict[str, Any])
async def get_data_quality_metrics(
    source: Optional[str] = Query(None, description="Filter by source"),
    crawler_manager: CrawlerManager = Depends(get_crawler_manager)
):
    """Get data quality metrics for crawled properties"""
    try:
        summary = crawler_manager.get_data_summary()
        
        if source:
            # Filter by specific source
            if source in summary.get('source_breakdown', {}):
                return {
                    "source": source,
                    "total_properties": summary['source_breakdown'][source],
                    "data_quality": summary.get('data_quality', {}),
                    "crawl_status": "completed"
                }
            else:
                return {
                    "source": source,
                    "total_properties": 0,
                    "data_quality": {},
                    "crawl_status": "not_crawled"
                }
        else:
            # Return overall metrics
            return summary
            
    except Exception as e:
        logger.error(f"Error getting data quality metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cleanup")
async def cleanup_old_data(
    days_to_keep: int = Query(default=30, ge=1, le=365, description="Days of data to keep"),
    crawler_manager: CrawlerManager = Depends(get_crawler_manager)
):
    """Clean up old crawled data files"""
    try:
        await crawler_manager.cleanup_old_data(days_to_keep)
        
        return {
            "message": f"Cleanup completed. Kept data from last {days_to_keep} days.",
            "cleanup_date": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def crawler_health():
    """Health check for crawler service"""
    return {
        "status": "healthy",
        "service": "property-crawler",
        "timestamp": datetime.now(),
        "version": "2.1.0"
    }

"""
Domain Schemas - Data models and validation schemas for PropCalc
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
import uuid

# ============================================================================
# Base Models
# ============================================================================

class BaseResponse(BaseModel):
    """Base response model with common fields"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class PaginatedResponse(BaseModel):
    """Base paginated response model"""
    data: List[Any]
    total: int
    page: int
    size: int
    pages: int

# ============================================================================
# DLD Data Models
# ============================================================================

class DldDataRequest(BaseModel):
    """Request model for DLD data loading"""
    source: str = Field(..., description="Data source identifier")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Data filters")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Processing options")
    bulk_load: bool = Field(default=False, description="Whether to perform bulk data loading")
    priority: str = Field(default="normal", description="Processing priority: low, normal, high")

class DldTransaction(BaseModel):
    """DLD transaction data model"""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    property_id: str = Field(..., description="Property identifier")
    transaction_date: date = Field(..., description="Transaction date")
    transaction_type: str = Field(..., description="Type of transaction")
    property_type: str = Field(..., description="Property type")
    area_sqft: Optional[float] = Field(None, description="Property area in square feet")
    price_aed: float = Field(..., description="Transaction price in AED")
    price_per_sqft: Optional[float] = Field(None, description="Price per square foot")
    location: str = Field(..., description="Property location")
    developer: Optional[str] = Field(None, description="Property developer")
    project_name: Optional[str] = Field(..., description="Project name")
    latitude: Optional[float] = Field(None, description="Property latitude")
    longitude: Optional[float] = Field(None, description="Property longitude")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class DldProject(BaseModel):
    """DLD project data model"""
    project_id: str = Field(..., description="Unique project identifier")
    project_name: str = Field(..., description="Project name")
    developer: str = Field(..., description="Project developer")
    location: str = Field(..., description="Project location")
    property_type: str = Field(..., description="Primary property type")
    total_units: Optional[int] = Field(None, description="Total number of units")
    completion_date: Optional[date] = Field(None, description="Project completion date")
    status: str = Field(..., description="Project status")
    description: Optional[str] = Field(None, description="Project description")
    latitude: Optional[float] = Field(None, description="Project latitude")
    longitude: Optional[float] = Field(None, description="Project longitude")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# ============================================================================
# Analytics Response Models
# ============================================================================

class DldAnalyticsResponse(BaseModel):
    """Response model for DLD analytics"""
    summary: Dict[str, Any] = Field(..., description="Analytics summary")
    trends: Dict[str, Any] = Field(..., description="Trend analysis")
    insights: List[str] = Field(..., description="Key insights")
    recommendations: List[str] = Field(..., description="Recommendations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class MarketTrendsResponse(BaseModel):
    """Response model for market trends analysis"""
    timeframe: str = Field(..., description="Analysis timeframe")
    property_type: Optional[str] = Field(None, description="Property type analyzed")
    region: Optional[str] = Field(None, description="Region analyzed")
    price_trends: Dict[str, Any] = Field(..., description="Price trend analysis")
    volume_trends: Dict[str, Any] = Field(..., description="Volume trend analysis")
    market_sentiment: str = Field(..., description="Overall market sentiment")
    key_indicators: Dict[str, Any] = Field(..., description="Key market indicators")
    forecast: Optional[Dict[str, Any]] = Field(None, description="Market forecast")

class PortfolioAnalysisResponse(BaseModel):
    """Response model for portfolio analysis"""
    portfolio_id: str = Field(..., description="Portfolio identifier")
    performance_metrics: Dict[str, Any] = Field(..., description="Performance metrics")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk assessment")
    diversification: Dict[str, Any] = Field(..., description="Diversification analysis")
    geospatial_analysis: Optional[Dict[str, Any]] = Field(None, description="Geospatial analysis")
    recommendations: List[str] = Field(..., description="Portfolio recommendations")

class TransactionSummaryResponse(BaseModel):
    """Response model for transaction summary"""
    period: Dict[str, date] = Field(..., description="Analysis period")
    total_transactions: int = Field(..., description="Total number of transactions")
    total_volume: float = Field(..., description="Total transaction volume")
    average_price: float = Field(..., description="Average transaction price")
    price_distribution: Dict[str, Any] = Field(..., description="Price distribution analysis")
    location_breakdown: Dict[str, Any] = Field(..., description="Location breakdown")
    property_type_breakdown: Dict[str, Any] = Field(..., description="Property type breakdown")

class GeospatialAnalysisResponse(BaseModel):
    """Response model for geospatial analysis"""
    bounds: tuple = Field(..., description="Geographic bounds analyzed")
    property_type: Optional[str] = Field(None, description="Property type filter")
    time_period: Optional[str] = Field(None, description="Time period filter")
    spatial_distribution: Dict[str, Any] = Field(..., description="Spatial distribution analysis")
    hotspot_analysis: Dict[str, Any] = Field(..., description="Hotspot analysis")
    accessibility_metrics: Dict[str, Any] = Field(..., description="Accessibility metrics")
    environmental_factors: Optional[Dict[str, Any]] = Field(None, description="Environmental factors")

# ============================================================================
# User and Authentication Models
# ============================================================================

class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    DEVELOPER = "developer"

class User(BaseModel):
    """User model"""
    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="User email")
    full_name: str = Field(..., description="Full name")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(default=True, description="Whether user is active")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

class UserCreate(BaseModel):
    """User creation request model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="Valid email address")
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    role: UserRole = Field(default=UserRole.VIEWER)

class UserUpdate(BaseModel):
    """User update request model"""
    email: Optional[str] = Field(None, description="Valid email address")
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = Field(None)
    is_active: Optional[bool] = Field(None)

class LoginRequest(BaseModel):
    """Login request model"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")

class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: User = Field(..., description="User information")

# ============================================================================
# Project Models
# ============================================================================

class ProjectStatus(str, Enum):
    """Project status enumeration"""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

class Project(BaseModel):
    """Project model"""
    project_id: str = Field(..., description="Unique project identifier")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    status: ProjectStatus = Field(..., description="Project status")
    owner_id: str = Field(..., description="Project owner user ID")
    team_members: List[str] = Field(default_factory=list, description="Team member user IDs")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    start_date: Optional[date] = Field(None, description="Project start date")
    target_date: Optional[date] = Field(None, description="Project target completion date")

class ProjectCreate(BaseModel):
    """Project creation request model"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: ProjectStatus = Field(default=ProjectStatus.PLANNING)
    team_members: List[str] = Field(default_factory=list)
    start_date: Optional[date] = Field(None)
    target_date: Optional[date] = Field(None)

class ProjectUpdate(BaseModel):
    """Project update request model"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[ProjectStatus] = Field(None)
    team_members: Optional[List[str]] = Field(None)
    start_date: Optional[date] = Field(None)
    target_date: Optional[date] = Field(None)

# ============================================================================
# AI and Analytics Models
# ============================================================================

class AIScoringRequest(BaseModel):
    """AI scoring request model"""
    property_data: Dict[str, Any] = Field(..., description="Property data for scoring")
    scoring_model: str = Field(default="vantage_score", description="Scoring model to use")
    include_explanations: bool = Field(default=True, description="Include scoring explanations")
    confidence_threshold: float = Field(default=0.7, description="Confidence threshold")

class AIScoringResponse(BaseModel):
    """AI scoring response model"""
    score: float = Field(..., description="Calculated score")
    confidence: float = Field(..., description="Confidence level")
    explanations: Optional[List[str]] = Field(None, description="Score explanations")
    factors: Dict[str, float] = Field(..., description="Contributing factors")
    recommendations: List[str] = Field(..., description="Recommendations")
    model_version: str = Field(..., description="Model version used")

class ModelTrainingRequest(BaseModel):
    """Model training request model"""
    model_type: str = Field(..., description="Type of model to train")
    training_data_source: str = Field(..., description="Training data source")
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="Model hyperparameters")
    validation_split: float = Field(default=0.2, description="Validation data split")
    target_metric: str = Field(default="accuracy", description="Target optimization metric")

class ModelTrainingResponse(BaseModel):
    """Model training response model"""
    training_id: str = Field(..., description="Training job identifier")
    status: str = Field(..., description="Training status")
    model_version: str = Field(..., description="New model version")
    performance_metrics: Dict[str, float] = Field(..., description="Model performance metrics")
    training_time: float = Field(..., description="Training time in seconds")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")

# ============================================================================
# System and Monitoring Models
# ============================================================================

class SystemHealth(BaseModel):
    """System health status model"""
    status: str = Field(..., description="Overall system status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    components: Dict[str, Dict[str, Any]] = Field(..., description="Component health status")
    metrics: Dict[str, Any] = Field(..., description="System metrics")
    alerts: List[str] = Field(default_factory=list, description="Active alerts")

class PerformanceMetrics(BaseModel):
    """Performance metrics model"""
    timestamp: datetime = Field(..., description="Metrics timestamp")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    disk_usage: float = Field(..., description="Disk usage percentage")
    network_throughput: float = Field(..., description="Network throughput in MB/s")
    database_connections: int = Field(..., description="Active database connections")
    api_response_time: float = Field(..., description="Average API response time in ms")
    cache_hit_ratio: float = Field(..., description="Cache hit ratio percentage")

class DataQualityReport(BaseModel):
    """Data quality report model"""
    source: str = Field(..., description="Data source name")
    timestamp: datetime = Field(..., description="Report timestamp")
    overall_score: float = Field(..., description="Overall quality score")
    completeness: float = Field(..., description="Data completeness score")
    accuracy: float = Field(..., description="Data accuracy score")
    consistency: float = Field(..., description="Data consistency score")
    timeliness: float = Field(..., description="Data timeliness score")
    issues: List[Dict[str, Any]] = Field(..., description="Data quality issues")
    recommendations: List[str] = Field(..., description="Quality improvement recommendations")

# ============================================================================
# Validation and Utility Methods
# ============================================================================

class Config:
    """Pydantic configuration"""
    use_enum_values = True
    validate_assignment = True
    arbitrary_types_allowed = True

# Custom validators
@validator('email')
def validate_email(cls, v):
    """Validate email format"""
    if v and '@' not in v:
        raise ValueError('Invalid email format')
    return v.lower() if v else v

@validator('price_aed')
def validate_positive_price(cls, v):
    """Validate positive price"""
    if v <= 0:
        raise ValueError('Price must be positive')
    return v

@validator('area_sqft')
def validate_positive_area(cls, v):
    """Validate positive area"""
    if v is not None and v <= 0:
        raise ValueError('Area must be positive')
    return v

# ============================================================================
# DLD Analytics Models
# ============================================================================

class DldAnalyticsRequest(BaseModel):
    """Request model for DLD analytics"""
    start_date: Optional[date] = Field(None, description="Start date for analysis")
    end_date: Optional[date] = Field(None, description="End date for analysis")
    location: Optional[str] = Field(None, description="Location filter")
    property_type: Optional[str] = Field(None, description="Property type filter")
    developer: Optional[str] = Field(None, description="Developer filter")
    price_range: Optional[tuple[float, float]] = Field(None, description="Price range filter (min, max)")
    area_range: Optional[tuple[float, float]] = Field(None, description="Area range filter (min, max)")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis to perform")
    group_by: Optional[str] = Field(None, description="Grouping dimension (month, quarter, year, location, property_type)")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of results")

class DldMarketTrendsRequest(BaseModel):
    """Request model for market trends analysis"""
    timeframe: str = Field(default="1Y", description="Analysis timeframe (1M, 3M, 6M, 1Y, 2Y, 5Y)")
    location: Optional[str] = Field(None, description="Location filter")
    property_type: Optional[str] = Field(None, description="Property type filter")
    developer: Optional[str] = Field(None, description="Developer filter")
    include_forecast: bool = Field(default=False, description="Include trend forecasting")
    confidence_level: float = Field(default=0.95, ge=0.8, le=0.99, description="Forecast confidence level")

class DldPortfolioAnalysisRequest(BaseModel):
    """Request model for portfolio analysis"""
    portfolio_locations: List[str] = Field(..., description="Portfolio locations")
    portfolio_property_types: List[str] = Field(..., description="Portfolio property types")
    investment_horizon: str = Field(default="5Y", description="Investment horizon")
    risk_tolerance: str = Field(default="moderate", description="Risk tolerance level")
    include_market_comparison: bool = Field(default=True, description="Include market comparison")
    include_geospatial_analysis: bool = Field(default=True, description="Include geospatial analysis")

class DldGeospatialAnalysisRequest(BaseModel):
    """Request model for geospatial analysis"""
    bounds: Optional[tuple[float, float, float, float]] = Field(None, description="Geographic bounds (min_lat, min_lng, max_lat, max_lng)")
    center_point: Optional[tuple[float, float]] = Field(None, description="Center point (lat, lng)")
    radius_km: Optional[float] = Field(None, description="Radius in kilometers")
    property_type: Optional[str] = Field(None, description="Property type filter")
    time_period: Optional[str] = Field(None, description="Time period filter")
    analysis_type: str = Field(default="hotspot", description="Analysis type (hotspot, accessibility, clustering)")

class DldDeveloperAnalysisRequest(BaseModel):
    """Request model for developer analysis"""
    developer_name: Optional[str] = Field(None, description="Developer name filter")
    time_period: str = Field(default="2Y", description="Analysis time period")
    include_performance_metrics: bool = Field(default=True, description="Include performance metrics")
    include_market_share: bool = Field(default=True, description="Include market share analysis")
    include_competitor_analysis: bool = Field(default=False, description="Include competitor analysis")

# ============================================================================
# Enhanced Analytics Response Models
# ============================================================================

class DldMarketTrendsResponse(BaseModel):
    """Enhanced response model for market trends analysis"""
    timeframe: str = Field(..., description="Analysis timeframe")
    location: Optional[str] = Field(None, description="Location analyzed")
    property_type: Optional[str] = Field(None, description="Property type analyzed")
    developer: Optional[str] = Field(None, description="Developer analyzed")
    
    # Price trends
    price_trends: Dict[str, Any] = Field(..., description="Price trend analysis")
    price_per_sqft_trends: Dict[str, Any] = Field(..., description="Price per sqft trends")
    volume_trends: Dict[str, Any] = Field(..., description="Transaction volume trends")
    
    # Market indicators
    market_sentiment: str = Field(..., description="Overall market sentiment")
    market_volatility: float = Field(..., description="Market volatility index")
    key_indicators: Dict[str, Any] = Field(..., description="Key market indicators")
    
    # Forecasting
    forecast: Optional[Dict[str, Any]] = Field(None, description="Market forecast")
    confidence_intervals: Optional[Dict[str, Any]] = Field(None, description="Forecast confidence intervals")
    
    # Comparative analysis
    market_performance: Dict[str, Any] = Field(..., description="Market performance metrics")
    benchmark_comparison: Optional[Dict[str, Any]] = Field(None, description="Benchmark comparison")
    
    # Metadata
    analysis_date: datetime = Field(default_factory=datetime.now)
    data_points: int = Field(..., description="Number of data points analyzed")
    last_updated: datetime = Field(..., description="Last data update")

class DldPortfolioAnalysisResponse(BaseModel):
    """Enhanced response model for portfolio analysis"""
    portfolio_id: str = Field(..., description="Portfolio identifier")
    analysis_date: datetime = Field(default_factory=datetime.now)
    
    # Performance metrics
    performance_metrics: Dict[str, Any] = Field(..., description="Performance metrics")
    roi_analysis: Dict[str, Any] = Field(..., description="ROI analysis")
    cash_flow_projection: Dict[str, Any] = Field(..., description="Cash flow projections")
    
    # Risk assessment
    risk_assessment: Dict[str, Any] = Field(..., description="Risk assessment")
    stress_test_results: Dict[str, Any] = Field(..., description="Stress test results")
    risk_factors: List[str] = Field(..., description="Key risk factors")
    
    # Diversification analysis
    diversification: Dict[str, Any] = Field(..., description="Diversification analysis")
    concentration_risk: Dict[str, Any] = Field(..., description="Concentration risk analysis")
    optimal_allocation: Dict[str, Any] = Field(..., description="Optimal allocation recommendations")
    
    # Geospatial analysis
    geospatial_analysis: Optional[Dict[str, Any]] = Field(None, description="Geospatial analysis")
    location_risk: Optional[Dict[str, Any]] = Field(None, description="Location-based risk assessment")
    
    # Market comparison
    market_comparison: Optional[Dict[str, Any]] = Field(None, description="Market comparison")
    benchmark_performance: Optional[Dict[str, Any]] = Field(None, description="Benchmark performance")
    
    # Recommendations
    recommendations: List[str] = Field(..., description="Portfolio recommendations")
    action_items: List[Dict[str, Any]] = Field(..., description="Action items with priorities")

class DldGeospatialAnalysisResponse(BaseModel):
    """Enhanced response model for geospatial analysis"""
    analysis_type: str = Field(..., description="Type of analysis performed")
    geographic_scope: Dict[str, Any] = Field(..., description="Geographic scope of analysis")
    
    # Spatial distribution
    spatial_distribution: Dict[str, Any] = Field(..., description="Spatial distribution analysis")
    density_analysis: Dict[str, Any] = Field(..., description="Property density analysis")
    clustering_results: Dict[str, Any] = Field(..., description="Clustering analysis results")
    
    # Hotspot analysis
    hotspot_analysis: Dict[str, Any] = Field(..., description="Hotspot analysis")
    high_value_areas: List[Dict[str, Any]] = Field(..., description="High-value areas identified")
    emerging_areas: List[Dict[str, Any]] = Field(..., description="Emerging areas identified")
    
    # Accessibility metrics
    accessibility_metrics: Dict[str, Any] = Field(..., description="Accessibility metrics")
    infrastructure_analysis: Dict[str, Any] = Field(..., description="Infrastructure analysis")
    connectivity_scores: Dict[str, Any] = Field(..., description="Connectivity scores")
    
    # Environmental factors
    environmental_factors: Optional[Dict[str, Any]] = Field(None, description="Environmental factors")
    sustainability_scores: Optional[Dict[str, Any]] = Field(None, description="Sustainability scores")
    
    # Market insights
    market_insights: Dict[str, Any] = Field(..., description="Market insights from spatial analysis")
    investment_opportunities: List[Dict[str, Any]] = Field(..., description="Investment opportunities")
    
    # Visualization data
    visualization_data: Dict[str, Any] = Field(..., description="Data for visualization")
    map_overlays: List[Dict[str, Any]] = Field(..., description="Map overlay data")

class DldDeveloperAnalysisResponse(BaseModel):
    """Enhanced response model for developer analysis"""
    developer_name: str = Field(..., description="Developer name")
    analysis_period: str = Field(..., description="Analysis period")
    
    # Performance metrics
    performance_metrics: Dict[str, Any] = Field(..., description="Performance metrics")
    project_success_rate: float = Field(..., description="Project success rate")
    average_completion_time: Optional[float] = Field(None, description="Average project completion time")
    
    # Market share
    market_share: Dict[str, Any] = Field(..., description="Market share analysis")
    competitive_position: str = Field(..., description="Competitive position")
    market_rank: Optional[int] = Field(None, description="Market ranking")
    
    # Financial metrics
    financial_metrics: Dict[str, Any] = Field(..., description="Financial metrics")
    revenue_trends: Dict[str, Any] = Field(..., description="Revenue trends")
    profitability_analysis: Dict[str, Any] = Field(..., description="Profitability analysis")
    
    # Project portfolio
    project_portfolio: Dict[str, Any] = Field(..., description="Project portfolio analysis")
    active_projects: List[Dict[str, Any]] = Field(..., description="Active projects")
    completed_projects: List[Dict[str, Any]] = Field(..., description="Completed projects")
    
    # Quality metrics
    quality_metrics: Dict[str, Any] = Field(..., description="Quality metrics")
    customer_satisfaction: Optional[float] = Field(None, description="Customer satisfaction score")
    quality_ratings: Dict[str, Any] = Field(..., description="Quality ratings")
    
    # Competitor analysis
    competitor_analysis: Optional[Dict[str, Any]] = Field(None, description="Competitor analysis")
    competitive_advantages: List[str] = Field(..., description="Competitive advantages")
    improvement_areas: List[str] = Field(..., description="Areas for improvement")
    
    # Future outlook
    future_outlook: Dict[str, Any] = Field(..., description="Future outlook")
    growth_potential: str = Field(..., description="Growth potential assessment")
    strategic_recommendations: List[str] = Field(..., description="Strategic recommendations")

class DldComprehensiveReportResponse(BaseModel):
    """Comprehensive DLD report response"""
    report_id: str = Field(..., description="Report identifier")
    generated_at: datetime = Field(default_factory=datetime.now)
    report_period: Dict[str, date] = Field(..., description="Report period")
    
    # Executive summary
    executive_summary: Dict[str, Any] = Field(..., description="Executive summary")
    key_findings: List[str] = Field(..., description="Key findings")
    market_overview: str = Field(..., description="Market overview")
    
    # Market analysis
    market_analysis: DldMarketTrendsResponse = Field(..., description="Market analysis")
    geospatial_analysis: DldGeospatialAnalysisResponse = Field(..., description="Geospatial analysis")
    
    # Developer analysis
    top_developers: List[DldDeveloperAnalysisResponse] = Field(..., description="Top developers analysis")
    developer_performance: Dict[str, Any] = Field(..., description="Developer performance summary")
    
    # Investment insights
    investment_insights: Dict[str, Any] = Field(..., description="Investment insights")
    risk_assessment: Dict[str, Any] = Field(..., description="Overall risk assessment")
    opportunities: List[Dict[str, Any]] = Field(..., description="Investment opportunities")
    
    # Recommendations
    strategic_recommendations: List[str] = Field(..., description="Strategic recommendations")
    action_plan: List[Dict[str, Any]] = Field(..., description="Action plan")
    
    # Data quality
    data_quality: Dict[str, Any] = Field(..., description="Data quality assessment")
    methodology: Dict[str, Any] = Field(..., description="Analysis methodology")
    
    # Metadata
    data_sources: List[str] = Field(..., description="Data sources used")
    last_updated: datetime = Field(..., description="Last data update")
    next_update: Optional[datetime] = Field(None, description="Next scheduled update")

# ============================================================================
# Data Export and Report Models
# ============================================================================

class ReportExportRequest(BaseModel):
    """Request model for report export"""
    report_type: str = Field(..., description="Type of report to export")
    format: str = Field(default="pdf", description="Export format (pdf, excel, csv, json)")
    include_charts: bool = Field(default=True, description="Include charts and visualizations")
    include_raw_data: bool = Field(default=False, description="Include raw data")
    custom_filters: Optional[Dict[str, Any]] = Field(None, description="Custom filters for export")

class ReportExportResponse(BaseModel):
    """Response model for report export"""
    export_id: str = Field(..., description="Export identifier")
    download_url: str = Field(..., description="Download URL for exported file")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    expires_at: datetime = Field(..., description="Download link expiration time")
    format: str = Field(..., description="Export format")

# ============================================================================
# Real-time Analytics Models
# ============================================================================

class RealTimeMetricsRequest(BaseModel):
    """Request model for real-time metrics"""
    metrics: List[str] = Field(..., description="Metrics to retrieve")
    refresh_interval: Optional[int] = Field(None, description="Refresh interval in seconds")
    include_historical: bool = Field(default=False, description="Include historical data")

class RealTimeMetricsResponse(BaseModel):
    """Response model for real-time metrics"""
    timestamp: datetime = Field(default_factory=datetime.now)
    metrics: Dict[str, Any] = Field(..., description="Requested metrics")
    historical_data: Optional[Dict[str, Any]] = Field(None, description="Historical data if requested")
    alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Active alerts")

# ============================================================================
# Enhanced Validation and Utility Methods
# ============================================================================

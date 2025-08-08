"""
Enhanced Analytics Module for PropCalc
Comprehensive data analysis using all available data sources
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, desc, func, text
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Analysis types"""
    MARKET_TRENDS = "market_trends"
    DEVELOPER_PERFORMANCE = "developer_performance"
    PROPERTY_VALUATION = "property_valuation"
    RENTAL_ANALYSIS = "rental_analysis"
    BROKER_ACTIVITY = "broker_activity"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    AREA_COMPARISON = "area_comparison"
    PROJECT_ANALYSIS = "project_analysis"

@dataclass
class MarketTrend:
    """Market trend data"""
    period: str
    total_transactions: int
    avg_price: float
    total_volume: float
    price_change_pct: float
    volume_change_pct: float

@dataclass
class DeveloperPerformance:
    """Developer performance data"""
    developer_id: str
    developer_name: str
    total_projects: int
    completed_projects: int
    total_units: int
    avg_completion_rate: float
    total_valuation: float
    market_share: float

@dataclass
class PropertyValuation:
    """Property valuation data"""
    property_id: str
    area_name: str
    property_type: str
    current_valuation: float
    historical_valuations: list[float]
    valuation_trend: float
    comparable_properties: list[dict]

@dataclass
class RentalAnalysis:
    """Rental analysis data"""
    area_id: int
    area_name: str
    avg_rent_amount: float
    rent_trend: float
    occupancy_rate: float
    rental_yield: float
    market_demand: str

class EnhancedAnalytics:
    """Enhanced analytics engine with comprehensive data analysis"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    async def get_market_trends(
        self,
        area_id: int | None = None,
        property_type: str | None = None,
        period_months: int = 12
    ) -> list[MarketTrend]:
        """Analyze market trends over time"""
        try:
            session = self.SessionLocal()

            # Calculate date range
            end_date = datetime.now()
            end_date - timedelta(days=period_months * 30)

            # Base query for rent contracts
            rent_query = session.query(
                func.date_trunc('month', text('contract_date')).label('period'),
                func.count(text('contract_id')).label('total_transactions'),
                func.avg(text('rent_amount')).label('avg_price'),
                func.sum(text('rent_amount')).label('total_volume')
            ).filter(
                text('contract_date >= :start_date'),
                text('contract_date <= :end_date')
            )

            # Add filters
            if area_id:
                rent_query = rent_query.filter(text('area_id = :area_id'))
            if property_type:
                rent_query = rent_query.filter(text('property_type_en = :property_type'))

            rent_results = rent_query.group_by(text('period')).order_by(text('period')).all()

            # Calculate trends
            trends = []
            for i, result in enumerate(rent_results):
                if i > 0:
                    prev_result = rent_results[i-1]
                    price_change = ((result.avg_price - prev_result.avg_price) / prev_result.avg_price * 100) if prev_result.avg_price else 0
                    volume_change = ((result.total_volume - prev_result.total_volume) / prev_result.total_volume * 100) if prev_result.total_volume else 0
                else:
                    price_change = 0
                    volume_change = 0

                trend = MarketTrend(
                    period=result.period.strftime('%Y-%m'),
                    total_transactions=result.total_transactions,
                    avg_price=float(result.avg_price) if result.avg_price else 0,
                    total_volume=float(result.total_volume) if result.total_volume else 0,
                    price_change_pct=price_change,
                    volume_change_pct=volume_change
                )
                trends.append(trend)

            session.close()
            return trends

        except Exception as e:
            logger.error(f"Error analyzing market trends: {e}")
            return []

    async def get_developer_performance(self, developer_id: str | None = None) -> list[DeveloperPerformance]:
        """Analyze developer performance"""
        try:
            session = self.SessionLocal()

            # Base query
            query = session.query(
                text('d.developer_id'),
                text('d.developer_name_en'),
                func.count(text('p.project_id')).label('total_projects'),
                func.count(text('CASE WHEN p.project_status = \'FINISHED\' THEN 1 END')).label('completed_projects'),
                func.sum(text('p.no_of_units')).label('total_units'),
                func.avg(text('p.percent_completed')).label('avg_completion_rate'),
                func.sum(text('v.valuation_amount')).label('total_valuation')
            ).select_from(
                text('developers d')
            ).outerjoin(
                text('projects p'), text('d.developer_id = p.developer_id')
            ).outerjoin(
                text('valuations v'), text('p.project_id = v.project_id')
            )

            if developer_id:
                query = query.filter(text('d.developer_id = :developer_id'))

            results = query.group_by(text('d.developer_id, d.developer_name_en')).all()

            # Calculate market share
            total_units = session.query(func.sum(text('no_of_units'))).select_from(text('projects')).scalar() or 0

            performances = []
            for result in results:
                market_share = (result.total_units / total_units * 100) if total_units > 0 else 0

                performance = DeveloperPerformance(
                    developer_id=result.developer_id,
                    developer_name=result.developer_name_en,
                    total_projects=result.total_projects,
                    completed_projects=result.completed_projects,
                    total_units=result.total_units or 0,
                    avg_completion_rate=float(result.avg_completion_rate) if result.avg_completion_rate else 0,
                    total_valuation=float(result.total_valuation) if result.total_valuation else 0,
                    market_share=market_share
                )
                performances.append(performance)

            session.close()
            return performances

        except Exception as e:
            logger.error(f"Error analyzing developer performance: {e}")
            return []

    async def get_property_valuation_analysis(self, property_id: str) -> PropertyValuation | None:
        """Analyze property valuation trends"""
        try:
            session = self.SessionLocal()

            # Get property details
            property_query = session.query(
                text('b.property_id'),
                text('b.area_name_en'),
                text('b.property_type_en'),
                text('b.actual_area')
            ).select_from(
                text('buildings b')
            ).filter(
                text('b.property_id = :property_id')
            )

            property_result = property_query.first()
            if not property_result:
                session.close()
                return None

            # Get historical valuations
            valuations_query = session.query(
                text('v.valuation_amount'),
                text('v.valuation_date')
            ).select_from(
                text('valuations v')
            ).filter(
                text('v.property_id = :property_id')
            ).order_by(
                text('v.valuation_date')
            )

            valuation_results = valuations_query.all()
            historical_valuations = [float(v.valuation_amount) for v in valuation_results if v.valuation_amount]

            # Calculate valuation trend
            valuation_trend = 0
            if len(historical_valuations) >= 2:
                valuation_trend = ((historical_valuations[-1] - historical_valuations[0]) / historical_valuations[0] * 100)

            # Get comparable properties
            comparable_query = session.query(
                text('b.property_id'),
                text('b.area_name_en'),
                text('v.valuation_amount'),
                text('b.actual_area')
            ).select_from(
                text('buildings b')
            ).join(
                text('valuations v'), text('b.property_id = v.property_id')
            ).filter(
                text('b.area_name_en = :area_name'),
                text('b.property_type_en = :property_type'),
                text('b.property_id != :property_id')
            ).limit(5)

            comparable_results = comparable_query.all()
            comparable_properties = [
                {
                    'property_id': r.property_id,
                    'area_name': r.area_name_en,
                    'valuation_amount': float(r.valuation_amount) if r.valuation_amount else 0,
                    'area': float(r.actual_area) if r.actual_area else 0
                }
                for r in comparable_results
            ]

            current_valuation = historical_valuations[-1] if historical_valuations else 0

            valuation = PropertyValuation(
                property_id=property_result.property_id,
                area_name=property_result.area_name_en,
                property_type=property_result.property_type_en,
                current_valuation=current_valuation,
                historical_valuations=historical_valuations,
                valuation_trend=valuation_trend,
                comparable_properties=comparable_properties
            )

            session.close()
            return valuation

        except Exception as e:
            logger.error(f"Error analyzing property valuation: {e}")
            return None

    async def get_rental_analysis(self, area_id: int | None = None) -> list[RentalAnalysis]:
        """Analyze rental market data"""
        try:
            session = self.SessionLocal()

            # Base query for rental analysis
            query = session.query(
                text('b.area_id'),
                text('b.area_name_en'),
                func.avg(text('rc.rent_amount')).label('avg_rent_amount'),
                func.count(text('rc.contract_id')).label('total_contracts'),
                func.avg(text('rc.area_sqft')).label('avg_area')
            ).select_from(
                text('buildings b')
            ).join(
                text('rent_contracts rc'), text('b.property_id = rc.property_id')
            ).filter(
                text('rc.contract_date >= :start_date')
            )

            if area_id:
                query = query.filter(text('b.area_id = :area_id'))

            results = query.group_by(text('b.area_id, b.area_name_en')).all()

            # Calculate additional metrics
            analyses = []
            for result in results:
                # Calculate rental yield (simplified)
                avg_price_per_sqft = result.avg_rent_amount / result.avg_area if result.avg_area else 0

                # Determine market demand based on transaction volume
                if result.total_contracts > 100:
                    market_demand = "High"
                elif result.total_contracts > 50:
                    market_demand = "Medium"
                else:
                    market_demand = "Low"

                analysis = RentalAnalysis(
                    area_id=result.area_id,
                    area_name=result.area_name_en,
                    avg_rent_amount=float(result.avg_rent_amount) if result.avg_rent_amount else 0,
                    rent_trend=0,  # Would need historical data for trend
                    occupancy_rate=0,  # Would need occupancy data
                    rental_yield=avg_price_per_sqft,
                    market_demand=market_demand
                )
                analyses.append(analysis)

            session.close()
            return analyses

        except Exception as e:
            logger.error(f"Error analyzing rental data: {e}")
            return []

    async def get_broker_activity_analysis(self) -> dict[str, Any]:
        """Analyze broker activity and performance"""
        try:
            session = self.SessionLocal()

            # Top performing brokers
            top_brokers_query = session.query(
                text('b.broker_name_en'),
                text('b.broker_number'),
                func.count(text('rc.contract_id')).label('total_transactions'),
                func.sum(text('rc.rent_amount')).label('total_volume')
            ).select_from(
                text('brokers b')
            ).join(
                text('rent_contracts rc'), text('b.participant_id = rc.broker_id')
            ).group_by(
                text('b.broker_name_en, b.broker_number')
            ).order_by(
                desc(text('total_volume'))
            ).limit(10)

            top_brokers = [
                {
                    'broker_name': r.broker_name_en,
                    'broker_number': r.broker_number,
                    'total_transactions': r.total_transactions,
                    'total_volume': float(r.total_volume) if r.total_volume else 0
                }
                for r in top_brokers_query.all()
            ]

            # Broker license status
            license_status_query = session.query(
                text('CASE WHEN license_end_date > CURRENT_DATE THEN \'Active\' ELSE \'Expired\' END').label('status'),
                func.count(text('*')).label('count')
            ).select_from(
                text('brokers')
            ).group_by(
                text('status')
            )

            license_status = [
                {
                    'status': r.status,
                    'count': r.count
                }
                for r in license_status_query.all()
            ]

            session.close()

            return {
                'top_brokers': top_brokers,
                'license_status': license_status,
                'total_brokers': sum(r['count'] for r in license_status),
                'active_brokers': sum(r['count'] for r in license_status if r['status'] == 'Active')
            }

        except Exception as e:
            logger.error(f"Error analyzing broker activity: {e}")
            return {}

    async def get_regulatory_compliance_analysis(self) -> dict[str, Any]:
        """Analyze regulatory compliance across different entities"""
        try:
            session = self.SessionLocal()

            # Developer compliance
            developer_compliance = session.query(
                text('CASE WHEN license_expiry_date > CURRENT_DATE THEN \'Compliant\' ELSE \'Non-Compliant\' END').label('status'),
                func.count(text('*')).label('count')
            ).select_from(
                text('developers')
            ).group_by(
                text('status')
            ).all()

            # Broker compliance
            broker_compliance = session.query(
                text('CASE WHEN license_end_date > CURRENT_DATE THEN \'Compliant\' ELSE \'Non-Compliant\' END').label('status'),
                func.count(text('*')).label('count')
            ).select_from(
                text('brokers')
            ).group_by(
                text('status')
            ).all()

            # Valuator compliance
            valuator_compliance = session.query(
                text('CASE WHEN license_end_date > CURRENT_DATE THEN \'Compliant\' ELSE \'Non-Compliant\' END').label('status'),
                func.count(text('*')).label('count')
            ).select_from(
                text('valuators')
            ).group_by(
                text('status')
            ).all()

            session.close()

            return {
                'developer_compliance': [
                    {'status': r.status, 'count': r.count}
                    for r in developer_compliance
                ],
                'broker_compliance': [
                    {'status': r.status, 'count': r.count}
                    for r in broker_compliance
                ],
                'valuator_compliance': [
                    {'status': r.status, 'count': r.count}
                    for r in valuator_compliance
                ]
            }

        except Exception as e:
            logger.error(f"Error analyzing regulatory compliance: {e}")
            return {}

    async def generate_market_dashboard(self) -> dict[str, Any]:
        """Generate comprehensive market dashboard"""
        try:
            # Get all analytics data
            market_trends = await self.get_market_trends(period_months=6)
            developer_performance = await self.get_developer_performance()
            rental_analysis = await self.get_rental_analysis()
            broker_activity = await self.get_broker_activity_analysis()
            regulatory_compliance = await self.get_regulatory_compliance_analysis()

            # Calculate key metrics
            total_properties = len(market_trends) if market_trends else 0
            avg_price = sum(t.avg_price for t in market_trends) / len(market_trends) if market_trends else 0
            total_volume = sum(t.total_volume for t in market_trends) if market_trends else 0

            dashboard = {
                'summary': {
                    'total_properties': total_properties,
                    'average_price': avg_price,
                    'total_volume': total_volume,
                    'active_developers': len(developer_performance),
                    'active_brokers': broker_activity.get('active_brokers', 0)
                },
                'market_trends': [
                    {
                        'period': t.period,
                        'total_transactions': t.total_transactions,
                        'avg_price': t.avg_price,
                        'total_volume': t.total_volume,
                        'price_change_pct': t.price_change_pct,
                        'volume_change_pct': t.volume_change_pct
                    }
                    for t in market_trends
                ],
                'top_developers': [
                    {
                        'developer_name': d.developer_name,
                        'total_projects': d.total_projects,
                        'market_share': d.market_share,
                        'avg_completion_rate': d.avg_completion_rate
                    }
                    for d in sorted(developer_performance, key=lambda x: x.market_share, reverse=True)[:5]
                ],
                'rental_market': [
                    {
                        'area_name': r.area_name,
                        'avg_rent_amount': r.avg_rent_amount,
                        'rental_yield': r.rental_yield,
                        'market_demand': r.market_demand
                    }
                    for r in rental_analysis
                ],
                'broker_activity': broker_activity,
                'regulatory_compliance': regulatory_compliance,
                'generated_at': datetime.now().isoformat()
            }

            return dashboard

        except Exception as e:
            logger.error(f"Error generating market dashboard: {e}")
            return {}

    async def create_visualization(self, data: dict[str, Any], chart_type: str) -> str:
        """Create visualization charts"""
        try:
            if chart_type == "market_trends":
                return await self._create_market_trends_chart(data)
            elif chart_type == "developer_performance":
                return await self._create_developer_performance_chart(data)
            elif chart_type == "rental_analysis":
                return await self._create_rental_analysis_chart(data)
            else:
                return "Unsupported chart type"

        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return "Error creating visualization"

    async def _create_market_trends_chart(self, data: dict[str, Any]) -> str:
        """Create market trends chart"""
        try:
            trends = data.get('market_trends', [])
            if not trends:
                return "No data available for market trends"

            periods = [t['period'] for t in trends]
            prices = [t['avg_price'] for t in trends]
            volumes = [t['total_volume'] for t in trends]

            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Average Price Trend', 'Total Volume Trend'),
                vertical_spacing=0.1
            )

            fig.add_trace(
                go.Scatter(x=periods, y=prices, mode='lines+markers', name='Average Price'),
                row=1, col=1
            )

            fig.add_trace(
                go.Scatter(x=periods, y=volumes, mode='lines+markers', name='Total Volume'),
                row=2, col=1
            )

            fig.update_layout(
                title="Market Trends Analysis",
                height=600,
                showlegend=True
            )

            return fig.to_html(include_plotlyjs='cdn')

        except Exception as e:
            logger.error(f"Error creating market trends chart: {e}")
            return "Error creating market trends chart"

    async def _create_developer_performance_chart(self, data: dict[str, Any]) -> str:
        """Create developer performance chart"""
        try:
            developers = data.get('top_developers', [])
            if not developers:
                return "No data available for developer performance"

            names = [d['developer_name'] for d in developers]
            market_shares = [d['market_share'] for d in developers]

            fig = go.Figure(data=[
                go.Bar(x=names, y=market_shares, name='Market Share (%)')
            ])

            fig.update_layout(
                title="Top Developers by Market Share",
                xaxis_title="Developer",
                yaxis_title="Market Share (%)",
                height=500
            )

            return fig.to_html(include_plotlyjs='cdn')

        except Exception as e:
            logger.error(f"Error creating developer performance chart: {e}")
            return "Error creating developer performance chart"

    async def _create_rental_analysis_chart(self, data: dict[str, Any]) -> str:
        """Create rental analysis chart"""
        try:
            rental_data = data.get('rental_market', [])
            if not rental_data:
                return "No data available for rental analysis"

            areas = [r['area_name'] for r in rental_data]
            avg_rents = [r['avg_rent_amount'] for r in rental_data]
            yields = [r['rental_yield'] for r in rental_data]

            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Average Rent by Area', 'Rental Yield by Area'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}]]
            )

            fig.add_trace(
                go.Bar(x=areas, y=avg_rents, name='Average Rent'),
                row=1, col=1
            )

            fig.add_trace(
                go.Bar(x=areas, y=yields, name='Rental Yield'),
                row=1, col=2
            )

            fig.update_layout(
                title="Rental Market Analysis",
                height=500
            )

            return fig.to_html(include_plotlyjs='cdn')

        except Exception as e:
            logger.error(f"Error creating rental analysis chart: {e}")
            return "Error creating rental analysis chart"

# Global instance
_enhanced_analytics = None

async def get_enhanced_analytics(database_url: str = None) -> EnhancedAnalytics:
    """Get global enhanced analytics instance"""
    global _enhanced_analytics
    if _enhanced_analytics is None:
        if database_url is None:
            import os
            database_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/propcalc')
        _enhanced_analytics = EnhancedAnalytics(database_url)
    return _enhanced_analytics

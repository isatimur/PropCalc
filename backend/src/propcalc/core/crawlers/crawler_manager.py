"""
Crawler Manager for Property Websites
Orchestrates multiple crawlers and manages data aggregation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

from .base_crawler import PropertyData
from .property_finder_crawler import PropertyFinderCrawler
from .bayut_crawler import BayutCrawler

logger = logging.getLogger(__name__)

class CrawlerManager:
    """Manages multiple property website crawlers"""
    
    def __init__(self, output_dir: str = "data/crawled"):
        self.crawlers = {
            'propertyfinder': PropertyFinderCrawler(),
            'bayut': BayutCrawler()
        }
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Data storage
        self.crawled_data: Dict[str, List[PropertyData]] = {}
        self.aggregated_data: Optional[pd.DataFrame] = None
        
        logger.info(f"Initialized CrawlerManager with output directory: {self.output_dir}")
    
    async def crawl_all_sources(self, max_pages_per_source: int = 5) -> Dict[str, List[PropertyData]]:
        """Crawl all configured property sources"""
        logger.info(f"Starting crawl of {len(self.crawlers)} sources")
        
        all_properties = {}
        
        for source_name, crawler in self.crawlers.items():
            try:
                logger.info(f"Starting crawl of {source_name}")
                
                async with crawler:
                    properties = await crawler.crawl_properties(max_pages_per_source)
                    all_properties[source_name] = properties
                    
                    logger.info(f"✅ Completed {source_name}: {len(properties)} properties")
                    
                    # Save individual source data
                    await self._save_source_data(source_name, properties)
                    
            except Exception as e:
                logger.error(f"❌ Error crawling {source_name}: {e}")
                all_properties[source_name] = []
        
        self.crawled_data = all_properties
        return all_properties
    
    async def crawl_single_source(self, source_name: str, max_pages: int = 5) -> List[PropertyData]:
        """Crawl a single property source"""
        if source_name not in self.crawlers:
            raise ValueError(f"Unknown source: {source_name}")
        
        crawler = self.crawlers[source_name]
        logger.info(f"Starting crawl of {source_name}")
        
        try:
            async with crawler:
                properties = await crawler.crawl_properties(max_pages)
                
                # Save source data
                await self._save_source_data(source_name, properties)
                
                # Update crawled data
                if source_name not in self.crawled_data:
                    self.crawled_data[source_name] = []
                self.crawled_data[source_name] = properties
                
                logger.info(f"✅ Completed {source_name}: {len(properties)} properties")
                return properties
                
        except Exception as e:
            logger.error(f"❌ Error crawling {source_name}: {e}")
            return []
    
    async def _save_source_data(self, source_name: str, properties: List[PropertyData]):
        """Save crawled data for a specific source"""
        if not properties:
            return
        
        try:
            # Convert to DataFrame
            df = await self.crawlers[source_name].save_to_dataframe(properties)
            
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = self.output_dir / f"{source_name}_{timestamp}.csv"
            df.to_csv(csv_filename, index=False)
            
            # Save to JSON
            json_filename = self.output_dir / f"{source_name}_{timestamp}.json"
            df.to_json(json_filename, orient='records', indent=2)
            
            logger.info(f"Saved {source_name} data: {csv_filename}, {json_filename}")
            
        except Exception as e:
            logger.error(f"Error saving {source_name} data: {e}")
    
    async def aggregate_data(self) -> pd.DataFrame:
        """Aggregate data from all sources into a single DataFrame"""
        if not self.crawled_data:
            logger.warning("No crawled data available. Run crawl_all_sources() first.")
            return pd.DataFrame()
        
        all_properties = []
        
        for source_name, properties in self.crawled_data.items():
            if properties:
                # Convert to DataFrame
                df = await self.crawlers[source_name].save_to_dataframe(properties)
                all_properties.append(df)
        
        if all_properties:
            # Combine all DataFrames
            self.aggregated_data = pd.concat(all_properties, ignore_index=True)
            
            # Add metadata
            self.aggregated_data['aggregated_at'] = datetime.now()
            self.aggregated_data['total_sources'] = len([p for p in self.crawled_data.values() if p])
            
            # Save aggregated data
            await self._save_aggregated_data()
            
            logger.info(f"✅ Aggregated data from {len(all_properties)} sources: {len(self.aggregated_data)} properties")
            return self.aggregated_data
        else:
            logger.warning("No properties to aggregate")
            return pd.DataFrame()
    
    async def _save_aggregated_data(self):
        """Save aggregated data to files"""
        if self.aggregated_data is None or self.aggregated_data.empty:
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save to CSV
            csv_filename = self.output_dir / f"aggregated_properties_{timestamp}.csv"
            self.aggregated_data.to_csv(csv_filename, index=False)
            
            # Save to JSON
            json_filename = self.output_dir / f"aggregated_properties_{timestamp}.json"
            self.aggregated_data.to_json(json_filename, orient='records', indent=2)
            
            # Save to Parquet (for better performance with large datasets)
            parquet_filename = self.output_dir / f"aggregated_properties_{timestamp}.parquet"
            self.aggregated_data.to_parquet(parquet_filename, index=False)
            
            logger.info(f"Saved aggregated data: {csv_filename}, {json_filename}, {parquet_filename}")
            
        except Exception as e:
            logger.error(f"Error saving aggregated data: {e}")
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary statistics of crawled data"""
        summary = {
            'total_sources': len(self.crawlers),
            'crawled_sources': len([p for p in self.crawled_data.values() if p]),
            'total_properties': 0,
            'source_breakdown': {},
            'data_quality': {},
            'price_ranges': {},
            'location_distribution': {},
            'property_types': {}
        }
        
        if self.aggregated_data is not None and not self.aggregated_data.empty:
            df = self.aggregated_data
            summary['total_properties'] = len(df)
            
            # Source breakdown
            if 'source' in df.columns:
                summary['source_breakdown'] = df['source'].value_counts().to_dict()
            
            # Data quality
            if 'data_quality_score' in df.columns:
                summary['data_quality'] = {
                    'average_score': df['data_quality_score'].mean(),
                    'min_score': df['data_quality_score'].min(),
                    'max_score': df['data_quality_score'].max()
                }
            
            # Price ranges
            if 'price' in df.columns:
                price_data = df['price'].dropna()
                if not price_data.empty:
                    summary['price_ranges'] = {
                        'min_price': price_data.min(),
                        'max_price': price_data.max(),
                        'average_price': price_data.mean(),
                        'median_price': price_data.median()
                    }
            
            # Location distribution
            if 'location' in df.columns:
                summary['location_distribution'] = df['location'].value_counts().head(10).to_dict()
            
            # Property types
            if 'property_type' in df.columns:
                summary['property_types'] = df['property_type'].value_counts().to_dict()
        
        return summary
    
    def find_similar_properties(self, target_property: PropertyData, 
                              similarity_threshold: float = 0.7) -> List[PropertyData]:
        """Find similar properties based on various criteria"""
        if self.aggregated_data is None or self.aggregated_data.empty:
            logger.warning("No aggregated data available for similarity search")
            return []
        
        similar_properties = []
        df = self.aggregated_data
        
        for _, row in df.iterrows():
            similarity_score = self._calculate_similarity(target_property, row)
            if similarity_score >= similarity_threshold:
                # Convert row back to PropertyData
                similar_prop = self._row_to_property_data(row)
                similar_prop.data_quality_score = similarity_score
                similar_properties.append(similar_prop)
        
        # Sort by similarity score
        similar_properties.sort(key=lambda x: x.data_quality_score or 0, reverse=True)
        
        logger.info(f"Found {len(similar_properties)} similar properties")
        return similar_properties
    
    def _calculate_similarity(self, target: PropertyData, candidate_row) -> float:
        """Calculate similarity score between two properties"""
        score = 0
        max_score = 0
        
        # Location similarity (high weight)
        if target.location and candidate_row.get('location'):
            if target.location.lower() in candidate_row['location'].lower():
                score += 30
            max_score += 30
        
        # Property type similarity (high weight)
        if target.property_type and candidate_row.get('property_type'):
            if target.property_type.lower() == candidate_row['property_type'].lower():
                score += 25
            max_score += 25
        
        # Bedrooms similarity (medium weight)
        if target.bedrooms and candidate_row.get('bedrooms'):
            if target.bedrooms == candidate_row['bedrooms']:
                score += 15
            elif abs(target.bedrooms - candidate_row['bedrooms']) == 1:
                score += 10
            max_score += 15
        
        # Bathrooms similarity (medium weight)
        if target.bathrooms and candidate_row.get('bathrooms'):
            if target.bathrooms == candidate_row['bathrooms']:
                score += 15
            elif abs(target.bathrooms - candidate_row['bathrooms']) == 1:
                score += 10
            max_score += 15
        
        # Area similarity (medium weight)
        if target.area_sqft and candidate_row.get('area_sqft'):
            area_diff = abs(target.area_sqft - candidate_row['area_sqft'])
            area_percentage = area_diff / target.area_sqft
            if area_percentage <= 0.1:  # Within 10%
                score += 15
            elif area_percentage <= 0.2:  # Within 20%
                score += 10
            max_score += 15
        
        # Price similarity (low weight for now, as prices vary significantly)
        if target.price and candidate_row.get('price'):
            price_diff = abs(target.price - candidate_row['price'])
            price_percentage = price_diff / target.price
            if price_percentage <= 0.2:  # Within 20%
                score += 5
            max_score += 5
        
        return score / max_score if max_score > 0 else 0
    
    def _row_to_property_data(self, row) -> PropertyData:
        """Convert DataFrame row back to PropertyData"""
        # This is a simplified conversion - in practice, you'd want more robust handling
        return PropertyData(
            source=row.get('source', ''),
            source_id=row.get('source_id', ''),
            url=row.get('url', ''),
            title=row.get('title', ''),
            price=row.get('price'),
            price_currency=row.get('price_currency', 'AED'),
            location=row.get('location', ''),
            property_type=row.get('property_type', ''),
            bedrooms=row.get('bedrooms'),
            bathrooms=row.get('bathrooms'),
            area_sqft=row.get('area_sqft'),
            area_sqm=row.get('area_sqm'),
            developer=row.get('developer'),
            completion_date=row.get('completion_date'),
            description=row.get('description'),
            amenities=row.get('amenities', '').split(';') if row.get('amenities') else [],
            images=row.get('images', '').split(';') if row.get('images') else [],
            coordinates={'lat': row.get('latitude'), 'lng': row.get('longitude')} if row.get('latitude') and row.get('longitude') else None,
            listing_date=row.get('listing_date'),
            last_updated=row.get('last_updated'),
            agent_name=row.get('agent_name'),
            agent_phone=row.get('agent_phone'),
            agent_email=row.get('agent_email'),
            verification_status=row.get('verification_status', 'unverified'),
            data_quality_score=row.get('data_quality_score'),
            raw_data=row.to_dict()
        )
    
    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old crawled data files"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for file_path in self.output_dir.glob("*"):
            if file_path.is_file():
                file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_age < cutoff_date:
                    try:
                        file_path.unlink()
                        logger.info(f"Deleted old file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting {file_path}: {e}")
    
    def get_crawler_status(self) -> Dict[str, Any]:
        """Get status of all crawlers"""
        status = {}
        
        for source_name, crawler in self.crawlers.items():
            status[source_name] = {
                'base_url': crawler.config.base_url,
                'request_delay': crawler.config.request_delay,
                'max_retries': crawler.config.max_retries,
                'respect_robots_txt': crawler.config.respect_robots_txt,
                'current_page': crawler.current_page,
                'request_count': crawler.request_count,
                'session_active': crawler.session is not None
            }
        
        return status

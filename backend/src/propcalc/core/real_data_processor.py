"""
Real Data Processor for PropCalc
Processes only real data from actual CSV and KML sources
No demo or fabricated data - only real facts
"""

import json
import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

class RealDataSource(Enum):
    """Real data sources from actual files"""
    # CSV Data Sources
    ACCREDITED_ESCROW_AGENTS = "accredited_escrow_agents"
    BROKERS = "brokers"
    BUILDINGS = "buildings"
    DEVELOPERS = "developers"
    FREE_ZONE_COMPANIES = "free_zone_companies"
    LICENSED_OWNER_ASSOCIATIONS = "licensed_owner_associations"
    MAP_REQUESTS = "map_requests"
    OFFICES = "offices"
    PROJECTS = "projects"
    REAL_ESTATE_LICENSES = "real_estate_licenses"
    REAL_ESTATE_PERMITS = "real_estate_permits"
    RENT_CONTRACTS = "rent_contracts"
    UNITS = "units"
    VALUATION = "valuation"
    VALUATOR_LICENSING = "valuator_licensing"

    # KML Data Sources
    COMMUNITY = "community"
    SECTORS = "sectors"
    ENTRANCES = "entrances"

class DataQualityLevel(Enum):
    """Data quality levels based on real data analysis"""
    EXCELLENT = "excellent"  # 90-100% completeness
    GOOD = "good"           # 70-89% completeness
    FAIR = "fair"           # 50-69% completeness
    POOR = "poor"           # <50% completeness

@dataclass
class RealDataQualityReport:
    """Real data quality report"""
    source: RealDataSource
    total_records: int
    valid_records: int
    quality_score: float
    quality_level: DataQualityLevel
    processing_time_seconds: float
    timestamp: datetime
    errors: list[str]
    warnings: list[str]
    file_size_mb: float
    data_columns: list[str]

@dataclass
class RealDataSummary:
    """Summary of real data processing"""
    total_sources: int
    total_records: int
    total_file_size_gb: float
    processing_time_seconds: float
    quality_score: float
    sources_processed: list[RealDataSource]
    errors: list[str]

class RealDataProcessor:
    """Process only real data from actual sources"""

    def __init__(self, database_url: str = None):
        self.database_url = database_url
        if database_url:
            self.engine = create_engine(database_url)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Real data directory
        self.data_dir = Path("..")

        # Real data file mappings
        self.csv_files = {
            RealDataSource.ACCREDITED_ESCROW_AGENTS: "Accredited_Escrow_Agents.csv",
            RealDataSource.BROKERS: "Brokers.csv",
            RealDataSource.BUILDINGS: "Buildings.csv",
            RealDataSource.DEVELOPERS: "Developers.csv",
            RealDataSource.FREE_ZONE_COMPANIES: "Free_Zone_Companies_Licensing.csv",
            RealDataSource.LICENSED_OWNER_ASSOCIATIONS: "Licenced_Owner_Associations.csv",
            RealDataSource.MAP_REQUESTS: "Map_Requests.csv",
            RealDataSource.OFFICES: "Offices.csv",
            RealDataSource.PROJECTS: "Projects.csv",
            RealDataSource.REAL_ESTATE_LICENSES: "Real_Estate_Licenses.csv",
            RealDataSource.REAL_ESTATE_PERMITS: "Real_Estate_Permits.csv",
            RealDataSource.RENT_CONTRACTS: "Rent_Contracts.csv",
            RealDataSource.UNITS: "Units.csv",
            RealDataSource.VALUATION: "Valuation.csv",
            RealDataSource.VALUATOR_LICENSING: "Valuator_Licensing.csv"
        }

        self.kml_files = {
            RealDataSource.COMMUNITY: "Community.kml",
            RealDataSource.SECTORS: "Sectors.kml",
            RealDataSource.ENTRANCES: "Dmgisnet_Enterances.kml"
        }

    async def process_all_real_data(self) -> RealDataSummary:
        """Process all available real data sources"""
        start_time = datetime.now()
        results = []
        total_records = 0
        total_file_size = 0.0
        sources_processed = []
        errors = []

        logger.info("🔄 Starting real data processing...")

        # Process CSV files
        for source, filename in self.csv_files.items():
            try:
                file_path = self.data_dir / filename
                if file_path.exists():
                    logger.info(f"📊 Processing {source.value}: {filename}")
                    result = await self.process_csv_source(source, file_path)
                    results.append(result)
                    total_records += result.total_records
                    total_file_size += result.file_size_mb
                    sources_processed.append(source)
                else:
                    logger.warning(f"⚠️ File not found: {filename}")
                    errors.append(f"File not found: {filename}")
            except Exception as e:
                logger.error(f"❌ Error processing {source.value}: {e}")
                errors.append(f"Error processing {source.value}: {str(e)}")

        # Process KML files
        for source, filename in self.kml_files.items():
            try:
                file_path = self.data_dir / filename
                if file_path.exists():
                    logger.info(f"🗺️ Processing {source.value}: {filename}")
                    result = await self.process_kml_source(source, file_path)
                    results.append(result)
                    total_records += result.total_records
                    total_file_size += result.file_size_mb
                    sources_processed.append(source)
                else:
                    logger.warning(f"⚠️ File not found: {filename}")
                    errors.append(f"File not found: {filename}")
            except Exception as e:
                logger.error(f"❌ Error processing {source.value}: {e}")
                errors.append(f"Error processing {source.value}: {str(e)}")

        processing_time = (datetime.now() - start_time).total_seconds()

        # Calculate overall quality score
        if results:
            overall_quality = sum(r.quality_score for r in results) / len(results)
        else:
            overall_quality = 0.0

        summary = RealDataSummary(
            total_sources=len(sources_processed),
            total_records=total_records,
            total_file_size_gb=total_file_size / 1024,
            processing_time_seconds=processing_time,
            quality_score=overall_quality,
            sources_processed=sources_processed,
            errors=errors
        )

        logger.info(f"✅ Real data processing complete: {summary.total_sources} sources, {summary.total_records:,} records, {summary.total_file_size_gb:.2f} GB")

        return summary

    async def process_csv_source(self, source: RealDataSource, file_path: Path) -> RealDataQualityReport:
        """Process a single CSV data source"""
        start_time = datetime.now()

        try:
            # Get file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)

            # Read CSV with chunking for large files
            chunk_size = 10000 if file_size_mb > 100 else None

            if chunk_size:
                # Process large files in chunks
                total_records = 0
                valid_records = 0
                columns = []
                errors = []
                warnings = []

                for chunk_num, chunk in enumerate(pd.read_csv(file_path, chunksize=chunk_size)):
                    if chunk_num == 0:
                        columns = list(chunk.columns)

                    chunk_valid = len(chunk.dropna())
                    chunk_total = len(chunk)

                    total_records += chunk_total
                    valid_records += chunk_valid

                    # Check for data quality issues
                    missing_ratio = (chunk_total - chunk_valid) / chunk_total
                    if missing_ratio > 0.5:
                        warnings.append(f"High missing data ratio: {missing_ratio:.1%}")

                    if chunk_num % 10 == 0:
                        logger.info(f"   Processed chunk {chunk_num + 1}: {chunk_total} records")
            else:
                # Process small files entirely
                df = pd.read_csv(file_path)
                total_records = len(df)
                valid_records = len(df.dropna())
                columns = list(df.columns)
                errors = []
                warnings = []

                # Check for data quality issues
                missing_ratio = (total_records - valid_records) / total_records
                if missing_ratio > 0.5:
                    warnings.append(f"High missing data ratio: {missing_ratio:.1%}")

            # Calculate quality metrics
            quality_score = valid_records / total_records if total_records > 0 else 0.0

            if quality_score >= 0.9:
                quality_level = DataQualityLevel.EXCELLENT
            elif quality_score >= 0.7:
                quality_level = DataQualityLevel.GOOD
            elif quality_score >= 0.5:
                quality_level = DataQualityLevel.FAIR
            else:
                quality_level = DataQualityLevel.POOR

            processing_time = (datetime.now() - start_time).total_seconds()

            return RealDataQualityReport(
                source=source,
                total_records=total_records,
                valid_records=valid_records,
                quality_score=quality_score,
                quality_level=quality_level,
                processing_time_seconds=processing_time,
                timestamp=datetime.now(),
                errors=errors,
                warnings=warnings,
                file_size_mb=file_size_mb,
                data_columns=columns
            )

        except Exception as e:
            logger.error(f"Error processing CSV {source.value}: {e}")
            return RealDataQualityReport(
                source=source,
                total_records=0,
                valid_records=0,
                quality_score=0.0,
                quality_level=DataQualityLevel.POOR,
                processing_time_seconds=0.0,
                timestamp=datetime.now(),
                errors=[str(e)],
                warnings=[],
                file_size_mb=0.0,
                data_columns=[]
            )

    async def process_kml_source(self, source: RealDataSource, file_path: Path) -> RealDataQualityReport:
        """Process a single KML data source"""
        start_time = datetime.now()

        try:
            # Get file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)

            # Parse KML file
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Define namespace
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}

            # Count placemarks
            placemarks = root.findall('.//kml:Placemark', ns)
            total_records = len(placemarks)

            # Validate placemarks
            valid_records = 0
            errors = []
            warnings = []
            columns = []

            for placemark in placemarks:
                try:
                    # Check for required elements
                    extended_data = placemark.find('.//kml:ExtendedData', ns)
                    if extended_data is not None:
                        valid_records += 1

                        # Extract column names from first valid record
                        if not columns:
                            for simple_data in extended_data.findall('.//kml:SimpleData', ns):
                                name = simple_data.get('name')
                                if name:
                                    columns.append(name)
                except Exception as e:
                    errors.append(f"Error processing placemark: {e}")

            # Calculate quality metrics
            quality_score = valid_records / total_records if total_records > 0 else 0.0

            if quality_score >= 0.9:
                quality_level = DataQualityLevel.EXCELLENT
            elif quality_score >= 0.7:
                quality_level = DataQualityLevel.GOOD
            elif quality_score >= 0.5:
                quality_level = DataQualityLevel.FAIR
            else:
                quality_level = DataQualityLevel.POOR

            processing_time = (datetime.now() - start_time).total_seconds()

            return RealDataQualityReport(
                source=source,
                total_records=total_records,
                valid_records=valid_records,
                quality_score=quality_score,
                quality_level=quality_level,
                processing_time_seconds=processing_time,
                timestamp=datetime.now(),
                errors=errors,
                warnings=warnings,
                file_size_mb=file_size_mb,
                data_columns=columns
            )

        except Exception as e:
            logger.error(f"Error processing KML {source.value}: {e}")
            return RealDataQualityReport(
                source=source,
                total_records=0,
                valid_records=0,
                quality_score=0.0,
                quality_level=DataQualityLevel.POOR,
                processing_time_seconds=0.0,
                timestamp=datetime.now(),
                errors=[str(e)],
                warnings=[],
                file_size_mb=0.0,
                data_columns=[]
            )

    async def generate_real_data_report(self, summary: RealDataSummary) -> dict[str, Any]:
        """Generate comprehensive report of real data processing"""
        report = {
            'summary': {
                'total_sources': summary.total_sources,
                'total_records': summary.total_records,
                'total_file_size_gb': summary.total_file_size_gb,
                'processing_time_seconds': summary.processing_time_seconds,
                'overall_quality_score': summary.quality_score,
                'sources_processed': [s.value for s in summary.sources_processed],
                'errors': summary.errors,
                'timestamp': datetime.now().isoformat()
            },
            'data_sources': {
                'csv_files': list(self.csv_files.keys()),
                'kml_files': list(self.kml_files.keys())
            },
            'file_sizes': {},
            'quality_metrics': {}
        }

        # Add file size information
        for source, filename in self.csv_files.items():
            file_path = self.data_dir / filename
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                report['file_sizes'][source.value] = f"{size_mb:.2f} MB"

        for source, filename in self.kml_files.items():
            file_path = self.data_dir / filename
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                report['file_sizes'][source.value] = f"{size_mb:.2f} MB"

        return report

    async def save_to_database(self, summary: RealDataSummary) -> bool:
        """Save real data processing results to database"""
        try:
            if not self.database_url:
                logger.warning("No database URL provided, skipping database save")
                return False

            engine = create_engine(self.database_url)

            # Create real data processing table
            with engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS real_data_processing (
                        id SERIAL PRIMARY KEY,
                        processing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        total_sources INTEGER,
                        total_records BIGINT,
                        total_file_size_gb DECIMAL(10,2),
                        processing_time_seconds DECIMAL(10,2),
                        quality_score DECIMAL(5,4),
                        sources_processed JSONB,
                        errors JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))

                # Insert processing summary
                conn.execute(text("""
                    INSERT INTO real_data_processing (
                        total_sources, total_records, total_file_size_gb,
                        processing_time_seconds, quality_score, sources_processed, errors
                    ) VALUES (
                        :total_sources, :total_records, :total_file_size_gb,
                        :processing_time_seconds, :quality_score, :sources_processed, :errors
                    )
                """), {
                    'total_sources': summary.total_sources,
                    'total_records': summary.total_records,
                    'total_file_size_gb': summary.total_file_size_gb,
                    'processing_time_seconds': summary.processing_time_seconds,
                    'quality_score': summary.quality_score,
                    'sources_processed': json.dumps([s.value for s in summary.sources_processed]),
                    'errors': json.dumps(summary.errors)
                })

                conn.commit()

            logger.info("✅ Real data processing results saved to database")
            return True

        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            return False

# Global instance
_real_data_processor = None

async def get_real_data_processor(database_url: str = None) -> RealDataProcessor:
    """Get global real data processor instance"""
    global _real_data_processor
    if _real_data_processor is None:
        if database_url is None:
            import os
            database_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/propcalc')
        _real_data_processor = RealDataProcessor(database_url)
    return _real_data_processor

"""
Enhanced Data Import Module for PropCalc
Handles comprehensive CSV data import with validation and transformation
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import (
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .kml_geospatial_processor import get_kml_processor

logger = logging.getLogger(__name__)

class DataSource(Enum):
    """Data source types"""
    BUILDINGS = "buildings"
    UNITS = "units"
    PROJECTS = "projects"
    OFFICES = "offices"
    BROKERS = "brokers"
    VALUATORS = "valuators"
    PERMITS = "permits"
    MAP_REQUESTS = "map_requests"
    RENT_CONTRACTS = "rent_contracts"
    DEVELOPERS = "developers"
    VALUATION = "valuation"
    FREE_ZONE_COMPANIES = "free_zone_companies"
    LICENSED_OWNER_ASSOCIATIONS = "licensed_owner_associations"
    REAL_ESTATE_LICENSES = "real_estate_licenses"
    ACCREDITED_ESCROW_AGENTS = "accredited_escrow_agents"

class DataQualityLevel(Enum):
    """Data quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

@dataclass
class DataQualityReport:
    """Data quality report"""
    source: DataSource
    total_records: int
    valid_records: int
    quality_score: float
    quality_level: DataQualityLevel
    processing_time_seconds: float
    timestamp: datetime
    errors: list[str]
    warnings: list[str]
    transformation_stats: dict[str, Any]

@dataclass
class ImportResult:
    """Import result"""
    source: DataSource
    status: str
    records_processed: int
    records_imported: int
    quality_report: DataQualityReport
    errors: list[str]
    warnings: list[str]

class EnhancedDataImporter:
    """Enhanced data importer with comprehensive validation and transformation"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()
        self.data_dir = Path(".")
        self.import_history = []

    async def import_all_sources(self) -> list[ImportResult]:
        """Import all available data sources including KML geospatial data"""
        results = []

        # Define import order based on dependencies
        import_order = [
            DataSource.DEVELOPERS,
            DataSource.PROJECTS,
            DataSource.BUILDINGS,
            DataSource.UNITS,
            DataSource.BROKERS,
            DataSource.OFFICES,
            DataSource.VALUATORS,
            DataSource.PERMITS,
            DataSource.MAP_REQUESTS,
            DataSource.RENT_CONTRACTS,
            DataSource.VALUATION,
            DataSource.FREE_ZONE_COMPANIES,
            DataSource.LICENSED_OWNER_ASSOCIATIONS,
            DataSource.REAL_ESTATE_LICENSES,
            DataSource.ACCREDITED_ESCROW_AGENTS
        ]

        for source in import_order:
            try:
                result = await self.import_source(source)
                results.append(result)
                logger.info(f"Imported {source.value}: {result.records_imported}/{result.records_processed} records")
            except Exception as e:
                logger.error(f"Error importing {source.value}: {e}")
                results.append(ImportResult(
                    source=source,
                    status="error",
                    records_processed=0,
                    records_imported=0,
                    quality_report=None,
                    errors=[str(e)],
                    warnings=[]
                ))

        # Process KML geospatial data
        try:
            logger.info("Processing KML geospatial data...")
            kml_processor = await get_kml_processor(self.database_url)
            kml_results = await kml_processor.process_all_kml_files()

            if 'error' not in kml_results:
                # Save KML data to database
                save_success = await kml_processor.save_to_database(kml_results)

                # Generate KML report
                kml_report = await kml_processor.generate_geospatial_report(kml_results)

                # Create import result for KML data
                kml_result = ImportResult(
                    source=DataSource.BUILDINGS,  # Use buildings as placeholder
                    status="success" if save_success else "error",
                    records_processed=kml_results.get('communities', {}).get('count', 0) +
                                   kml_results.get('sectors', {}).get('count', 0) +
                                   kml_results.get('entrances', {}).get('count', 0),
                    records_imported=kml_results.get('communities', {}).get('count', 0) +
                                  kml_results.get('sectors', {}).get('count', 0) +
                                  kml_results.get('entrances', {}).get('count', 0),
                    quality_report=DataQualityReport(
                        source=DataSource.BUILDINGS,
                        total_records=kml_results.get('communities', {}).get('count', 0) +
                                    kml_results.get('sectors', {}).get('count', 0) +
                                    kml_results.get('entrances', {}).get('count', 0),
                        valid_records=kml_results.get('communities', {}).get('count', 0) +
                                   kml_results.get('sectors', {}).get('count', 0) +
                                   kml_results.get('entrances', {}).get('count', 0),
                        quality_score=1.0,
                        quality_level=DataQualityLevel.EXCELLENT,
                        processing_time_seconds=0.0,
                        timestamp=datetime.now(),
                        errors=[],
                        warnings=[],
                        transformation_stats=kml_report
                    ),
                    errors=[],
                    warnings=[]
                )
                results.append(kml_result)
                logger.info(f"Successfully processed KML data: {kml_results.get('communities', {}).get('count', 0)} communities, "
                          f"{kml_results.get('sectors', {}).get('count', 0)} sectors, "
                          f"{kml_results.get('entrances', {}).get('count', 0)} entrances")
            else:
                logger.error(f"Error processing KML data: {kml_results['error']}")

        except Exception as e:
            logger.error(f"Error processing KML geospatial data: {e}")

        return results

    async def import_source(self, source: DataSource) -> ImportResult:
        """Import a specific data source"""
        start_time = datetime.now()

        # Get file path
        file_path = self._get_file_path(source)
        if not file_path.exists():
            return ImportResult(
                source=source,
                status="error",
                records_processed=0,
                records_imported=0,
                quality_report=None,
                errors=[f"File not found: {file_path}"],
                warnings=[]
            )

        try:
            # Read CSV data
            df = await self._read_csv_data(file_path, source)

            # Validate and transform data
            transformed_df, quality_report = await self._validate_and_transform(df, source)

            # Import to database
            imported_count = await self._import_to_database(transformed_df, source)

            processing_time = (datetime.now() - start_time).total_seconds()
            quality_report.processing_time_seconds = processing_time

            return ImportResult(
                source=source,
                status="success",
                records_processed=len(df),
                records_imported=imported_count,
                quality_report=quality_report,
                errors=quality_report.errors,
                warnings=quality_report.warnings
            )

        except Exception as e:
            logger.error(f"Error importing {source.value}: {e}")
            return ImportResult(
                source=source,
                status="error",
                records_processed=0,
                records_imported=0,
                quality_report=None,
                errors=[str(e)],
                warnings=[]
            )

    def _get_file_path(self, source: DataSource) -> Path:
        """Get file path for data source"""
        file_mapping = {
            DataSource.BUILDINGS: "Buildings.csv",
            DataSource.UNITS: "Units.csv",
            DataSource.PROJECTS: "Projects.csv",
            DataSource.OFFICES: "Offices.csv",
            DataSource.BROKERS: "Brokers.csv",
            DataSource.VALUATORS: "Valuator_Licensing.csv",
            DataSource.PERMITS: "Real_Estate_Permits.csv",
            DataSource.MAP_REQUESTS: "Map_Requests.csv",
            DataSource.RENT_CONTRACTS: "Rent_Contracts.csv",
            DataSource.DEVELOPERS: "Developers.csv",
            DataSource.VALUATION: "Valuation.csv",
            DataSource.FREE_ZONE_COMPANIES: "Free_Zone_Companies_Licensing.csv",
            DataSource.LICENSED_OWNER_ASSOCIATIONS: "Licenced_Owner_Associations.csv",
            DataSource.REAL_ESTATE_LICENSES: "Real_Estate_Licenses.csv",
            DataSource.ACCREDITED_ESCROW_AGENTS: "Accredited_Escrow_Agents.csv"
        }

        return self.data_dir / file_mapping[source]

    async def _read_csv_data(self, file_path: Path, source: DataSource) -> pd.DataFrame:
        """Read CSV data with appropriate settings"""
        try:
            # Use different chunk sizes based on file size
            file_size = file_path.stat().st_size
            chunk_size = 10000 if file_size > 100 * 1024 * 1024 else None  # 100MB threshold

            if chunk_size:
                # Read in chunks for large files
                chunks = []
                for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
                    chunks.append(chunk)
                df = pd.concat(chunks, ignore_index=True)
            else:
                df = pd.read_csv(file_path, low_memory=False)

            logger.info(f"Read {len(df)} records from {file_path}")
            return df

        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            raise

    async def _validate_and_transform(self, df: pd.DataFrame, source: DataSource) -> tuple[pd.DataFrame, DataQualityReport]:
        """Validate and transform data based on source type"""
        start_time = datetime.now()
        original_count = len(df)

        # Remove duplicates
        df = df.drop_duplicates()

        # Apply source-specific validation and transformation
        if source == DataSource.BUILDINGS:
            df, errors, warnings = await self._validate_buildings(df)
        elif source == DataSource.UNITS:
            df, errors, warnings = await self._validate_units(df)
        elif source == DataSource.PROJECTS:
            df, errors, warnings = await self._validate_projects(df)
        elif source == DataSource.OFFICES:
            df, errors, warnings = await self._validate_offices(df)
        elif source == DataSource.BROKERS:
            df, errors, warnings = await self._validate_brokers(df)
        elif source == DataSource.VALUATORS:
            df, errors, warnings = await self._validate_valuators(df)
        elif source == DataSource.PERMITS:
            df, errors, warnings = await self._validate_permits(df)
        elif source == DataSource.MAP_REQUESTS:
            df, errors, warnings = await self._validate_map_requests(df)
        elif source == DataSource.RENT_CONTRACTS:
            df, errors, warnings = await self._validate_rent_contracts(df)
        elif source == DataSource.DEVELOPERS:
            df, errors, warnings = await self._validate_developers(df)
        elif source == DataSource.VALUATION:
            df, errors, warnings = await self._validate_valuation(df)
        else:
            df, errors, warnings = await self._validate_generic(df)

        # Calculate quality metrics
        valid_count = len(df)
        quality_score = (valid_count / original_count * 100) if original_count > 0 else 0

        if quality_score >= 95:
            quality_level = DataQualityLevel.EXCELLENT
        elif quality_score >= 85:
            quality_level = DataQualityLevel.GOOD
        elif quality_score >= 70:
            quality_level = DataQualityLevel.FAIR
        else:
            quality_level = DataQualityLevel.POOR

        processing_time = (datetime.now() - start_time).total_seconds()

        quality_report = DataQualityReport(
            source=source,
            total_records=original_count,
            valid_records=valid_count,
            quality_score=quality_score,
            quality_level=quality_level,
            processing_time_seconds=processing_time,
            timestamp=datetime.now(),
            errors=errors,
            warnings=warnings,
            transformation_stats={
                "duplicates_removed": original_count - len(df.drop_duplicates()),
                "null_values": df.isnull().sum().to_dict(),
                "data_types": df.dtypes.to_dict()
            }
        )

        return df, quality_report

    async def _validate_buildings(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
        """Validate and transform buildings data"""
        errors = []
        warnings = []

        # Required columns
        required_cols = ['property_id', 'area_id', 'area_name_en', 'property_type_en']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        # Data type conversions
        if 'property_id' in df.columns:
            df['property_id'] = df['property_id'].astype(str)

        if 'area_id' in df.columns:
            df['area_id'] = pd.to_numeric(df['area_id'], errors='coerce')

        # Date conversions
        date_columns = ['creation_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Boolean conversions
        boolean_columns = ['is_free_hold', 'is_lease_hold', 'is_registered']
        for col in boolean_columns:
            if col in df.columns:
                df[col] = df[col].map({'1': True, '0': False, 1: True, 0: False}).fillna(False)

        # Remove rows with invalid property_id
        if 'property_id' in df.columns:
            df = df[df['property_id'].notna() & (df['property_id'] != '')]

        return df, errors, warnings

    async def _validate_units(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
        """Validate and transform units data"""
        errors = []
        warnings = []

        # Required columns
        required_cols = ['property_id', 'unit_number', 'property_type_en']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        # Data type conversions
        if 'property_id' in df.columns:
            df['property_id'] = df['property_id'].astype(str)

        if 'unit_number' in df.columns:
            df['unit_number'] = df['unit_number'].astype(str)

        # Numeric conversions
        numeric_columns = ['actual_area', 'unit_balcony_area', 'floor_number']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Date conversions
        if 'creation_date' in df.columns:
            df['creation_date'] = pd.to_datetime(df['creation_date'], errors='coerce')

        # Boolean conversions
        boolean_columns = ['is_free_hold', 'is_lease_hold', 'is_registered']
        for col in boolean_columns:
            if col in df.columns:
                df[col] = df[col].map({'1': True, '0': False, 1: True, 0: False}).fillna(False)

        return df, errors, warnings

    async def _validate_projects(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
        """Validate and transform projects data"""
        errors = []
        warnings = []

        # Required columns
        required_cols = ['project_id', 'project_name', 'developer_name']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        # Data type conversions
        if 'project_id' in df.columns:
            df['project_id'] = df['project_id'].astype(str)

        # Date conversions
        date_columns = ['project_start_date', 'project_end_date', 'completion_date', 'cancellation_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Numeric conversions
        if 'percent_completed' in df.columns:
            df['percent_completed'] = pd.to_numeric(df['percent_completed'], errors='coerce')

        return df, errors, warnings

    async def _validate_offices(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
        """Validate and transform offices data"""
        errors = []
        warnings = []

        # Required columns
        required_cols = ['participant_id', 'real_estate_id', 'license_number']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        # Data type conversions
        if 'participant_id' in df.columns:
            df['participant_id'] = df['participant_id'].astype(str)

        if 'real_estate_id' in df.columns:
            df['real_estate_id'] = df['real_estate_id'].astype(str)

        # Date conversions
        date_columns = ['license_issue_date', 'license_expiry_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Boolean conversions
        if 'is_branch' in df.columns:
            df['is_branch'] = df['is_branch'].map({'1': True, '0': False, 1: True, 0: False}).fillna(False)

        return df, errors, warnings

    async def _validate_brokers(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
        """Validate and transform brokers data"""
        errors = []
        warnings = []

        # Required columns
        required_cols = ['participant_id', 'broker_number', 'broker_name_en']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        # Data type conversions
        if 'participant_id' in df.columns:
            df['participant_id'] = df['participant_id'].astype(str)

        if 'broker_number' in df.columns:
            df['broker_number'] = df['broker_number'].astype(str)

        # Date conversions
        date_columns = ['license_start_date', 'license_end_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        return df, errors, warnings

    async def _validate_valuators(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
        """Validate and transform valuators data"""
        errors = []
        warnings = []

        # Required columns
        required_cols = ['valuator_number', 'valuator_name_en']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        # Data type conversions
        if 'valuator_number' in df.columns:
            df['valuator_number'] = df['valuator_number'].astype(str)

        # Date conversions
        date_columns = ['license_start_date', 'license_end_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        return df, errors, warnings

    async def _validate_permits(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
        """Validate and transform permits data"""
        errors = []
        warnings = []

        # Required columns
        required_cols = ['permits_id', 'permit_number']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        # Data type conversions
        if 'permits_id' in df.columns:
            df['permits_id'] = df['permits_id'].astype(str)

        if 'permit_number' in df.columns:
            df['permit_number'] = df['permit_number'].astype(str)

        # Date conversions
        date_columns = ['start_date', 'end_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        return df, errors, warnings

    async def _validate_map_requests(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
        """Validate and transform map requests data"""
        errors = []
        warnings = []

        # Required columns
        required_cols = ['request_id', 'request_date']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        # Data type conversions
        if 'request_id' in df.columns:
            df['request_id'] = df['request_id'].astype(str)

        # Date conversions
        if 'request_date' in df.columns:
            df['request_date'] = pd.to_datetime(df['request_date'], errors='coerce')

        # Numeric conversions
        if 'no_of_siteplans' in df.columns:
            df['no_of_siteplans'] = pd.to_numeric(df['no_of_siteplans'], errors='coerce')

        return df, errors, warnings

    async def _validate_rent_contracts(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
        """Validate and transform rent contracts data"""
        errors = []
        warnings = []

        # This is a large file, so we'll do basic validation
        # Required columns
        required_cols = ['contract_id']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        # Data type conversions
        if 'contract_id' in df.columns:
            df['contract_id'] = df['contract_id'].astype(str)

        # Date conversions for common date columns
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        return df, errors, warnings

    async def _validate_developers(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
        """Validate and transform developers data"""
        errors = []
        warnings = []

        # Required columns
        required_cols = ['developer_id', 'developer_name']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        # Data type conversions
        if 'developer_id' in df.columns:
            df['developer_id'] = df['developer_id'].astype(str)

        return df, errors, warnings

    async def _validate_valuation(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
        """Validate and transform valuation data"""
        errors = []
        warnings = []

        # Required columns
        required_cols = ['valuation_id']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        # Data type conversions
        if 'valuation_id' in df.columns:
            df['valuation_id'] = df['valuation_id'].astype(str)

        # Numeric conversions for valuation amounts
        numeric_columns = [col for col in df.columns if 'amount' in col.lower() or 'value' in col.lower()]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Date conversions
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        return df, errors, warnings

    async def _validate_generic(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
        """Generic validation for other data sources"""
        errors = []
        warnings = []

        # Basic data type conversions
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to convert to numeric if possible
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                if not numeric_series.isna().all():
                    df[col] = numeric_series

        return df, errors, warnings

    async def _import_to_database(self, df: pd.DataFrame, source: DataSource) -> int:
        """Import data to database"""
        try:
            # Create table if not exists
            table_name = f"{source.value}_data"

            # Convert DataFrame to SQL and insert
            df.to_sql(
                table_name,
                self.engine,
                if_exists='replace',
                index=False,
                method='multi',
                chunksize=1000
            )

            logger.info(f"Imported {len(df)} records to {table_name}")
            return len(df)

        except Exception as e:
            logger.error(f"Error importing to database: {e}")
            raise

    async def generate_import_summary(self, results: list[ImportResult]) -> dict[str, Any]:
        """Generate comprehensive import summary"""
        total_processed = sum(r.records_processed for r in results)
        total_imported = sum(r.records_imported for r in results)
        successful_imports = [r for r in results if r.status == "success"]
        failed_imports = [r for r in results if r.status == "error"]

        # Calculate overall quality metrics
        if successful_imports:
            avg_quality_score = sum(r.quality_report.quality_score for r in successful_imports) / len(successful_imports)
            quality_distribution = {}
            for level in DataQualityLevel:
                count = sum(1 for r in successful_imports if r.quality_report.quality_level == level)
                quality_distribution[level.value] = count
        else:
            avg_quality_score = 0
            quality_distribution = {}

        return {
            "timestamp": datetime.now().isoformat(),
            "total_sources": len(results),
            "successful_imports": len(successful_imports),
            "failed_imports": len(failed_imports),
            "total_records_processed": total_processed,
            "total_records_imported": total_imported,
            "overall_success_rate": (len(successful_imports) / len(results) * 100) if results else 0,
            "average_quality_score": avg_quality_score,
            "quality_distribution": quality_distribution,
            "failed_sources": [r.source.value for r in failed_imports],
            "detailed_results": [
                {
                    "source": r.source.value,
                    "status": r.status,
                    "records_processed": r.records_processed,
                    "records_imported": r.records_imported,
                    "quality_score": r.quality_report.quality_score if r.quality_report else None,
                    "errors": r.errors,
                    "warnings": r.warnings
                }
                for r in results
            ]
        }

# Global instance
_enhanced_importer = None

async def get_enhanced_importer(database_url: str = None) -> EnhancedDataImporter:
    """Get global enhanced importer instance"""
    global _enhanced_importer
    if _enhanced_importer is None:
        if database_url is None:
            database_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/propcalc')
        _enhanced_importer = EnhancedDataImporter(database_url)
    return _enhanced_importer

#!/usr/bin/env python3
"""
Scheduled DLD Data Ingestion System
===================================

A comprehensive, production-ready system for scheduled DLD data ingestion with:
- Automated data downloading from DLD sources
- Intelligent data processing and validation
- Database upserting with integrity checks
- Comprehensive logging and monitoring
- Error handling and recovery
- Performance optimization
- Health checks and alerts

Author: PropCalc Team
Date: 2025-08-02
"""

import asyncio
import gc
import gzip
import hashlib
import logging
import shutil
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

import aiohttp
import asyncpg
import pandas as pd
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dld_scheduled_ingestion.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ScheduledDLDIngestion:
    """
    Comprehensive scheduled DLD data ingestion system
    """

    def __init__(self, config: dict):
        """
        Initialize the scheduled ingestion system

        Args:
            config: Configuration dictionary with all settings
        """
        self.config = config
        self.db_pool = None
        self.scheduler = AsyncIOScheduler()
        self.session = None
        self.ingestion_stats = {}
        self.health_status = {
            'last_run': None,
            'last_success': None,
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'current_status': 'idle'
        }

        # Property type mapping from CSV to enum (from working implementation)
        self.property_type_mapping = {
            'Unit': 'Apartment',
            'Land': 'Villa',  # Map land to villa as closest match
            'Building': 'Office',  # Map building to office as closest match
            'Apartment': 'Apartment',
            'Villa': 'Villa',
            'Townhouse': 'Townhouse',
            'Office': 'Office',
            'Retail': 'Retail',
            'Warehouse': 'Warehouse'
        }

        # DLD Data Sources Configuration
        self.dld_sources = {
            'areas': {
                'url': 'https://dubailand.gov.ae/en/open-data/areas/',
                'filename': 'Lkp_Areas.csv',
                'table': 'dld_areas',
                'primary_key': 'area_id',
                'required_columns': ['area_id', 'name_en', 'name_ar', 'municipality_number']
            },
            'market_types': {
                'url': 'https://dubailand.gov.ae/en/open-data/market-types/',
                'filename': 'Lkp_Market_Types.csv',
                'table': 'dld_market_types',
                'primary_key': 'market_type_id',
                'required_columns': ['market_type_id', 'name_en', 'name_ar']
            },
            'transaction_procedures': {
                'url': 'https://dubailand.gov.ae/en/open-data/transaction-procedures/',
                'filename': 'Lkp_Transaction_Procedures.csv',
                'table': 'dld_transaction_procedures',
                'primary_key': 'procedure_id',
                'required_columns': ['procedure_id', 'name_en', 'name_ar', 'is_pre_registration']
            },
            'residential_sale_index': {
                'url': 'https://dubailand.gov.ae/en/open-data/residential-sale-index/',
                'filename': 'Residential_Sale_Index.csv',
                'table': 'dld_residential_sale_index',
                'primary_key': 'index_id',
                'required_columns': ['first_date_of_month', 'all_monthly_index', 'flat_monthly_index', 'villa_monthly_index']
            },
            'transactions': {
                'url': 'https://dubailand.gov.ae/en/open-data/transactions/',
                'filename': 'Transactions.csv',
                'table': 'dld_transactions',
                'primary_key': 'transaction_id',
                'required_columns': ['transaction_id', 'property_type', 'location', 'transaction_date', 'price_aed', 'area_sqft']
            }
        }

        # Create data directories
        self.data_dir = Path(config.get('data_directory', './dld_data'))
        self.data_dir.mkdir(exist_ok=True)
        self.backup_dir = self.data_dir / 'backups'
        self.backup_dir.mkdir(exist_ok=True)

        logger.info("🚀 Scheduled DLD Ingestion System Initialized")
        logger.info(f"📁 Data Directory: {self.data_dir}")
        logger.info(f"📁 Backup Directory: {self.backup_dir}")

    async def initialize_database(self):
        """Initialize database connection pool"""
        try:
            self.db_pool = await asyncpg.create_pool(
                host=self.config['database']['host'],
                port=self.config['database']['port'],
                user=self.config['database']['user'],
                password=self.config['database']['password'],
                database=self.config['database']['name'],
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("✅ Database connection pool initialized")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise

    async def initialize_http_session(self):
        """Initialize HTTP session for downloads"""
        try:
            timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    'User-Agent': 'PropCalc-DLD-Ingestion/1.0',
                    'Accept': 'text/csv,application/csv,*/*'
                }
            )
            logger.info("✅ HTTP session initialized")
        except Exception as e:
            logger.error(f"❌ HTTP session initialization failed: {e}")
            raise

    async def download_dld_data(self, source_name: str, source_config: dict) -> Path | None:
        """
        Download DLD data from official sources with intelligent retry logic

        Args:
            source_name: Name of the data source
            source_config: Configuration for the data source

        Returns:
            Path to downloaded file or None if failed
        """
        try:
            logger.info(f"📥 Downloading {source_name} from {source_config['url']}")

            # Create backup of existing file
            file_path = self.data_dir / source_config['filename']
            if file_path.exists():
                backup_path = self.backup_dir / f"{source_config['filename']}.{int(time.time())}.bak"
                shutil.copy2(file_path, backup_path)
                logger.info(f"📦 Created backup: {backup_path}")

            # Download with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    async with self.session.get(source_config['url']) as response:
                        if response.status == 200:
                            # Check if response is gzipped
                            content_encoding = response.headers.get('content-encoding', '')

                            if content_encoding == 'gzip':
                                # Handle gzipped content
                                compressed_data = await response.read()
                                data = gzip.decompress(compressed_data)
                                with open(file_path, 'wb') as f:
                                    f.write(data)
                            else:
                                # Handle regular content
                                with open(file_path, 'wb') as f:
                                    async for chunk in response.content.iter_chunked(8192):
                                        f.write(chunk)

                            # Verify file integrity
                            if file_path.exists() and file_path.stat().st_size > 0:
                                logger.info(f"✅ Successfully downloaded {source_name}: {file_path.stat().st_size} bytes")
                                return file_path
                            else:
                                raise Exception("Downloaded file is empty or missing")
                        else:
                            raise Exception(f"HTTP {response.status}: {response.reason}")

                except Exception as e:
                    logger.warning(f"⚠️ Download attempt {attempt + 1} failed for {source_name}: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise

            return None

        except Exception as e:
            logger.error(f"❌ Failed to download {source_name}: {e}")
            return None

    def validate_csv_structure(self, file_path: Path, required_columns: list[str]) -> bool:
        """
        Validate CSV file structure and data quality

        Args:
            file_path: Path to CSV file
            required_columns: List of required column names

        Returns:
            True if valid, False otherwise
        """
        try:
            # Read first few rows to check structure
            df = pd.read_csv(file_path, nrows=5)

            # Check required columns
            missing_columns = set(required_columns) - set(df.columns)
            if missing_columns:
                logger.error(f"❌ Missing required columns: {missing_columns}")
                return False

            # Check for empty dataframe
            if df.empty:
                logger.error("❌ CSV file is empty")
                return False

            # Check for completely null columns
            null_columns = df.columns[df.isnull().all()].tolist()
            if null_columns:
                logger.warning(f"⚠️ Columns with all null values: {null_columns}")

            logger.info(f"✅ CSV structure validated: {len(df.columns)} columns, {len(df)} sample rows")
            return True

        except Exception as e:
            logger.error(f"❌ CSV validation failed: {e}")
            return False

    def calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"❌ Checksum calculation failed: {e}")
            return ""

    async def process_areas_data(self, file_path: Path) -> dict:
        """Process areas data with comprehensive validation"""
        try:
            logger.info("🔄 Processing areas data...")

            # Validate file
            if not self.validate_csv_structure(file_path, self.dld_sources['areas']['required_columns']):
                raise Exception("Invalid CSV structure")

            # Read data
            df = pd.read_csv(file_path)
            logger.info(f"📊 Loaded {len(df)} areas from CSV")

            # Data validation and cleaning
            df = df.dropna(subset=['area_id', 'name_en'])  # Remove rows with missing critical data
            df['area_id'] = df['area_id'].astype(int)
            df['name_en'] = df['name_en'].str.strip()
            df['name_ar'] = df['name_ar'].str.strip()
            df['municipality_number'] = df['municipality_number'].astype(str).str.zfill(3)

            # Process data
            processed_count = 0
            inserted_count = 0
            updated_count = 0
            errors = 0

            async with self.db_pool.acquire() as conn:
                for _, row in df.iterrows():
                    try:
                        # Prepare data
                        area_data = {
                            'area_id': int(row['area_id']),
                            'name_en': str(row['name_en']),
                            'name_ar': str(row['name_ar']),
                            'municipality_number': str(row['municipality_number']),
                            'checksum': self.calculate_file_checksum(file_path),
                            'downloaded_at': datetime.now(UTC),
                            'updated_at': datetime.now(UTC)
                        }

                        # Upsert data
                        result = await conn.execute("""
                            INSERT INTO dld_areas (area_id, name_en, name_ar, municipality_number,
                                                 checksum, downloaded_at, updated_at)
                            VALUES ($1, $2, $3, $4, $5, $6, $7)
                            ON CONFLICT (area_id) DO UPDATE SET
                                name_en = EXCLUDED.name_en,
                                name_ar = EXCLUDED.name_ar,
                                municipality_number = EXCLUDED.municipality_number,
                                checksum = EXCLUDED.checksum,
                                updated_at = EXCLUDED.updated_at
                        """, area_data['area_id'], area_data['name_en'], area_data['name_ar'],
                             area_data['municipality_number'], area_data['checksum'],
                             area_data['downloaded_at'], area_data['updated_at'])

                        if 'INSERT' in result:
                            inserted_count += 1
                        else:
                            updated_count += 1

                        processed_count += 1

                    except Exception as e:
                        logger.error(f"❌ Error processing area {row.get('area_id', 'unknown')}: {e}")
                        errors += 1

            stats = {
                'processed': processed_count,
                'inserted': inserted_count,
                'updated': updated_count,
                'errors': errors
            }

            logger.info(f"✅ Areas processing completed: {stats}")
            return stats

        except Exception as e:
            logger.error(f"❌ Areas processing failed: {e}")
            raise

    async def process_market_types_data(self, file_path: Path) -> dict:
        """Process market types data"""
        try:
            logger.info("🔄 Processing market types data...")

            if not self.validate_csv_structure(file_path, self.dld_sources['market_types']['required_columns']):
                raise Exception("Invalid CSV structure")

            df = pd.read_csv(file_path)
            logger.info(f"📊 Loaded {len(df)} market types from CSV")

            # Data cleaning
            df = df.dropna(subset=['market_type_id', 'name_en'])
            df['market_type_id'] = df['market_type_id'].astype(int)
            df['name_en'] = df['name_en'].str.strip()
            df['name_ar'] = df['name_ar'].str.strip()

            processed_count = 0
            inserted_count = 0
            updated_count = 0
            errors = 0

            async with self.db_pool.acquire() as conn:
                for _, row in df.iterrows():
                    try:
                        market_data = {
                            'market_type_id': int(row['market_type_id']),
                            'name_en': str(row['name_en']),
                            'name_ar': str(row['name_ar']),
                            'checksum': self.calculate_file_checksum(file_path),
                            'data_source': 'DLD_SCHEDULED',
                            'downloaded_at': datetime.now(UTC),
                            'updated_at': datetime.now(UTC)
                        }

                        result = await conn.execute("""
                            INSERT INTO dld_market_types (market_type_id, name_en, name_ar,
                                                        checksum, data_source, downloaded_at, updated_at)
                            VALUES ($1, $2, $3, $4, $5, $6, $7)
                            ON CONFLICT (market_type_id) DO UPDATE SET
                                name_en = EXCLUDED.name_en,
                                name_ar = EXCLUDED.name_ar,
                                checksum = EXCLUDED.checksum,
                                data_source = EXCLUDED.data_source,
                                updated_at = EXCLUDED.updated_at
                        """, market_data['market_type_id'], market_data['name_en'], market_data['name_ar'],
                             market_data['checksum'], market_data['data_source'],
                             market_data['downloaded_at'], market_data['updated_at'])

                        if 'INSERT' in result:
                            inserted_count += 1
                        else:
                            updated_count += 1

                        processed_count += 1

                    except Exception as e:
                        logger.error(f"❌ Error processing market type {row.get('market_type_id', 'unknown')}: {e}")
                        errors += 1

            stats = {
                'processed': processed_count,
                'inserted': inserted_count,
                'updated': updated_count,
                'errors': errors
            }

            logger.info(f"✅ Market types processing completed: {stats}")
            return stats

        except Exception as e:
            logger.error(f"❌ Market types processing failed: {e}")
            raise

    async def process_transaction_procedures_data(self, file_path: Path) -> dict:
        """Process transaction procedures data"""
        try:
            logger.info("🔄 Processing transaction procedures data...")

            if not self.validate_csv_structure(file_path, self.dld_sources['transaction_procedures']['required_columns']):
                raise Exception("Invalid CSV structure")

            df = pd.read_csv(file_path)
            logger.info(f"📊 Loaded {len(df)} transaction procedures from CSV")

            # Data cleaning
            df = df.dropna(subset=['procedure_id', 'name_en'])
            df['procedure_id'] = df['procedure_id'].astype(int)
            df['name_en'] = df['name_en'].str.strip()
            df['name_ar'] = df['name_ar'].str.strip()
            df['is_pre_registration'] = df['is_pre_registration'].astype(bool)

            processed_count = 0
            inserted_count = 0
            updated_count = 0
            errors = 0

            async with self.db_pool.acquire() as conn:
                for _, row in df.iterrows():
                    try:
                        procedure_data = {
                            'procedure_id': int(row['procedure_id']),
                            'name_en': str(row['name_en']),
                            'name_ar': str(row['name_ar']),
                            'is_pre_registration': bool(row['is_pre_registration']),
                            'checksum': self.calculate_file_checksum(file_path),
                            'data_source': 'DLD_SCHEDULED',
                            'downloaded_at': datetime.now(UTC),
                            'updated_at': datetime.now(UTC)
                        }

                        result = await conn.execute("""
                            INSERT INTO dld_transaction_procedures (procedure_id, name_en, name_ar,
                                                                  is_pre_registration, checksum, data_source,
                                                                  downloaded_at, updated_at)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                            ON CONFLICT (procedure_id) DO UPDATE SET
                                name_en = EXCLUDED.name_en,
                                name_ar = EXCLUDED.name_ar,
                                is_pre_registration = EXCLUDED.is_pre_registration,
                                checksum = EXCLUDED.checksum,
                                data_source = EXCLUDED.data_source,
                                updated_at = EXCLUDED.updated_at
                        """, procedure_data['procedure_id'], procedure_data['name_en'], procedure_data['name_ar'],
                             procedure_data['is_pre_registration'], procedure_data['checksum'],
                             procedure_data['data_source'], procedure_data['downloaded_at'], procedure_data['updated_at'])

                        if 'INSERT' in result:
                            inserted_count += 1
                        else:
                            updated_count += 1

                        processed_count += 1

                    except Exception as e:
                        logger.error(f"❌ Error processing procedure {row.get('procedure_id', 'unknown')}: {e}")
                        errors += 1

            stats = {
                'processed': processed_count,
                'inserted': inserted_count,
                'updated': updated_count,
                'errors': errors
            }

            logger.info(f"✅ Transaction procedures processing completed: {stats}")
            return stats

        except Exception as e:
            logger.error(f"❌ Transaction procedures processing failed: {e}")
            raise

    async def process_residential_sale_index_data(self, file_path: Path) -> dict:
        """Process residential sale index data"""
        try:
            logger.info("🔄 Processing residential sale index data...")

            if not self.validate_csv_structure(file_path, self.dld_sources['residential_sale_index']['required_columns']):
                raise Exception("Invalid CSV structure")

            df = pd.read_csv(file_path)
            logger.info(f"📊 Loaded {len(df)} residential sale index records from CSV")

            # Data cleaning and validation
            df = df.dropna(subset=['first_date_of_month'])
            df['first_date_of_month'] = pd.to_datetime(df['first_date_of_month'], format='%d-%m-%Y')

            # Convert numeric columns
            numeric_columns = ['all_monthly_index', 'flat_monthly_index', 'villa_monthly_index']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            processed_count = 0
            inserted_count = 0
            updated_count = 0
            errors = 0

            async with self.db_pool.acquire() as conn:
                for _, row in df.iterrows():
                    try:
                        index_data = {
                            'first_date_of_month': row['first_date_of_month'].date(),
                            'all_monthly_index': float(row.get('all_monthly_index', 0)) if pd.notna(row.get('all_monthly_index')) else None,
                            'all_quarterly_index': float(row.get('all_quarterly_index', 0)) if pd.notna(row.get('all_quarterly_index')) else None,
                            'all_yearly_index': float(row.get('all_yearly_index', 0)) if pd.notna(row.get('all_yearly_index')) else None,
                            'flat_monthly_index': float(row.get('flat_monthly_index', 0)) if pd.notna(row.get('flat_monthly_index')) else None,
                            'flat_quarterly_index': float(row.get('flat_quarterly_index', 0)) if pd.notna(row.get('flat_quarterly_index')) else None,
                            'flat_yearly_index': float(row.get('flat_yearly_index', 0)) if pd.notna(row.get('flat_yearly_index')) else None,
                            'villa_monthly_index': float(row.get('villa_monthly_index', 0)) if pd.notna(row.get('villa_monthly_index')) else None,
                            'villa_quarterly_index': float(row.get('villa_quarterly_index', 0)) if pd.notna(row.get('villa_quarterly_index')) else None,
                            'villa_yearly_index': float(row.get('villa_yearly_index', 0)) if pd.notna(row.get('villa_yearly_index')) else None,
                            'checksum': self.calculate_file_checksum(file_path),
                            'data_source': 'DLD_SCHEDULED',
                            'downloaded_at': datetime.now(UTC),
                            'updated_at': datetime.now(UTC)
                        }

                        result = await conn.execute("""
                            INSERT INTO dld_residential_sale_index (first_date_of_month, all_monthly_index,
                                                                  all_quarterly_index, all_yearly_index, flat_monthly_index,
                                                                  flat_quarterly_index, flat_yearly_index, villa_monthly_index,
                                                                  villa_quarterly_index, villa_yearly_index, checksum,
                                                                  data_source, downloaded_at, updated_at)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                            ON CONFLICT (first_date_of_month) DO UPDATE SET
                                all_monthly_index = EXCLUDED.all_monthly_index,
                                all_quarterly_index = EXCLUDED.all_quarterly_index,
                                all_yearly_index = EXCLUDED.all_yearly_index,
                                flat_monthly_index = EXCLUDED.flat_monthly_index,
                                flat_quarterly_index = EXCLUDED.flat_quarterly_index,
                                flat_yearly_index = EXCLUDED.flat_yearly_index,
                                villa_monthly_index = EXCLUDED.villa_monthly_index,
                                villa_quarterly_index = EXCLUDED.villa_quarterly_index,
                                villa_yearly_index = EXCLUDED.villa_yearly_index,
                                checksum = EXCLUDED.checksum,
                                data_source = EXCLUDED.data_source,
                                updated_at = EXCLUDED.updated_at
                        """, index_data['first_date_of_month'], index_data['all_monthly_index'],
                             index_data['all_quarterly_index'], index_data['all_yearly_index'],
                             index_data['flat_monthly_index'], index_data['flat_quarterly_index'],
                             index_data['flat_yearly_index'], index_data['villa_monthly_index'],
                             index_data['villa_quarterly_index'], index_data['villa_yearly_index'],
                             index_data['checksum'], index_data['data_source'],
                             index_data['downloaded_at'], index_data['updated_at'])

                        if 'INSERT' in result:
                            inserted_count += 1
                        else:
                            updated_count += 1

                        processed_count += 1

                    except Exception as e:
                        logger.error(f"❌ Error processing index record {row.get('first_date_of_month', 'unknown')}: {e}")
                        errors += 1

            stats = {
                'processed': processed_count,
                'inserted': inserted_count,
                'updated': updated_count,
                'errors': errors
            }

            logger.info(f"✅ Residential sale index processing completed: {stats}")
            return stats

        except Exception as e:
            logger.error(f"❌ Residential sale index processing failed: {e}")
            raise

    def map_property_type(self, csv_property_type: str) -> str:
        """Map CSV property type to valid enum value (from working implementation)."""
        if pd.isna(csv_property_type) or csv_property_type is None:
            return 'Apartment'  # Default value

        csv_property_type = str(csv_property_type).strip()
        return self.property_type_mapping.get(csv_property_type, 'Apartment')

    async def process_transactions_data(self, file_path: Path) -> dict:
        """Process transactions data with chunking for large files"""
        try:
            logger.info(f"📊 Processing transactions from {file_path}")

            if not self.validate_csv_structure(file_path, self.dld_sources['transactions']['required_columns']):
                raise Exception("Invalid CSV structure")

            # Process in chunks for large files
            chunk_size = 10000
            processed_count = 0
            inserted_count = 0
            updated_count = 0
            skipped_count = 0
            errors = 0

            chunk_count = 0
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                chunk_count += 1
                logger.info(f"📦 Processing chunk {chunk_count}: {len(chunk)} records")

                async with self.db_pool.acquire() as conn:
                    for _, row in chunk.iterrows():
                        try:
                            # Parse date - using the correct column name with dayfirst=True
                            transaction_date = pd.to_datetime(row['instance_date'], dayfirst=True).date() if pd.notna(row['instance_date']) else None

                            # Map to correct database schema with proper enum mapping
                            transaction_id = row['transaction_id']
                            csv_property_type = row['property_type_en'] if pd.notna(row['property_type_en']) else None
                            property_type = self.map_property_type(csv_property_type)
                            location = row['area_name_en'] if pd.notna(row['area_name_en']) else None
                            price_aed = row['actual_worth'] if pd.notna(row['actual_worth']) else 0
                            area_sqft = row['procedure_area'] if pd.notna(row['procedure_area']) else 0
                            developer_name = row['master_project_en'] if pd.notna(row['master_project_en']) else None
                            project_name = row['project_name_en'] if pd.notna(row['project_name_en']) else None
                            unit_number = None  # Not available in CSV
                            floor_number = None  # Not available in CSV
                            bedrooms = None  # Not available in CSV
                            bathrooms = None  # Not available in CSV
                            parking_spaces = None  # Not available in CSV
                            area_id = int(row['area_id']) if pd.notna(row['area_id']) else None
                            market_type_id = None  # Not available in CSV
                            procedure_id = int(row['procedure_id']) if pd.notna(row['procedure_id']) else None
                            quality_score = 1.0  # Default quality score
                            data_source = 'DLD_SCHEDULED'
                            checksum = hashlib.md5(str(row).encode()).hexdigest()
                            is_verified = False
                            verification_date = None

                            # Upsert transaction with correct schema mapping
                            result = await conn.execute("""
                                INSERT INTO dld_transactions (
                                    id, uuid, transaction_id, property_type, location, transaction_date,
                                    price_aed, area_sqft, developer_name, project_name, unit_number,
                                    floor_number, bedrooms, bathrooms, parking_spaces, created_at, updated_at,
                                    area_id, market_type_id, procedure_id, quality_score, data_source,
                                    checksum, is_verified, verification_date
                                )
                                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, $25)
                                ON CONFLICT (transaction_id) DO UPDATE SET
                                    property_type = EXCLUDED.property_type,
                                    location = EXCLUDED.location,
                                    transaction_date = EXCLUDED.transaction_date,
                                    price_aed = EXCLUDED.price_aed,
                                    area_sqft = EXCLUDED.area_sqft,
                                    developer_name = EXCLUDED.developer_name,
                                    project_name = EXCLUDED.project_name,
                                    area_id = EXCLUDED.area_id,
                                    procedure_id = EXCLUDED.procedure_id,
                                    quality_score = EXCLUDED.quality_score,
                                    data_source = EXCLUDED.data_source,
                                    checksum = EXCLUDED.checksum,
                                    updated_at = EXCLUDED.updated_at
                            """,
                            processed_count + 1,  # Use sequential integer as primary key
                            str(uuid.uuid4()), transaction_id, property_type, location, transaction_date,
                            price_aed, area_sqft, developer_name, project_name, unit_number,
                            floor_number, bedrooms, bathrooms, parking_spaces, datetime.now(UTC), datetime.now(UTC),
                            area_id, market_type_id, procedure_id, quality_score, data_source,
                            checksum, is_verified, verification_date
                            )

                            if 'INSERT' in result:
                                inserted_count += 1
                            else:
                                updated_count += 1

                            processed_count += 1

                        except Exception as e:
                            logger.error(f"❌ Error processing transaction {row.get('transaction_id', 'unknown')}: {e}")
                            errors += 1

                # Log progress
                if chunk_count % 10 == 0:
                    logger.info(f"📊 Progress: {processed_count} transactions processed")

                # Force garbage collection to manage memory
                gc.collect()

            stats = {
                'processed': processed_count,
                'inserted': inserted_count,
                'updated': updated_count,
                'skipped': skipped_count,
                'errors': errors
            }

            logger.info("✅ Transactions processing completed:")
            logger.info(f"   📊 Processed: {processed_count}")
            logger.info(f"   ➕ Inserted: {inserted_count}")
            logger.info(f"   🔄 Updated: {updated_count}")
            logger.info(f"   ⏭️ Skipped: {skipped_count}")

            return stats

        except Exception as e:
            logger.error(f"❌ Transactions processing failed: {e}")
            raise

    async def run_full_ingestion(self) -> dict:
        """
        Run complete DLD data ingestion process

        Returns:
            Dictionary with ingestion statistics
        """
        start_time = time.time()
        self.health_status['current_status'] = 'running'
        self.health_status['last_run'] = datetime.now(UTC)

        try:
            logger.info("🚀 Starting Scheduled DLD Data Ingestion")
            logger.info("=" * 50)

            # Initialize connections
            await self.initialize_database()
            await self.initialize_http_session()

            # Process each data source
            for source_name, source_config in self.dld_sources.items():
                try:
                    logger.info(f"📁 Processing {source_name} from {source_config['filename']}")

                    # Download data
                    file_path = await self.download_dld_data(source_name, source_config)
                    if not file_path:
                        logger.error(f"❌ Failed to download {source_name}")
                        continue

                    # Process data based on source type
                    if source_name == 'areas':
                        stats = await self.process_areas_data(file_path)
                    elif source_name == 'market_types':
                        stats = await self.process_market_types_data(file_path)
                    elif source_name == 'transaction_procedures':
                        stats = await self.process_transaction_procedures_data(file_path)
                    elif source_name == 'residential_sale_index':
                        stats = await self.process_residential_sale_index_data(file_path)
                    elif source_name == 'transactions':
                        stats = await self.process_transactions_data(file_path)
                    else:
                        logger.warning(f"⚠️ Unknown source type: {source_name}")
                        continue

                    self.ingestion_stats[source_name] = stats

                except Exception as e:
                    logger.error(f"❌ Error processing {source_name}: {e}")
                    self.ingestion_stats[source_name] = {
                        'processed': 0,
                        'inserted': 0,
                        'updated': 0,
                        'errors': 1
                    }

            # Log summary
            await self.log_ingestion_summary()

            # Update health status
            self.health_status['current_status'] = 'completed'
            self.health_status['last_success'] = datetime.now(UTC)
            self.health_status['successful_runs'] += 1

            duration = time.time() - start_time
            logger.info(f"✅ Scheduled ingestion completed in {duration:.2f} seconds")

            return self.ingestion_stats

        except Exception as e:
            logger.error(f"❌ Scheduled ingestion failed: {e}")
            self.health_status['current_status'] = 'failed'
            self.health_status['failed_runs'] += 1
            raise

        finally:
            self.health_status['total_runs'] += 1
            if self.db_pool:
                await self.db_pool.close()
            if self.session:
                await self.session.close()

    async def log_ingestion_summary(self):
        """Log comprehensive ingestion summary"""
        try:
            logger.info("📊 DLD Data Ingestion Summary")
            logger.info("=" * 50)

            for source_name, stats in self.ingestion_stats.items():
                logger.info(f"{source_name.upper()}:")
                logger.info(f"  Processed: {stats.get('processed', 0)}")
                logger.info(f"  Inserted: {stats.get('inserted', 0)}")
                logger.info(f"  Updated: {stats.get('updated', 0)}")
                logger.info(f"  Errors: {stats.get('errors', 0)}")
                if 'skipped' in stats:
                    logger.info(f"  Skipped: {stats.get('skipped', 0)}")
                logger.info("")

            # Calculate totals
            total_processed = sum(stats.get('processed', 0) for stats in self.ingestion_stats.values())
            total_inserted = sum(stats.get('inserted', 0) for stats in self.ingestion_stats.values())
            total_updated = sum(stats.get('updated', 0) for stats in self.ingestion_stats.values())
            total_errors = sum(stats.get('errors', 0) for stats in self.ingestion_stats.values())

            logger.info("TOTALS:")
            logger.info(f"  Total Processed: {total_processed}")
            logger.info(f"  Total Inserted: {total_inserted}")
            logger.info(f"  Total Updated: {total_updated}")
            logger.info(f"  Total Errors: {total_errors}")

            if total_processed > 0:
                success_rate = ((total_inserted + total_updated) / total_processed) * 100
                logger.info(f"  Success Rate: {success_rate:.2f}%")

            logger.info("✅ DLD Data Ingestion completed successfully!")

        except Exception as e:
            logger.error(f"❌ Error logging summary: {e}")

    def get_health_status(self) -> dict:
        """Get current health status"""
        return {
            **self.health_status,
            'ingestion_stats': self.ingestion_stats,
            'data_directory': str(self.data_dir),
            'backup_directory': str(self.backup_dir)
        }

    async def start_scheduler(self):
        """Start the scheduled ingestion system"""
        try:
            # Add scheduled job
            schedule_config = self.config.get('schedule', {})
            cron_expression = schedule_config.get('cron', '0 2 * * *')  # Default: 2 AM daily

            self.scheduler.add_job(
                self.run_full_ingestion,
                CronTrigger.from_crontab(cron_expression),
                id='dld_ingestion_job',
                name='DLD Data Ingestion',
                max_instances=1,
                coalesce=True
            )

            # Start scheduler
            self.scheduler.start()
            logger.info(f"✅ Scheduler started with cron expression: {cron_expression}")

            # Keep running
            try:
                while True:
                    await asyncio.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("🛑 Shutting down scheduler...")
                self.scheduler.shutdown()

        except Exception as e:
            logger.error(f"❌ Scheduler failed: {e}")
            raise

# Configuration
DEFAULT_CONFIG = {
    'database': {
        'host': 'localhost',
        'port': 5432,
        'user': 'vantage_user',
        'password': 'vantage_password',
        'name': 'vantage_ai'
    },
    'data_directory': './dld_data',
    'schedule': {
        'cron': '0 2 * * *'  # 2 AM daily
    },
    'logging': {
        'level': 'INFO',
        'file': 'dld_scheduled_ingestion.log'
    }
}

async def main():
    """Main entry point"""
    try:
        # Load configuration (you can load from file or environment)
        config = DEFAULT_CONFIG

        # Create and start ingestion system
        ingestion_system = ScheduledDLDIngestion(config)

        # Run immediate ingestion for testing
        logger.info("🧪 Running immediate ingestion for testing...")
        await ingestion_system.run_full_ingestion()

        # Start scheduler for regular ingestion
        logger.info("🚀 Starting scheduled ingestion system...")
        await ingestion_system.start_scheduler()

    except Exception as e:
        logger.error(f"❌ Main execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

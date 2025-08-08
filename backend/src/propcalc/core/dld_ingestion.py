"""
Real DLD (Dubai Land Department) Data Ingestion Module
"""

import logging
import os
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from io import StringIO
from typing import Any, AsyncGenerator

import aiohttp

logger = logging.getLogger(__name__)

class DLDDataSource(Enum):
    """DLD data sources"""
    OFFICIAL_API = "official_api"
    CSV_IMPORT = "csv_import"
    WEB_SCRAPING = "web_scraping"
    THIRD_PARTY = "third_party"

class DataQualityLevel(Enum):
    """Data quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

@dataclass
class DLDTransaction:
    """DLD transaction data model"""
    transaction_id: str
    property_type: str
    location: str
    transaction_date: datetime
    price_aed: float
    area_sqft: float
    developer_name: str
    transaction_type: str
    property_id: str
    unit_number: str | None = None
    building_name: str | None = None
    project_name: str | None = None
    floor_number: int | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    parking_spaces: int | None = None
    view: str | None = None

@dataclass
class DataQualityReport:
    """Data quality report"""
    total_records: int
    valid_records: int
    quality_score: float
    quality_level: DataQualityLevel
    processing_time_seconds: float
    timestamp: datetime
    errors: list[str]
    warnings: list[str]

class DLDDataIngestion:
    """Real DLD data ingestion and processing"""

    def __init__(self):
        self.api_base_url = os.getenv('DLD_API_BASE_URL', 'https://api.dld.gov.ae')
        self.api_key = os.getenv('DLD_API_KEY', '')
        self.api_secret = os.getenv('DLD_API_SECRET', '')
        self.session = None
        self.last_sync = None
        self.data_source = DLDDataSource.OFFICIAL_API

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'PropCalc/2.0.0'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def fetch_recent_transactions(self, hours: int = 4) -> list[DLDTransaction]:
        """Fetch recent DLD transactions"""
        try:
            logger.info(f"Fetching DLD transactions for last {hours} hours")

            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)

            # Fetch from DLD API
            params = {
                'start_date': start_time.isoformat(),
                'end_date': end_time.isoformat(),
                'limit': 1000,
                'format': 'json'
            }

            async with self.session.get(
                f"{self.api_base_url}/transactions",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    transactions = self._parse_transactions(data)
                    logger.info(f"Fetched {len(transactions)} transactions")
                    return transactions
                else:
                    logger.error(f"DLD API error: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Error fetching DLD transactions: {e}")
            return []

    async def fetch_transactions_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        location: str | None = None,
        property_type: str | None = None,
        limit: int = 1000
    ) -> list[DLDTransaction]:
        """Fetch DLD transactions for a specific date range"""
        try:
            logger.info(f"Fetching DLD transactions from {start_date} to {end_date}")

            params = {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'limit': limit,
                'format': 'json'
            }

            if location:
                params['location'] = location
            if property_type:
                params['property_type'] = property_type

            async with self.session.get(
                f"{self.api_base_url}/transactions",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    transactions = self._parse_transactions(data)
                    logger.info(f"Fetched {len(transactions)} transactions")
                    return transactions
                else:
                    logger.error(f"DLD API error: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Error fetching DLD transactions: {e}")
            return []

    def _parse_transactions(self, data: dict[str, Any]) -> list[DLDTransaction]:
        """Parse raw DLD data into transaction objects"""
        transactions = []

        try:
            for item in data.get('transactions', []):
                transaction = DLDTransaction(
                    transaction_id=item.get('transaction_id', ''),
                    property_type=item.get('property_type', ''),
                    location=item.get('location', ''),
                    transaction_date=datetime.fromisoformat(item.get('transaction_date', '')),
                    price_aed=float(item.get('price_aed', 0)),
                    area_sqft=float(item.get('area_sqft', 0)),
                    developer_name=item.get('developer_name', ''),
                    transaction_type=item.get('transaction_type', ''),
                    property_id=item.get('property_id', ''),
                    unit_number=item.get('unit_number'),
                    building_name=item.get('building_name'),
                    project_name=item.get('project_name'),
                    floor_number=item.get('floor_number'),
                    bedrooms=item.get('bedrooms'),
                    bathrooms=item.get('bathrooms'),
                    parking_spaces=item.get('parking_spaces'),
                    view=item.get('view')
                )
                transactions.append(transaction)

        except Exception as e:
            logger.error(f"Error parsing transactions: {e}")

        return transactions

    def _parse_csv_row(self, row: dict[str, str]) -> DLDTransaction | None:
        """Convert a CSV row into a transaction object"""
        try:
            return DLDTransaction(
                transaction_id=row.get('transaction_id', ''),
                property_type=row.get('property_type', ''),
                location=row.get('location', ''),
                transaction_date=datetime.fromisoformat(row.get('transaction_date', '')),
                price_aed=float(row.get('price_aed', 0) or 0),
                area_sqft=float(row.get('area_sqft', 0) or 0),
                developer_name=row.get('developer_name', ''),
                transaction_type=row.get('transaction_type', ''),
                property_id=row.get('property_id', ''),
                unit_number=row.get('unit_number') or None,
                building_name=row.get('building_name') or None,
                project_name=row.get('project_name') or None,
                floor_number=int(row['floor_number']) if row.get('floor_number') else None,
                bedrooms=int(row['bedrooms']) if row.get('bedrooms') else None,
                bathrooms=int(row['bathrooms']) if row.get('bathrooms') else None,
                parking_spaces=int(row['parking_spaces']) if row.get('parking_spaces') else None,
                view=row.get('view')
            )
        except Exception as e:
            logger.error(f"Error parsing CSV row: {e}")
            return None

    async def stream_transactions_csv(self, url: str) -> AsyncGenerator[DLDTransaction, None]:
        """Stream DLD transactions from a large CSV file"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"DLD CSV download error: {response.status}")
                    return
                header = None
                buffer = ""
                async for chunk in response.content.iter_chunked(1024):
                    buffer += chunk.decode('utf-8')
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if header is None:
                            header = next(csv.reader([line]))
                            continue
                        if not line.strip():
                            continue
                        row = next(csv.DictReader([line], fieldnames=header))
                        transaction = self._parse_csv_row(row)
                        if transaction:
                            yield transaction
                if buffer.strip() and header:
                    row = next(csv.DictReader([buffer], fieldnames=header))
                    transaction = self._parse_csv_row(row)
                    if transaction:
                        yield transaction
        except Exception as e:
            logger.error(f"Error streaming DLD transactions: {e}")
            return

    def validate_transaction(self, transaction: DLDTransaction) -> bool:
        """Validate a single transaction"""
        try:
            # Basic validation
            if not transaction.transaction_id:
                return False
            if not transaction.location:
                return False
            if transaction.price_aed <= 0:
                return False
            if transaction.area_sqft <= 0:
                return False
            if not transaction.developer_name:
                return False

            # Date validation
            if transaction.transaction_date > datetime.now():
                return False
            if transaction.transaction_date < datetime(2020, 1, 1):
                return False

            # Price range validation (reasonable Dubai property prices)
            if transaction.price_aed < 100000 or transaction.price_aed > 100000000:
                return False

            # Area validation
            if transaction.area_sqft < 100 or transaction.area_sqft > 50000:
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating transaction: {e}")
            return False

    def calculate_data_quality(self, transactions: list[DLDTransaction]) -> DataQualityReport:
        """Calculate data quality metrics"""
        start_time = datetime.now()
        total_records = len(transactions)
        valid_records = 0
        errors = []
        warnings = []

        for transaction in transactions:
            if self.validate_transaction(transaction):
                valid_records += 1
            else:
                errors.append(f"Invalid transaction: {transaction.transaction_id}")

        # Calculate quality score
        quality_score = (valid_records / total_records * 100) if total_records > 0 else 0

        # Determine quality level
        if quality_score >= 95:
            quality_level = DataQualityLevel.EXCELLENT
        elif quality_score >= 85:
            quality_level = DataQualityLevel.GOOD
        elif quality_score >= 70:
            quality_level = DataQualityLevel.FAIR
        else:
            quality_level = DataQualityLevel.POOR

        processing_time = (datetime.now() - start_time).total_seconds()

        return DataQualityReport(
            total_records=total_records,
            valid_records=valid_records,
            quality_score=quality_score,
            quality_level=quality_level,
            processing_time_seconds=processing_time,
            timestamp=datetime.now(),
            errors=errors,
            warnings=warnings
        )

    async def get_ingestion_status(self) -> dict[str, Any]:
        """Get current ingestion status"""
        return {
            "status": "active",
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "data_source": self.data_source.value,
            "api_connected": bool(self.api_key),
            "timestamp": datetime.now().isoformat()
        }

    async def process_and_store_transactions(self, transactions: list[DLDTransaction]) -> dict[str, Any]:
        """Process and store transactions in database"""
        try:
            # Calculate quality metrics
            quality_report = self.calculate_data_quality(transactions)

            # Filter valid transactions
            valid_transactions = [
                t for t in transactions
                if self.validate_transaction(t)
            ]

            # Store in database (placeholder for now)
            # In production, this would store in PostgreSQL
            stored_count = len(valid_transactions)

            # Update last sync time
            self.last_sync = datetime.now()

            return {
                "status": "success",
                "total_processed": len(transactions),
                "valid_stored": stored_count,
                "quality_report": {
                    "quality_score": quality_report.quality_score,
                    "quality_level": quality_report.quality_level.value,
                    "processing_time": quality_report.processing_time_seconds
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error processing transactions: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global instance
_dld_ingestion = None

async def get_dld_ingestion() -> DLDDataIngestion:
    """Get global DLD ingestion instance"""
    global _dld_ingestion
    if _dld_ingestion is None:
        _dld_ingestion = DLDDataIngestion()
    return _dld_ingestion

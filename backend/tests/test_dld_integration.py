"""
Comprehensive tests for DLD integration module
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
import asyncio

import pytest

from src.propcalc.core.dld_ingestion import (
    DataQualityLevel,
    DLDDataIngestion,
    DLDDataSource,
    DLDTransaction,
)


class TestDLDTransaction:
    """Test DLD transaction data model"""

    def test_valid_transaction(self):
        """Test creating a valid transaction"""
        transaction = DLDTransaction(
            transaction_id="TEST_001",
            property_type="Apartment",
            location="Dubai Marina",
            transaction_date=datetime.now(),
            price_aed=2500000.0,
            area_sqft=1200.0,
            developer_name="Emaar Properties",
            transaction_type="Sale",
            property_id="MARINA_001",
            unit_number="A-1501",
            building_name="Marina Heights",
            project_name="Marina Heights",
            floor_number=15,
            bedrooms=2,
            bathrooms=2,
            parking_spaces=1,
            view="Marina View"
        )

        assert transaction.transaction_id == "TEST_001"
        assert transaction.property_type == "Apartment"
        assert transaction.location == "Dubai Marina"
        assert transaction.price_aed == 2500000.0
        assert transaction.area_sqft == 1200.0
        assert transaction.developer_name == "Emaar Properties"
        assert transaction.bedrooms == 2
        assert transaction.bathrooms == 2
        assert transaction.parking_spaces == 1
        assert transaction.view == "Marina View"

    def test_minimal_transaction(self):
        """Test creating a transaction with minimal required fields"""
        transaction = DLDTransaction(
            transaction_id="TEST_002",
            property_type="Villa",
            location="Palm Jumeirah",
            transaction_date=datetime.now(),
            price_aed=3500000.0,
            area_sqft=1500.0,
            developer_name="Nakheel",
            transaction_type="Sale",
            property_id="PALM_001"
        )

        assert transaction.transaction_id == "TEST_002"
        assert transaction.property_type == "Villa"
        assert transaction.location == "Palm Jumeirah"
        assert transaction.price_aed == 3500000.0
        assert transaction.area_sqft == 1500.0
        assert transaction.developer_name == "Nakheel"
        assert transaction.unit_number is None
        assert transaction.bedrooms is None


class TestDLDDataIngestion:
    """Test DLD data ingestion functionality"""

    @pytest.fixture
    def mock_dld_data(self):
        """Mock DLD API response data"""
        return {
            "transactions": [
                {
                    "transaction_id": "DLD_001",
                    "property_type": "Apartment",
                    "location": "Dubai Marina",
                    "transaction_date": "2024-01-25T08:30:00Z",
                    "price_aed": 2500000.0,
                    "area_sqft": 1200.0,
                    "developer_name": "Emaar Properties",
                    "transaction_type": "Sale",
                    "property_id": "MARINA_001",
                    "unit_number": "A-1501",
                    "building_name": "Marina Heights",
                    "project_name": "Marina Heights",
                    "floor_number": 15,
                    "bedrooms": 2,
                    "bathrooms": 2,
                    "parking_spaces": 1,
                    "view": "Marina View"
                },
                {
                    "transaction_id": "DLD_002",
                    "property_type": "Villa",
                    "location": "Palm Jumeirah",
                    "transaction_date": "2024-01-25T09:15:00Z",
                    "price_aed": 3500000.0,
                    "area_sqft": 1500.0,
                    "developer_name": "Nakheel",
                    "transaction_type": "Sale",
                    "property_id": "PALM_001",
                    "unit_number": "V-2503",
                    "building_name": "Palm Vista",
                    "project_name": "Palm Vista",
                    "floor_number": 25,
                    "bedrooms": 3,
                    "bathrooms": 3,
                    "parking_spaces": 2,
                    "view": "Sea View"
                }
            ]
        }

    @pytest.fixture
    def ingestion(self):
        """Create DLD ingestion instance"""
        return DLDDataIngestion()

    def test_fetch_recent_transactions_success(self, ingestion, mock_dld_data):
        """Test successful fetching of recent transactions"""
        async def run():
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json.return_value = mock_dld_data
                mock_get.return_value.__aenter__.return_value = mock_response

                async with ingestion as ing:
                    transactions = await ing.fetch_recent_transactions(hours=4)

                    assert len(transactions) == 2
                    assert transactions[0].transaction_id == "DLD_001"
                    assert transactions[0].property_type == "Apartment"
                    assert transactions[0].location == "Dubai Marina"
                    assert transactions[0].price_aed == 2500000.0
                    assert transactions[0].area_sqft == 1200.0
                    assert transactions[0].developer_name == "Emaar Properties"
                    assert transactions[0].bedrooms == 2
                    assert transactions[0].bathrooms == 2
                    assert transactions[0].parking_spaces == 1
                    assert transactions[0].view == "Marina View"

                    assert transactions[1].transaction_id == "DLD_002"
                    assert transactions[1].property_type == "Villa"
                    assert transactions[1].location == "Palm Jumeirah"
                    assert transactions[1].price_aed == 3500000.0

        asyncio.run(run())

    def test_fetch_recent_transactions_api_error(self, ingestion):
        """Test handling of API errors"""
        async def run():
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 500
                mock_get.return_value.__aenter__.return_value = mock_response

                async with ingestion as ing:
                    transactions = await ing.fetch_recent_transactions(hours=4)
                    assert len(transactions) == 0

        asyncio.run(run())

    def test_fetch_recent_transactions_exception(self, ingestion):
        """Test handling of exceptions"""
        async def run():
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_get.side_effect = Exception("Network error")

                async with ingestion as ing:
                    transactions = await ing.fetch_recent_transactions(hours=4)
                    assert len(transactions) == 0

        asyncio.run(run())

    def test_fetch_transactions_by_date_range(self, ingestion, mock_dld_data):
        """Test fetching transactions by date range"""
        async def run():
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json.return_value = mock_dld_data
                mock_get.return_value.__aenter__.return_value = mock_response

                start_date = datetime.now() - timedelta(days=7)
                end_date = datetime.now()

                async with ingestion as ing:
                    transactions = await ing.fetch_transactions_by_date_range(
                        start_date, end_date, limit=1000
                    )

                    assert len(transactions) == 2
                    assert transactions[0].transaction_id == "DLD_001"
                    assert transactions[1].transaction_id == "DLD_002"

        asyncio.run(run())

    def test_stream_transactions_paginated(self, ingestion):
        """Test streaming transactions across multiple pages"""
        page1 = {
            "transactions": [
                {
                    "transaction_id": "DLD_001",
                    "property_type": "Apartment",
                    "location": "Dubai Marina",
                    "transaction_date": "2024-01-25T08:30:00",
                    "price_aed": 1000000,
                    "area_sqft": 900,
                    "developer_name": "Dev1",
                    "transaction_type": "Sale",
                    "property_id": "ID1",
                },
                {
                    "transaction_id": "DLD_002",
                    "property_type": "Villa",
                    "location": "Palm Jumeirah",
                    "transaction_date": "2024-01-26T08:30:00",
                    "price_aed": 2000000,
                    "area_sqft": 1500,
                    "developer_name": "Dev2",
                    "transaction_type": "Sale",
                    "property_id": "ID2",
                },
            ]
        }
        page2 = {
            "transactions": [
                {
                    "transaction_id": "DLD_003",
                    "property_type": "Apartment",
                    "location": "Downtown",
                    "transaction_date": "2024-01-27T08:30:00",
                    "price_aed": 1500000,
                    "area_sqft": 1100,
                    "developer_name": "Dev3",
                    "transaction_type": "Sale",
                    "property_id": "ID3",
                }
            ]
        }
        async def run():
            with patch('aiohttp.ClientSession.get') as mock_get:
                resp1 = AsyncMock()
                resp1.status = 200
                resp1.json.return_value = page1
                resp2 = AsyncMock()
                resp2.status = 200
                resp2.json.return_value = page2
                mock_get.side_effect = [
                    AsyncMock(__aenter__=AsyncMock(return_value=resp1), __aexit__=AsyncMock(return_value=None)),
                    AsyncMock(__aenter__=AsyncMock(return_value=resp2), __aexit__=AsyncMock(return_value=None)),
                ]

                start_date = datetime.now() - timedelta(days=7)
                end_date = datetime.now()
                async with ingestion as ing:
                    transactions = [
                        t async for t in ing.stream_transactions_paginated(
                            start_date, end_date, page_size=2
                        )
                    ]

                    assert len(transactions) == 3
                    assert transactions[0].transaction_id == "DLD_001"
                    assert transactions[2].transaction_id == "DLD_003"

        asyncio.run(run())

    def test_stream_transactions_csv(self, ingestion):
        """Test streaming of transactions from CSV without full download"""
        csv_content = (
            "transaction_id,property_type,location,transaction_date,price_aed,area_sqft,"
            "developer_name,transaction_type,property_id\n"
            "T1,Apartment,Dubai Marina,2024-01-01T00:00:00,1000000,900,Emaar,Sale,ID1\n"
            "T2,Villa,Palm Jumeirah,2024-01-02T00:00:00,2000000,1500,Nakheel,Sale,ID2\n"
        ).encode('utf-8')

        class MockContent:
            def __init__(self, data):
                self.data = data

            async def iter_chunked(self, size):
                for i in range(0, len(self.data), size):
                    yield self.data[i:i + size]

        async def run():
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.content = MockContent(csv_content)
                mock_get.return_value.__aenter__.return_value = mock_response

                async with ingestion as ing:
                    transactions = [
                        t async for t in ing.stream_transactions_csv('http://example.com/transactions.csv')
                    ]

                    assert len(transactions) == 2
                    assert transactions[0].transaction_id == "T1"
                    assert transactions[1].transaction_id == "T2"

        asyncio.run(run())

    def test_validate_transaction_valid(self, ingestion):
        """Test validation of valid transaction"""
        transaction = DLDTransaction(
            transaction_id="TEST_001",
            property_type="Apartment",
            location="Dubai Marina",
            transaction_date=datetime.now(),
            price_aed=2500000.0,
            area_sqft=1200.0,
            developer_name="Emaar Properties",
            transaction_type="Sale",
            property_id="MARINA_001"
        )

        assert ingestion.validate_transaction(transaction) is True

    def test_validate_transaction_invalid_missing_id(self, ingestion):
        """Test validation of transaction with missing ID"""
        transaction = DLDTransaction(
            transaction_id="",
            property_type="Apartment",
            location="Dubai Marina",
            transaction_date=datetime.now(),
            price_aed=2500000.0,
            area_sqft=1200.0,
            developer_name="Emaar Properties",
            transaction_type="Sale",
            property_id="MARINA_001"
        )

        assert ingestion.validate_transaction(transaction) is False

    def test_validate_transaction_invalid_price(self, ingestion):
        """Test validation of transaction with invalid price"""
        transaction = DLDTransaction(
            transaction_id="TEST_001",
            property_type="Apartment",
            location="Dubai Marina",
            transaction_date=datetime.now(),
            price_aed=0.0,  # Invalid price
            area_sqft=1200.0,
            developer_name="Emaar Properties",
            transaction_type="Sale",
            property_id="MARINA_001"
        )

        assert ingestion.validate_transaction(transaction) is False

    def test_validate_transaction_invalid_area(self, ingestion):
        """Test validation of transaction with invalid area"""
        transaction = DLDTransaction(
            transaction_id="TEST_001",
            property_type="Apartment",
            location="Dubai Marina",
            transaction_date=datetime.now(),
            price_aed=2500000.0,
            area_sqft=0.0,  # Invalid area
            developer_name="Emaar Properties",
            transaction_type="Sale",
            property_id="MARINA_001"
        )

        assert ingestion.validate_transaction(transaction) is False

    def test_validate_transaction_future_date(self, ingestion):
        """Test validation of transaction with future date"""
        transaction = DLDTransaction(
            transaction_id="TEST_001",
            property_type="Apartment",
            location="Dubai Marina",
            transaction_date=datetime.now() + timedelta(days=1),  # Future date
            price_aed=2500000.0,
            area_sqft=1200.0,
            developer_name="Emaar Properties",
            transaction_type="Sale",
            property_id="MARINA_001"
        )

        assert ingestion.validate_transaction(transaction) is False

    def test_validate_transaction_price_out_of_range(self, ingestion):
        """Test validation of transaction with price out of range"""
        transaction = DLDTransaction(
            transaction_id="TEST_001",
            property_type="Apartment",
            location="Dubai Marina",
            transaction_date=datetime.now(),
            price_aed=50000.0,  # Too low
            area_sqft=1200.0,
            developer_name="Emaar Properties",
            transaction_type="Sale",
            property_id="MARINA_001"
        )

        assert ingestion.validate_transaction(transaction) is False

    def test_calculate_data_quality_excellent(self, ingestion):
        """Test data quality calculation with excellent quality"""
        transactions = [
            DLDTransaction(
                transaction_id=f"TEST_{i}",
                property_type="Apartment",
                location="Dubai Marina",
                transaction_date=datetime.now(),
                price_aed=2500000.0,
                area_sqft=1200.0,
                developer_name="Emaar Properties",
                transaction_type="Sale",
                property_id=f"MARINA_{i}"
            )
            for i in range(100)  # 100 valid transactions
        ]

        quality_report = ingestion.calculate_data_quality(transactions)

        assert quality_report.total_records == 100
        assert quality_report.valid_records == 100
        assert quality_report.quality_score == 100.0
        assert quality_report.quality_level == DataQualityLevel.EXCELLENT
        assert quality_report.processing_time_seconds > 0
        assert len(quality_report.errors) == 0

    def test_calculate_data_quality_good(self, ingestion):
        """Test data quality calculation with good quality"""
        transactions = []

        # Add 90 valid transactions
        for i in range(90):
            transactions.append(DLDTransaction(
                transaction_id=f"TEST_{i}",
                property_type="Apartment",
                location="Dubai Marina",
                transaction_date=datetime.now(),
                price_aed=2500000.0,
                area_sqft=1200.0,
                developer_name="Emaar Properties",
                transaction_type="Sale",
                property_id=f"MARINA_{i}"
            ))

        # Add 10 invalid transactions
        for i in range(10):
            transactions.append(DLDTransaction(
                transaction_id="",  # Invalid
                property_type="Apartment",
                location="Dubai Marina",
                transaction_date=datetime.now(),
                price_aed=2500000.0,
                area_sqft=1200.0,
                developer_name="Emaar Properties",
                transaction_type="Sale",
                property_id=f"MARINA_{i}"
            ))

        quality_report = ingestion.calculate_data_quality(transactions)

        assert quality_report.total_records == 100
        assert quality_report.valid_records == 90
        assert quality_report.quality_score == 90.0
        assert quality_report.quality_level == DataQualityLevel.GOOD
        assert len(quality_report.errors) == 10

    def test_calculate_data_quality_poor(self, ingestion):
        """Test data quality calculation with poor quality"""
        transactions = []

        # Add 30 valid transactions
        for i in range(30):
            transactions.append(DLDTransaction(
                transaction_id=f"TEST_{i}",
                property_type="Apartment",
                location="Dubai Marina",
                transaction_date=datetime.now(),
                price_aed=2500000.0,
                area_sqft=1200.0,
                developer_name="Emaar Properties",
                transaction_type="Sale",
                property_id=f"MARINA_{i}"
            ))

        # Add 70 invalid transactions
        for i in range(70):
            transactions.append(DLDTransaction(
                transaction_id="",  # Invalid
                property_type="Apartment",
                location="Dubai Marina",
                transaction_date=datetime.now(),
                price_aed=2500000.0,
                area_sqft=1200.0,
                developer_name="Emaar Properties",
                transaction_type="Sale",
                property_id=f"MARINA_{i}"
            ))

        quality_report = ingestion.calculate_data_quality(transactions)

        assert quality_report.total_records == 100
        assert quality_report.valid_records == 30
        assert quality_report.quality_score == 30.0
        assert quality_report.quality_level == DataQualityLevel.POOR
        assert len(quality_report.errors) == 70

    def test_get_ingestion_status(self, ingestion):
        """Test getting ingestion status"""
        async def run():
            status = await ingestion.get_ingestion_status()

            assert "status" in status
            assert "timestamp" in status
            assert "api_connected" in status
            assert "data_source" in status
            assert status["data_source"] == DLDDataSource.OFFICIAL_API.value

        asyncio.run(run())

    def test_process_and_store_transactions(self, ingestion):
        """Test processing and storing transactions"""
        transactions = [
            DLDTransaction(
                transaction_id="TEST_001",
                property_type="Apartment",
                location="Dubai Marina",
                transaction_date=datetime.now(),
                price_aed=2500000.0,
                area_sqft=1200.0,
                developer_name="Emaar Properties",
                transaction_type="Sale",
                property_id="MARINA_001"
            ),
            DLDTransaction(
                transaction_id="TEST_002",
                property_type="Villa",
                location="Palm Jumeirah",
                transaction_date=datetime.now(),
                price_aed=3500000.0,
                area_sqft=1500.0,
                developer_name="Nakheel",
                transaction_type="Sale",
                property_id="PALM_001"
            )
        ]

        async def run():
            result = await ingestion.process_and_store_transactions(transactions)

            assert result["status"] == "success"
            assert result["total_processed"] == 2
            assert result["valid_stored"] == 2
            assert "quality_report" in result
            assert result["quality_report"]["quality_score"] == 100.0
            assert result["quality_report"]["quality_level"] == "excellent"
            assert "timestamp" in result

        asyncio.run(run())


class TestDataQualityLevel:
    """Test data quality level enum"""

    def test_quality_levels(self):
        """Test all quality levels"""
        assert DataQualityLevel.EXCELLENT.value == "excellent"
        assert DataQualityLevel.GOOD.value == "good"
        assert DataQualityLevel.FAIR.value == "fair"
        assert DataQualityLevel.POOR.value == "poor"


class TestDLDDataSource:
    """Test DLD data source enum"""

    def test_data_sources(self):
        """Test all data sources"""
        assert DLDDataSource.OFFICIAL_API.value == "official_api"
        assert DLDDataSource.CSV_IMPORT.value == "csv_import"
        assert DLDDataSource.WEB_SCRAPING.value == "web_scraping"
        assert DLDDataSource.THIRD_PARTY.value == "third_party"

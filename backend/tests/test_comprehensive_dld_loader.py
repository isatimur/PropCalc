"""
Comprehensive tests for the DLD loader
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from io import StringIO

from src.propcalc.core.comprehensive_dld_loader import (
    ComprehensiveDLDLoader,
    ProcessingResult,
    DataQualityMetrics,
    DLD_URLS
)


class TestComprehensiveDLDLoader:
    """Test comprehensive DLD loader functionality"""
    
    @pytest.fixture
    def loader(self):
        """Create a loader instance for testing"""
        return ComprehensiveDLDLoader(batch_size=100, max_retries=2)
    
    @pytest.fixture
    def sample_csv_data(self):
        """Sample CSV data for testing"""
        return """area_id,area_name_en,area_name_ar,emirate,sector
1,Dubai Marina,دبي مارينا,Dubai,Marina
2,Palm Jumeirah,جزيرة النخلة,Dubai,Beach
3,Business Bay,خليج الأعمال,Dubai,Business"""
    
    @pytest.fixture
    def sample_transaction_data(self):
        """Sample transaction data for testing"""
        return """transaction_id,transaction_date,price_aed,area_sqft,area_id,property_type,developer_name,project_name,transaction_type
TXN001,2024-01-15,1500000,1200,1,Apartment,Emaar,Dubai Marina Views,Sale
TXN002,2024-01-16,2500000,1800,2,Villa,Nakheel,Palm Jumeirah Villas,Sale
TXN003,2024-01-17,800000,800,3,Studio,Meraas,Business Bay Lofts,Sale"""
    
    @pytest.mark.asyncio
    async def test_loader_initialization(self, loader):
        """Test loader initialization"""
        assert loader.batch_size == 100
        assert loader.max_retries == 2
        assert loader.lookup_tables == {}
        assert loader.log_id is None
        assert loader.session is None
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self, loader):
        """Test async context manager functionality"""
        async with loader as ctx_loader:
            assert ctx_loader.session is not None
            assert ctx_loader.session.headers['User-Agent'] == 'PropCalc/2.0.0'
        
        # Session should be closed after context exit
        assert loader.session is None
    
    def test_parse_areas_csv(self, loader, sample_csv_data):
        """Test areas CSV parsing"""
        areas = loader._parse_areas_csv(sample_csv_data)
        
        assert len(areas) == 3
        assert areas[0]['area_id'] == '1'
        assert areas[0]['area_name_en'] == 'Dubai Marina'
        assert areas[0]['area_name_ar'] == 'دبي مارينا'
        assert areas[0]['emirate'] == 'Dubai'
        assert areas[0]['sector'] == 'Marina'
    
    def test_parse_transaction_groups_csv(self, loader):
        """Test transaction groups CSV parsing"""
        csv_data = """group_id,group_name_en,group_name_ar,category
1,Residential Sales,المبيعات السكنية,Residential
2,Commercial Leases,الإيجارات التجارية,Commercial"""
        
        groups = loader._parse_transaction_groups_csv(csv_data)
        
        assert len(groups) == 2
        assert groups[0]['group_id'] == '1'
        assert groups[0]['group_name_en'] == 'Residential Sales'
        assert groups[0]['group_name_ar'] == 'المبيعات السكنية'
        assert groups[0]['category'] == 'Residential'
    
    def test_parse_transaction_procedures_csv(self, loader):
        """Test transaction procedures CSV parsing"""
        csv_data = """procedure_id,procedure_name_en,procedure_name_ar,type
1,Property Sale,بيع العقار,Sale
2,Property Lease,إيجار العقار,Lease"""
        
        procedures = loader._parse_transaction_procedures_csv(csv_data)
        
        assert len(procedures) == 2
        assert procedures[0]['procedure_id'] == '1'
        assert procedures[0]['procedure_name_en'] == 'Property Sale'
        assert procedures[0]['procedure_name_ar'] == 'بيع العقار'
        assert procedures[0]['type'] == 'Sale'
    
    def test_parse_market_types_csv(self, loader):
        """Test market types CSV parsing"""
        csv_data = """market_type_id,market_type_en,market_type_ar,description
1,Primary Market,السوق الأولية,New properties
2,Secondary Market,السوق الثانوية,Resale properties"""
        
        types = loader._parse_market_types_csv(csv_data)
        
        assert len(types) == 2
        assert types[0]['market_type_id'] == '1'
        assert types[0]['market_type_en'] == 'Primary Market'
        assert types[0]['market_type_ar'] == 'السوق الأولية'
        assert types[0]['description'] == 'New properties'
    
    def test_parse_residential_index_csv(self, loader):
        """Test residential index CSV parsing"""
        csv_data = """year,month,quarter,index_value,change_percentage
2024,1,1,150.5,2.5
2024,2,1,152.1,1.1
2024,3,1,153.8,1.1"""
        
        indices = loader._parse_residential_index_csv(csv_data)
        
        assert len(indices) == 3
        assert indices[0]['year'] == 2024
        assert indices[0]['month'] == 1
        assert indices[0]['quarter'] == 1
        assert indices[0]['index_value'] == 150.5
        assert indices[0]['change_percentage'] == 2.5
    
    def test_parse_real_transaction(self, loader):
        """Test real transaction parsing"""
        # Set up lookup tables
        loader.lookup_tables['areas'] = {
            '1': {'area_id': '1', 'area_name_en': 'Dubai Marina'}
        }
        
        row = {
            'transaction_id': 'TXN001',
            'transaction_date': '2024-01-15',
            'price_aed': '1500000',
            'area_sqft': '1200',
            'area_id': '1',
            'property_type': 'Apartment',
            'developer_name': 'Emaar',
            'project_name': 'Dubai Marina Views',
            'transaction_type': 'Sale'
        }
        
        transaction = loader._parse_real_transaction(row)
        
        assert transaction is not None
        assert transaction['transaction_id'] == 'TXN001'
        assert transaction['price_aed'] == 1500000.0
        assert transaction['area_sqft'] == 1200.0
        assert transaction['area_name'] == 'Dubai Marina'
        assert transaction['property_type'] == 'Apartment'
        assert transaction['property_usage'] == 'Residential'
        assert transaction['data_source'] == 'DUBAI_PULSE_REAL_1.3M'
    
    def test_parse_real_transaction_invalid_data(self, loader):
        """Test transaction parsing with invalid data"""
        # Test with missing transaction_id
        row = {
            'transaction_date': '2024-01-15',
            'price_aed': '1500000'
        }
        
        transaction = loader._parse_real_transaction(row)
        assert transaction is None
        
        # Test with invalid date
        row = {
            'transaction_id': 'TXN001',
            'transaction_date': 'invalid-date',
            'price_aed': '1500000'
        }
        
        transaction = loader._parse_real_transaction(row)
        assert transaction is None
    
    def test_parse_date(self, loader):
        """Test date parsing with multiple formats"""
        # Test ISO format
        date = loader._parse_date('2024-01-15')
        assert date == datetime(2024, 1, 15)
        
        # Test DD/MM/YYYY format
        date = loader._parse_date('15/01/2024')
        assert date == datetime(2024, 1, 15)
        
        # Test MM/DD/YYYY format
        date = loader._parse_date('01/15/2024')
        assert date == datetime(2024, 1, 15)
        
        # Test invalid date
        date = loader._parse_date('invalid-date')
        assert date is None
        
        # Test empty string
        date = loader._parse_date('')
        assert date is None
    
    def test_parse_number(self, loader):
        """Test number parsing with cleaning"""
        # Test clean number
        assert loader._parse_number('1500000') == 1500000.0
        
        # Test number with commas
        assert loader._parse_number('1,500,000') == 1500000.0
        
        # Test number with currency symbol
        assert loader._parse_number('AED 1,500,000') == 1500000.0
        
        # Test decimal number
        assert loader._parse_number('1500.50') == 1500.5
        
        # Test empty string
        assert loader._parse_number('') == 0.0
        
        # Test invalid string
        assert loader._parse_number('invalid') == 0.0
    
    def test_parse_rooms(self, loader):
        """Test rooms parsing with pattern matching"""
        # Test simple number
        assert loader._parse_rooms('2') == 2
        
        # Test with BR suffix
        assert loader._parse_rooms('2BR') == 2
        
        # Test with Bedrooms suffix
        assert loader._parse_rooms('3 Bedrooms') == 3
        
        # Test with Bed suffix
        assert loader._parse_rooms('4 Bed') == 4
        
        # Test empty string
        assert loader._parse_rooms('') is None
        
        # Test invalid string
        assert loader._parse_rooms('invalid') is None
    
    def test_get_property_usage(self, loader):
        """Test property usage determination"""
        assert loader._get_property_usage('Apartment') == 'Residential'
        assert loader._get_property_usage('Villa') == 'Residential'
        assert loader._get_property_usage('Office') == 'Commercial'
        assert loader._get_property_usage('Retail Shop') == 'Retail'
        assert loader._get_property_usage('Warehouse') == 'Industrial'
        assert loader._get_property_usage('') == 'Unknown'
        assert loader._get_property_usage('Mixed Use Building') == 'Mixed'
    
    def test_get_area_name(self, loader):
        """Test area name lookup"""
        # Set up lookup table
        loader.lookup_tables['areas'] = {
            '1': {'area_id': '1', 'area_name_en': 'Dubai Marina'},
            '2': {'area_id': '2', 'area_name_ar': 'جزيرة النخلة'}
        }
        
        # Test existing area
        assert loader._get_area_name('1') == 'Dubai Marina'
        
        # Test non-existing area
        assert loader._get_area_name('999') is None
        
        # Test empty area_id
        assert loader._get_area_name('') is None
    
    @pytest.mark.asyncio
    async def test_load_single_lookup_table_success(self, loader):
        """Test successful lookup table loading"""
        # Create a proper mock response class
        class MockResponse:
            def __init__(self, status, text_content):
                self.status = status
                self._text_content = text_content
            
            async def __aenter__(self):
                return self
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
            
            async def text(self):
                return self._text_content
        
        mock_response = MockResponse(200, "id,name\n1,Test")
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        loader.session = mock_session
        
        # Mock parser and inserter functions
        def mock_parser(csv_content):
            return [{'id': '1', 'name': 'Test'}]
        
        async def mock_inserter(data):
            return len(data)
        
        result = await loader._load_single_lookup_table(
            'test_table', 'http://test.com', mock_parser, mock_inserter
        )
        
        assert result.success is True
        assert result.records_processed == 1
        assert result.records_inserted == 1
        assert result.records_failed == 0
    
    @pytest.mark.asyncio
    async def test_load_single_lookup_table_http_error(self, loader):
        """Test lookup table loading with HTTP error"""
        # Create a proper mock response class
        class MockResponse:
            def __init__(self, status, text_content):
                self.status = status
                self._text_content = text_content
            
            async def __aenter__(self):
                return self
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
            
            async def text(self):
                return self._text_content
        
        mock_response = MockResponse(404, "")
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        loader.session = mock_session
        
        def mock_parser(csv_content):
            return []
        
        async def mock_inserter(data):
            return 0
        
        result = await loader._load_single_lookup_table(
            'test_table', 'http://test.com', mock_parser, mock_inserter
        )
        
        assert result.success is False
        assert result.error_message == "Failed after 2 attempts"
    
    @pytest.mark.asyncio
    async def test_load_single_lookup_table_exception(self, loader):
        """Test lookup table loading with exception"""
        # Mock session that raises exception
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(side_effect=Exception("Network error"))
        loader.session = mock_session
        
        def mock_parser(csv_content):
            return []
        
        async def mock_inserter(data):
            return 0
        
        result = await loader._load_single_lookup_table(
            'test_table', 'http://test.com', mock_parser, mock_inserter
        )
        
        assert result.success is False
        assert result.error_message == "Failed after 2 attempts"
    
    @pytest.mark.asyncio
    async def test_insert_areas_lookup(self, loader):
        """Test areas lookup insertion"""
        areas_data = [
            {
                'area_id': '1',
                'area_name_en': 'Dubai Marina',
                'area_name_ar': 'دبي مارينا',
                'emirate': 'Dubai',
                'sector': 'Marina'
            }
        ]
        
        # Mock database connection
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.executemany = AsyncMock()
        
        with patch('src.propcalc.core.comprehensive_dld_loader.get_db_connection', return_value=mock_conn):
            result = await loader._insert_areas_lookup(areas_data)
            
            assert result == 1
            mock_conn.execute.assert_called_once()
            mock_conn.executemany.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_insert_transactions_batch(self, loader):
        """Test transactions batch insertion"""
        batch_data = [
            {
                'transaction_id': 'TXN001',
                'transaction_date': datetime(2024, 1, 15),
                'price_aed': 1500000.0,
                'area_sqft': 1200.0,
                'area_name': 'Dubai Marina',
                'property_type': 'Apartment',
                'property_usage': 'Residential',
                'rooms': 2,
                'developer_name': 'Emaar',
                'project_name': 'Dubai Marina Views',
                'transaction_type': 'Sale',
                'data_source': 'DUBAI_PULSE_REAL_1.3M',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        ]
        
        # Mock database connection
        mock_conn = AsyncMock()
        mock_conn.executemany = AsyncMock()
        
        with patch('src.propcalc.core.comprehensive_dld_loader.get_db_connection', return_value=mock_conn):
            result = await loader._insert_transactions_batch(batch_data)
            
            assert result == 1
            mock_conn.executemany.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_verify_comprehensive_data(self, loader):
        """Test comprehensive data verification"""
        # Mock database connection and results
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value={
            'total_transactions': 1000,
            'unique_transactions': 1000,
            'earliest_date': datetime(2020, 1, 1),
            'latest_date': datetime(2024, 1, 1),
            'average_price_aed': 1500000.0,
            'total_volume_aed': 1500000000.0,
            'unique_locations': 50,
            'unique_developers': 25
        })
        mock_conn.fetchval = AsyncMock(side_effect=[50, 10, 20, 5, 100])
        
        with patch('src.propcalc.core.comprehensive_dld_loader.get_db_connection', return_value=mock_conn):
            result = await loader._verify_comprehensive_data()
            
            assert result['total_transactions'] == 1000
            assert result['unique_transactions'] == 1000
            assert result['average_price_aed'] == 1500000.0
            assert result['lookup_tables']['areas'] == 50
            assert result['lookup_tables']['transaction_groups'] == 10
            assert result['lookup_tables']['transaction_procedures'] == 20
            assert result['lookup_tables']['market_types'] == 5
            assert result['lookup_tables']['residential_index'] == 100


class TestProcessingResult:
    """Test ProcessingResult dataclass"""
    
    def test_processing_result_creation(self):
        """Test ProcessingResult creation"""
        result = ProcessingResult(
            success=True,
            records_processed=100,
            records_inserted=95,
            records_failed=5,
            processing_time_seconds=30.5
        )
        
        assert result.success is True
        assert result.records_processed == 100
        assert result.records_inserted == 95
        assert result.records_failed == 5
        assert result.processing_time_seconds == 30.5
        assert result.error_message is None
        assert result.details is None
    
    def test_processing_result_with_error(self):
        """Test ProcessingResult with error"""
        result = ProcessingResult(
            success=False,
            records_processed=0,
            records_inserted=0,
            records_failed=0,
            processing_time_seconds=0.1,
            error_message="Database connection failed"
        )
        
        assert result.success is False
        assert result.error_message == "Database connection failed"


class TestDataQualityMetrics:
    """Test DataQualityMetrics dataclass"""
    
    def test_data_quality_metrics_creation(self):
        """Test DataQualityMetrics creation"""
        metrics = DataQualityMetrics(
            total_records=1000,
            valid_records=950,
            invalid_records=50,
            quality_score=0.95,
            validation_errors=["Invalid date format", "Missing required field"]
        )
        
        assert metrics.total_records == 1000
        assert metrics.valid_records == 950
        assert metrics.invalid_records == 50
        assert metrics.quality_score == 0.95
        assert len(metrics.validation_errors) == 2


class TestDLDURLs:
    """Test DLD URLs configuration"""
    
    def test_dld_urls_configuration(self):
        """Test DLD URLs are properly configured"""
        assert 'transactions' in DLD_URLS
        assert 'transaction_groups' in DLD_URLS
        assert 'transaction_procedures' in DLD_URLS
        assert 'areas' in DLD_URLS
        assert 'market_types' in DLD_URLS
        assert 'residential_index' in DLD_URLS
        
        # Check URLs are valid
        for key, url in DLD_URLS.items():
            assert url.startswith('https://')
            assert 'dubaipulse.gov.ae' in url
            assert url.endswith('.csv')


if __name__ == '__main__':
    pytest.main([__file__])

#!/usr/bin/env python3
"""
Comprehensive Test Suite for DLD Ingestion Module
=================================================

This test suite covers all aspects of the DLD ingestion system including:
- Configuration management
- Database operations
- Data processing
- Error handling
- Performance validation
- Property type mapping
- Health monitoring

Author: PropCalc Team
Date: 2025-08-03
"""

import os

# Import the modules to test
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pandas as pd
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from propcalc.core.dld_ingestion import (
    DLDIngestion,
    DLDIngestionConfig,
    DLDIngestionError,
)


class TestDLDIngestionConfig:
    """Test configuration management."""

    def test_config_initialization(self):
        """Test configuration initialization with default values."""
        config_dict = {
            'database': {
                'host': 'test-host',
                'port': 5432,
                'user': 'test-user',
                'password': 'test-password',
                'database': 'test-db'
            },
            'chunk_size': 500,
            'retry_attempts': 5,
            'timeout': 60
        }

        config = DLDIngestionConfig(config_dict)

        assert config.database['host'] == 'test-host'
        assert config.chunk_size == 500
        assert config.retry_attempts == 5
        assert config.timeout == 60
        assert 'areas' in config.dld_sources
        assert 'transactions' in config.dld_sources

    def test_config_defaults(self):
        """Test configuration with minimal input."""
        config = DLDIngestionConfig({})

        assert config.chunk_size == 1000
        assert config.retry_attempts == 3
        assert config.timeout == 30
        assert len(config.dld_sources) == 5

    def test_dld_sources_structure(self):
        """Test DLD sources configuration structure."""
        config = DLDIngestionConfig({})

        for _source_name, source_config in config.dld_sources.items():
            assert 'url' in source_config
            assert 'filename' in source_config
            assert 'table' in source_config
            assert 'primary_key' in source_config
            assert 'required_columns' in source_config
            assert isinstance(source_config['required_columns'], list)


class TestDLDIngestion:
    """Test the main DLD ingestion class."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        return DLDIngestionConfig({
            'database': {
                'host': 'localhost',
                'port': 5432,
                'user': 'test_user',
                'password': 'test_password',
                'database': 'test_db'
            },
            'chunk_size': 100,
            'retry_attempts': 2,
            'timeout': 10
        })

    @pytest.fixture
    def ingestion(self, mock_config):
        """Create a DLD ingestion instance for testing."""
        return DLDIngestion(mock_config)

    def test_initialization(self, ingestion):
        """Test DLD ingestion initialization."""
        assert ingestion.config is not None
        assert ingestion.db_pool is None
        assert ingestion.session is None
        assert ingestion.ingestion_stats == {}
        assert 'current_status' in ingestion.health_status
        assert ingestion.health_status['current_status'] == 'idle'
        assert len(ingestion.property_type_mapping) > 0

    def test_property_type_mapping(self, ingestion):
        """Test property type mapping functionality."""
        # Test valid mappings
        assert ingestion.map_property_type('Unit') == 'Apartment'
        assert ingestion.map_property_type('Land') == 'Villa'
        assert ingestion.map_property_type('Building') == 'Office'
        assert ingestion.map_property_type('Apartment') == 'Apartment'
        assert ingestion.map_property_type('Villa') == 'Villa'

        # Test unknown types (should default to Apartment)
        assert ingestion.map_property_type('Unknown') == 'Apartment'
        assert ingestion.map_property_type('') == 'Apartment'
        assert ingestion.map_property_type(None) == 'Apartment'
        assert ingestion.map_property_type(pd.NA) == 'Apartment'

    def test_validate_csv_structure_valid(self, ingestion):
        """Test CSV structure validation with valid file."""
        # Create a temporary CSV file with valid structure
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("area_id,name_en,name_ar,municipality_number\n")
            f.write("1,Dubai Marina,دبي مارينا,001\n")
            f.write("2,Palm Jumeirah,جميرا النخيل,002\n")
            temp_file = Path(f.name)

        try:
            required_columns = ['area_id', 'name_en', 'name_ar', 'municipality_number']
            result = ingestion.validate_csv_structure(temp_file, required_columns)
            assert result is True
        finally:
            temp_file.unlink()

    def test_validate_csv_structure_invalid(self, ingestion):
        """Test CSV structure validation with invalid file."""
        # Create a temporary CSV file with missing columns
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("area_id,name_en\n")  # Missing required columns
            f.write("1,Dubai Marina\n")
            temp_file = Path(f.name)

        try:
            required_columns = ['area_id', 'name_en', 'name_ar', 'municipality_number']
            result = ingestion.validate_csv_structure(temp_file, required_columns)
            assert result is False
        finally:
            temp_file.unlink()

    def test_calculate_file_checksum(self, ingestion):
        """Test file checksum calculation."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content for checksum calculation")
            temp_file = Path(f.name)

        try:
            checksum = ingestion.calculate_file_checksum(temp_file)
            assert len(checksum) == 64  # SHA256 produces 64 character hex string
            assert checksum.isalnum()  # Should be alphanumeric
        finally:
            temp_file.unlink()

    @pytest.mark.asyncio
    async def test_initialize_database_success(self, ingestion):
        """Test successful database initialization."""
        with patch('asyncpg.create_pool', new_callable=AsyncMock) as mock_pool:
            mock_pool.return_value = Mock()

            result = await ingestion.initialize_database()

            assert result is True
            assert ingestion.db_pool is not None
            mock_pool.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_database_failure(self, ingestion):
        """Test database initialization failure."""
        with patch('asyncpg.create_pool', new_callable=AsyncMock) as mock_pool:
            mock_pool.side_effect = Exception("Connection failed")

            with pytest.raises(DLDIngestionError, match="Database initialization failed"):
                await ingestion.initialize_database()

    @pytest.mark.asyncio
    async def test_initialize_http_session_success(self, ingestion):
        """Test successful HTTP session initialization."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value = Mock()

            result = await ingestion.initialize_http_session()

            assert result is True
            assert ingestion.session is not None
            mock_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_http_session_failure(self, ingestion):
        """Test HTTP session initialization failure."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.side_effect = Exception("Session creation failed")

            with pytest.raises(DLDIngestionError, match="HTTP session initialization failed"):
                await ingestion.initialize_http_session()

    def test_get_health_status(self, ingestion):
        """Test health status retrieval."""
        health_status = ingestion.get_health_status()

        assert isinstance(health_status, dict)
        assert 'current_status' in health_status
        assert 'last_run' in health_status
        assert 'total_runs' in health_status
        assert 'successful_runs' in health_status
        assert 'failed_runs' in health_status

        # Should return a copy, not the original
        assert health_status is not ingestion.health_status


class TestDLDIngestionIntegration:
    """Integration tests for DLD ingestion."""

    @pytest.fixture
    def sample_areas_csv(self):
        """Create a sample areas CSV file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("area_id,name_en,name_ar,municipality_number\n")
            f.write("1,Dubai Marina,دبي مارينا,001\n")
            f.write("2,Palm Jumeirah,جميرا النخيل,002\n")
            f.write("3,Downtown Dubai,وسط مدينة دبي,003\n")
            temp_file = Path(f.name)

        yield temp_file
        temp_file.unlink()

    @pytest.fixture
    def sample_transactions_csv(self):
        """Create a sample transactions CSV file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("transaction_id,instance_date,property_type_en,area_name_en,actual_worth,procedure_area,area_id,procedure_id,master_project_en,project_name_en\n")
            f.write("T001,01/01/2024,Unit,Dubai Marina,1000000,1000,1,1,Marina Project,Marina Tower A\n")
            f.write("T002,02/01/2024,Land,Palm Jumeirah,2000000,2000,2,2,Palm Project,Palm Villa 1\n")
            temp_file = Path(f.name)

        yield temp_file
        temp_file.unlink()

    @pytest.mark.asyncio
    async def test_process_areas_data_integration(self, mock_config, sample_areas_csv):
        """Test areas data processing integration."""
        ingestion = DLDIngestion(mock_config)

        # Mock database pool
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.execute.return_value = "INSERT 0 1"
        ingestion.db_pool = mock_pool

        # Process areas data
        stats = await ingestion.process_areas_data(sample_areas_csv)

        assert stats['processed'] == 3
        assert stats['inserted'] == 3
        assert stats['updated'] == 0
        assert stats['errors'] == 0

        # Verify database calls
        assert mock_conn.execute.call_count == 3

    @pytest.mark.asyncio
    async def test_process_transactions_data_integration(self, mock_config, sample_transactions_csv):
        """Test transactions data processing integration."""
        ingestion = DLDIngestion(mock_config)

        # Mock database pool
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.execute.return_value = "INSERT 0 1"
        ingestion.db_pool = mock_pool

        # Process transactions data
        stats = await ingestion.process_transactions_data(sample_transactions_csv)

        assert stats['processed'] == 2
        assert stats['inserted'] == 2
        assert stats['updated'] == 0
        assert stats['errors'] == 0

        # Verify database calls
        assert mock_conn.execute.call_count == 2


class TestDLDIngestionErrorHandling:
    """Test error handling scenarios."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        return DLDIngestionConfig({
            'database': {
                'host': 'localhost',
                'port': 5432,
                'user': 'test_user',
                'password': 'test_password',
                'database': 'test_db'
            }
        })

    def test_dld_ingestion_error_inheritance(self):
        """Test that DLDIngestionError inherits from Exception."""
        error = DLDIngestionError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    @pytest.mark.asyncio
    async def test_process_areas_data_invalid_csv(self, mock_config):
        """Test areas processing with invalid CSV."""
        ingestion = DLDIngestion(mock_config)

        # Create invalid CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("invalid_column,another_column\n")
            f.write("1,test\n")
            temp_file = Path(f.name)

        try:
            with pytest.raises(DLDIngestionError, match="Invalid CSV structure"):
                await ingestion.process_areas_data(temp_file)
        finally:
            temp_file.unlink()

    @pytest.mark.asyncio
    async def test_process_transactions_data_invalid_csv(self, mock_config):
        """Test transactions processing with invalid CSV."""
        ingestion = DLDIngestion(mock_config)

        # Create invalid CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("invalid_column,another_column\n")
            f.write("1,test\n")
            temp_file = Path(f.name)

        try:
            with pytest.raises(DLDIngestionError, match="Invalid CSV structure"):
                await ingestion.process_transactions_data(temp_file)
        finally:
            temp_file.unlink()


class TestDLDIngestionPerformance:
    """Test performance characteristics."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        return DLDIngestionConfig({
            'database': {
                'host': 'localhost',
                'port': 5432,
                'user': 'test_user',
                'password': 'test_password',
                'database': 'test_db'
            },
            'chunk_size': 100
        })

    def test_property_type_mapping_performance(self, mock_config):
        """Test property type mapping performance."""
        ingestion = DLDIngestion(mock_config)

        import time
        start_time = time.time()

        # Test mapping performance with many iterations
        for _i in range(10000):
            ingestion.map_property_type('Unit')
            ingestion.map_property_type('Land')
            ingestion.map_property_type('Building')

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time (less than 1 second)
        assert duration < 1.0

    @pytest.mark.asyncio
    async def test_large_file_processing_performance(self, mock_config):
        """Test large file processing performance."""
        ingestion = DLDIngestion(mock_config)

        # Create a large CSV file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("transaction_id,instance_date,property_type_en,area_name_en,actual_worth,procedure_area,area_id,procedure_id,master_project_en,project_name_en\n")

            # Generate 1000 test records
            for i in range(1000):
                f.write(f"T{i:03d},01/01/2024,Unit,Dubai Marina,{1000000 + i},{1000 + i},1,1,Project {i},Tower {i}\n")

            temp_file = Path(f.name)

        try:
            # Mock database pool for performance testing
            mock_pool = AsyncMock()
            mock_conn = AsyncMock()
            mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
            mock_conn.execute.return_value = "INSERT 0 1"
            ingestion.db_pool = mock_pool

            import time
            start_time = time.time()

            # Process the large file
            stats = await ingestion.process_transactions_data(temp_file)

            end_time = time.time()
            duration = end_time - start_time

            # Verify processing completed
            assert stats['processed'] == 1000
            assert stats['errors'] == 0

            # Should process at least 100 records per second
            records_per_second = stats['processed'] / duration
            assert records_per_second > 100

        finally:
            temp_file.unlink()


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])

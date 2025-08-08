"""Test suite for PropCalc backend."""

__version__ = "1.0.0"

# Ignore integration tests that rely on unavailable services and heavy dependencies
collect_ignore = [
    "test_api.py",
    "test_main.py",
    "test_dld_ingestion.py",
    "test_dld_integration.py",
    "performance",
]



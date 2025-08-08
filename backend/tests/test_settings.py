import os
import sys

import pytest

pytest.importorskip("pydantic")

# Ensure the src package is discoverable when running tests without installation
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from propcalc.config.settings import Settings  # noqa: E402


def test_environment_normalization():
    settings = Settings(environment="DeVeLoPmEnT")
    assert settings.environment == "development"


def test_log_level_normalization():
    settings = Settings(log_level="warning")
    assert settings.log_level == "WARNING"


def test_invalid_environment_raises():
    with pytest.raises(ValueError):
        Settings(environment="invalid")

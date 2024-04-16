import pytest
from pydantic import ValidationError

from src.conf.config import Settings


def test_valid_algorithm():
    valid_algorithm = "HS256"
    config = Settings(ALGORITHM=valid_algorithm)
    assert config.ALGORITHM == valid_algorithm


def test_invalid_algorithm():
    invalid_algorithm = "invalid_algorithm"
    with pytest.raises(ValidationError) as exc_info:
        Settings(ALGORITHM=invalid_algorithm)

    assert "Algorithm must be either HS256 or HS512" in str(exc_info.value)

"""Tests for configuration module."""

import os
from unittest.mock import patch

import pytest
from pydantic_core import ValidationError

from config import Settings, get_settings


class TestSettings:
    """Test Settings class."""

    def test_settings_with_all_required_fields(self):
        """Test settings initialization with required fields."""
        with patch.dict(
            os.environ,
            {"MONGODB_URI": "mongodb://localhost:27017", "OPENAI_API_KEY": "sk-test-key"},
            clear=True
        ):
            settings = Settings()
            assert settings.mongodb_uri == "mongodb://localhost:27017"
            assert settings.openai_api_key == "sk-test-key"
            assert settings.mongodb_database == "vector_rag"  # default

    def test_settings_missing_required_fields(self):
        """Test settings fail when required fields missing."""
        # Clear any cached settings and force fresh import
        import sys
        if 'config' in sys.modules:
            del sys.modules['config']
        
        # Ensure TESTING is set and clear all other env vars
        with patch.dict(os.environ, {"TESTING": "1"}, clear=True):
            # Import after environment is set
            from config import Settings
            with pytest.raises(ValidationError):  # Pydantic validation error
                Settings()

    def test_settings_with_custom_values(self):
        """Test settings with custom configuration values."""
        with patch.dict(
            os.environ,
            {
                "MONGODB_URI": "mongodb://custom:27017",
                "MONGODB_DATABASE": "custom_db",
                "OPENAI_API_KEY": "sk-custom-key",
                "EMBEDDING_MODEL": "text-embedding-ada-003",
                "EMBEDDING_DIMENSIONS": "2048",
                "MAX_CHUNK_SIZE": "2000",
                "CHUNK_OVERLAP": "300",
                "DEFAULT_SIMILARITY_THRESHOLD": "0.8",
                "DEFAULT_SEARCH_LIMIT": "10",
            },
            clear=True
        ):
            settings = Settings()
            assert settings.mongodb_uri == "mongodb://custom:27017"
            assert settings.mongodb_database == "custom_db"
            assert settings.openai_api_key == "sk-custom-key"
            assert settings.embedding_model == "text-embedding-ada-003"
            assert settings.embedding_dimensions == 2048
            assert settings.max_chunk_size == 2000
            assert settings.chunk_overlap == 300
            assert settings.default_similarity_threshold == 0.8
            assert settings.default_search_limit == 10

    def test_optional_fields_defaults(self):
        """Test optional fields have correct defaults."""
        with patch.dict(
            os.environ,
            {
                "MONGODB_URI": "mongodb://localhost:27017", 
                "OPENAI_API_KEY": "sk-test-key",
                # Explicitly unset this to test default
                "UNSTRUCTURED_API_KEY": ""
            },
            clear=True
        ):
            settings = Settings()
            # Check that empty string is treated as None
            assert settings.unstructured_api_key == "" or settings.unstructured_api_key is None
            assert settings.unstructured_api_url == "https://api.unstructured.io"
            assert settings.embedding_model == "text-embedding-ada-002"
            assert settings.embedding_dimensions == 1536
            assert settings.default_collection == "documents"
            assert settings.max_chunk_size == 1000
            assert settings.chunk_overlap == 200
            assert settings.default_similarity_threshold == 0.7
            assert settings.default_search_limit == 5
            assert settings.log_level == "INFO"


class TestGetSettings:
    """Test get_settings function."""

    def test_get_settings_returns_singleton(self):
        """Test that get_settings returns the same instance."""
        with patch.dict(
            os.environ,
            {"MONGODB_URI": "mongodb://localhost:27017", "OPENAI_API_KEY": "sk-test-key"},
            clear=True
        ):
            # Clear any cached settings first
            if hasattr(get_settings, "cache_clear"):
                get_settings.cache_clear()
            settings1 = get_settings()
            settings2 = get_settings()
            assert settings1 is settings2

    def test_get_settings_type(self):
        """Test get_settings returns Settings instance."""
        with patch.dict(
            os.environ, 
            {"MONGODB_URI": "mongodb://localhost:27017", "OPENAI_API_KEY": "sk-test-key"},
            clear=True
        ):
            if hasattr(get_settings, "cache_clear"):
                get_settings.cache_clear()
            settings = get_settings()
            assert isinstance(settings, Settings)


if __name__ == "__main__":
    pytest.main([__file__])

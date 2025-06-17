"""Configuration management for MongoDB MCP Server."""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # MongoDB Configuration
    mongodb_uri: str = Field(description="MongoDB connection string")
    mongodb_database: str = Field(default="vector_rag", description="MongoDB database name")

    # OpenAI Configuration
    openai_api_key: str = Field(description="OpenAI API key")

    # Unstructured.io Configuration
    unstructured_api_key: Optional[str] = Field(default=None, description="Unstructured.io API key")
    unstructured_api_url: str = Field(
        default="https://api.unstructured.io", description="Unstructured.io API URL"
    )

    # Embedding Configuration
    embedding_model: str = Field(
        default="text-embedding-ada-002", description="OpenAI embedding model"
    )
    embedding_dimensions: int = Field(default=1536, description="Embedding vector dimensions")

    # Collection Configuration
    default_collection: str = Field(
        default="documents", description="Default MongoDB collection name"
    )
    max_chunk_size: int = Field(default=1000, description="Maximum size of document chunks")
    chunk_overlap: int = Field(default=200, description="Overlap between chunks")

    # Search Configuration
    default_similarity_threshold: float = Field(
        default=0.7, description="Default similarity threshold for search"
    )
    default_search_limit: int = Field(default=5, description="Default number of search results")

    # Server Configuration
    log_level: str = Field(default="INFO", description="Logging level")

    class Config:
        # Don't read from .env file when TESTING environment variable is set
        env_file = None if os.environ.get("TESTING") else ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # Allow lowercase field names to match uppercase env vars
        extra = "ignore"  # Ignore extra fields instead of forbidding them


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get settings instance (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

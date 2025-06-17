"""Pytest configuration and shared fixtures."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import pytest


@pytest.fixture(autouse=True)
def isolate_env():
    """Isolate test environment from real .env files."""
    # Save original environment
    original_env = os.environ.copy()
    
    # Set TESTING flag to prevent .env file reading
    os.environ['TESTING'] = '1'
    
    # Clear environment variables that might affect tests
    test_env_vars = [
        'MONGODB_URI', 'OPENAI_API_KEY', 'MONGODB_DATABASE',
        'EMBEDDING_MODEL', 'EMBEDDING_DIMENSIONS', 'UNSTRUCTURED_API_KEY',
        'MAX_CHUNK_SIZE', 'CHUNK_OVERLAP', 'DEFAULT_SIMILARITY_THRESHOLD',
        'DEFAULT_SEARCH_LIMIT', 'LOG_LEVEL'
    ]
    
    for var in test_env_vars:
        os.environ.pop(var, None)
    
    # Clear any cached settings
    import config
    config._settings = None
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
    
    # Clear cached settings again
    config._settings = None


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_pdf_path(temp_dir):
    """Create a sample PDF file for testing."""
    pdf_path = temp_dir / "sample.pdf"
    # Create a minimal PDF-like file (not a real PDF, but enough for testing)
    pdf_path.write_bytes(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n")
    return pdf_path


@pytest.fixture
def sample_text_path(temp_dir):
    """Create a sample text file for testing."""
    text_path = temp_dir / "sample.txt"
    text_path.write_text(
        "This is a sample document.\nIt has multiple lines.\nFor testing purposes."
    )
    return text_path


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("config.get_settings") as mock_get_settings:
        mock_settings = Mock()
        mock_settings.mongodb_uri = "mongodb://test:27017"
        mock_settings.mongodb_database = "test_db"
        mock_settings.openai_api_key = "sk-test-key"
        mock_settings.embedding_model = "text-embedding-ada-002"
        mock_settings.embedding_dimensions = 1536
        mock_settings.default_collection = "documents"
        mock_settings.max_chunk_size = 1000
        mock_settings.chunk_overlap = 200
        mock_settings.default_similarity_threshold = 0.7
        mock_settings.default_search_limit = 5
        mock_settings.unstructured_api_key = None
        mock_settings.unstructured_api_url = "https://api.unstructured.io"
        mock_get_settings.return_value = mock_settings
        yield mock_settings


@pytest.fixture
def mock_mongodb_client():
    """Mock MongoDB client."""
    with patch("services.mongodb_client.MongoClient") as mock_client:
        mock_instance = Mock()
        mock_database = Mock()
        mock_collection = Mock()

        # Setup mock hierarchy
        mock_instance.__getitem__.return_value = mock_database
        mock_database.__getitem__.return_value = mock_collection
        mock_database.list_collection_names.return_value = ["documents", "test_collection"]
        mock_database.command.return_value = {"size": 1024, "storageSize": 2048, "avgObjSize": 512}

        # Mock collection operations
        mock_collection.insert_many.return_value.inserted_ids = ["id1", "id2", "id3"]
        mock_collection.count_documents.return_value = 10
        mock_collection.aggregate.return_value = [
            {
                "content": "Sample content 1",
                "metadata": {"source": "test.pdf", "page": 1},
                "similarity_score": 0.95,
            },
            {
                "content": "Sample content 2",
                "metadata": {"source": "test.pdf", "page": 2},
                "similarity_score": 0.87,
            },
        ]

        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    with patch("services.embeddings.AsyncOpenAI") as mock_client:
        mock_instance = Mock()

        # Mock embeddings response
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3]), Mock(embedding=[0.4, 0.5, 0.6])]
        mock_instance.embeddings.create.return_value = mock_response

        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_unstructured():
    """Mock unstructured library functions."""
    with patch("services.unstructured_client.partition") as mock_partition, patch(
        "services.unstructured_client.chunk_by_title"
    ) as mock_chunk_title, patch("services.unstructured_client.chunk_elements") as mock_chunk_basic:

        # Mock document elements
        mock_element1 = Mock()
        mock_element1.__str__ = Mock(return_value="Title: Document Title")
        mock_element1.category = "Title"
        mock_element1.metadata = Mock()
        mock_element1.metadata.to_dict.return_value = {"page_number": 1}

        mock_element2 = Mock()
        mock_element2.__str__ = Mock(return_value="This is paragraph content.")
        mock_element2.category = "NarrativeText"
        mock_element2.metadata = Mock()
        mock_element2.metadata.to_dict.return_value = {"page_number": 1}

        mock_partition.return_value = [mock_element1, mock_element2]
        mock_chunk_title.return_value = [mock_element1, mock_element2]
        mock_chunk_basic.return_value = [mock_element1, mock_element2]

        yield {
            "partition": mock_partition,
            "chunk_by_title": mock_chunk_title,
            "chunk_elements": mock_chunk_basic,
        }


@pytest.fixture
def mock_requests():
    """Mock requests for URL downloads."""
    with patch("services.unstructured_client.requests") as mock_req:
        mock_response = Mock()
        mock_response.content = b"Sample PDF content"
        mock_response.raise_for_status.return_value = None
        mock_req.get.return_value = mock_response
        yield mock_req

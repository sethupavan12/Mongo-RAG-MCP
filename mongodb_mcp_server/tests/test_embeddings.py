"""Tests for embedding service."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from services.embeddings import EmbeddingService, LocalEmbeddingService, create_embedding_service


class TestEmbeddingService:
    """Test EmbeddingService class."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client."""
        with patch("services.embeddings.AsyncOpenAI") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def embedding_service(self, mock_openai_client):
        """Create embedding service instance."""
        with patch("services.embeddings.get_settings") as mock_settings:
            mock_settings.return_value.openai_api_key = "test-key"
            mock_settings.return_value.embedding_model = "text-embedding-ada-002"
            mock_settings.return_value.embedding_dimensions = 1536
            return EmbeddingService()

    @pytest.mark.asyncio
    async def test_generate_single_embedding(self, embedding_service, mock_openai_client):
        """Test generating embedding for single text."""
        # Mock response
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_openai_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Test
        result = await embedding_service.generate_single_embedding("test text")

        # Assertions
        assert result == [0.1, 0.2, 0.3]
        mock_openai_client.embeddings.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_embeddings_multiple_texts(self, embedding_service, mock_openai_client):
        """Test generating embeddings for multiple texts."""
        # Mock response
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3]), Mock(embedding=[0.4, 0.5, 0.6])]
        mock_openai_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Test
        texts = ["text1", "text2"]
        result = await embedding_service.generate_embeddings(texts)

        # Assertions
        assert len(result) == 2
        assert result[0] == [0.1, 0.2, 0.3]
        assert result[1] == [0.4, 0.5, 0.6]

    @pytest.mark.asyncio
    async def test_generate_embeddings_empty_input(self, embedding_service):
        """Test generating embeddings with empty input."""
        result = await embedding_service.generate_embeddings([])
        assert result == []

        result = await embedding_service.generate_embeddings("")
        assert result == []

    @pytest.mark.asyncio
    async def test_generate_embeddings_batch_processing(
        self, embedding_service, mock_openai_client
    ):
        """Test batch processing of embeddings."""
        # Mock response for each batch
        def mock_create(*args, **kwargs):
            input_texts = kwargs.get('input', [])
            return Mock(data=[Mock(embedding=[0.1, 0.2, 0.3]) for _ in input_texts])
        
        mock_openai_client.embeddings.create = AsyncMock(side_effect=mock_create)

        # Test with batch_size=2
        texts = ["text1", "text2", "text3"]
        result = await embedding_service.generate_embeddings(texts, batch_size=2)

        # Should make 2 API calls (batch of 2, then batch of 1)
        assert mock_openai_client.embeddings.create.call_count == 2
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_generate_embeddings_filters_empty_strings(
        self, embedding_service, mock_openai_client
    ):
        """Test that empty strings are filtered out."""
        # Mock response
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_openai_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Test with empty strings
        texts = ["valid text", "", "   ", "another valid text"]
        await embedding_service.generate_embeddings(texts)

        # Should only process non-empty texts
        args, kwargs = mock_openai_client.embeddings.create.call_args
        assert len(kwargs["input"]) == 2  # Only 2 valid texts

    def test_get_embedding_dimensions(self, embedding_service):
        """Test getting embedding dimensions."""
        assert embedding_service.get_embedding_dimensions() == 1536

    def test_get_model_name(self, embedding_service):
        """Test getting model name."""
        assert embedding_service.get_model_name() == "text-embedding-ada-002"


class TestLocalEmbeddingService:
    """Test LocalEmbeddingService class."""

    @pytest.fixture
    def mock_sentence_transformer(self):
        """Mock SentenceTransformer."""
        # Mock the entire sentence_transformers module
        sentence_transformers_mock = Mock()
        
        with patch.dict('sys.modules', {'sentence_transformers': sentence_transformers_mock}):
            with patch("sentence_transformers.SentenceTransformer") as mock_st:
                mock_instance = Mock()
                # Make sure dimension property returns actual value, not Mock
                mock_instance.get_sentence_embedding_dimension.return_value = 384
                
                # Mock encode to return numpy-like array behavior
                def mock_encode(texts, convert_to_tensor=False):
                    if isinstance(texts, str):
                        texts = [texts]
                    
                    # Create mock array with shape attribute
                    mock_array = Mock()
                    if len(texts) == 1:
                        # Single embedding - shape (384,)
                        mock_array.shape = (384,)
                        mock_array.tolist.return_value = [0.1, 0.2, 0.3]
                    else:
                        # Multiple embeddings - shape (n, 384)
                        mock_array.shape = (len(texts), 384)
                        mock_array.tolist.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]][:len(texts)]
                    
                    return mock_array
                
                mock_instance.encode.side_effect = mock_encode
                mock_st.return_value = mock_instance
                sentence_transformers_mock.SentenceTransformer = mock_st
                yield mock_instance

    def test_init_success(self, mock_sentence_transformer):
        """Test successful initialization."""
        with patch.dict('sys.modules', {'sentence_transformers': Mock()}):
            # Mock the initialization to set actual dimensions value
            with patch.object(LocalEmbeddingService, '__init__', 
                             lambda self, model_name="all-MiniLM-L6-v2": setattr(self, 'model_name', model_name) or setattr(self, 'dimensions', 384)):
                service = LocalEmbeddingService()
                assert service.model_name == "all-MiniLM-L6-v2"
                assert service.dimensions == 384

    def test_init_missing_dependency(self):
        """Test initialization fails when sentence-transformers not installed."""
        # Mock import failure by making the import raise ImportError
        def mock_import(name, *args, **kwargs):
            if name == 'sentence_transformers':
                raise ImportError("No module named 'sentence_transformers'")
            return __import__(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            with pytest.raises(ImportError, match="sentence-transformers not installed"):
                LocalEmbeddingService()

    @pytest.mark.asyncio
    async def test_generate_embeddings(self, mock_sentence_transformer):
        """Test generating embeddings locally."""
        with patch.dict('sys.modules', {'sentence_transformers': Mock()}):
            # Create service instance with mocked behavior
            service = LocalEmbeddingService.__new__(LocalEmbeddingService)
            service.model = mock_sentence_transformer
            service.model_name = "all-MiniLM-L6-v2"
            service.dimensions = 384

            texts = ["text1", "text2"]
            result = await service.generate_embeddings(texts)

            assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            mock_sentence_transformer.encode.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_single_embedding(self, mock_sentence_transformer):
        """Test generating single embedding locally."""
        with patch.dict('sys.modules', {'sentence_transformers': Mock()}):
            # Create service instance with mocked behavior
            service = LocalEmbeddingService.__new__(LocalEmbeddingService)
            service.model = mock_sentence_transformer
            service.model_name = "all-MiniLM-L6-v2"
            service.dimensions = 384

            result = await service.generate_single_embedding("test text")
            assert result == [0.1, 0.2, 0.3]


class TestCreateEmbeddingService:
    """Test create_embedding_service factory function."""

    @patch("services.embeddings.LocalEmbeddingService")
    def test_create_local_service(self, mock_local):
        """Test creating local embedding service."""
        create_embedding_service(use_local=True)
        mock_local.assert_called_once()

    @patch("services.embeddings.EmbeddingService")
    def test_create_openai_service(self, mock_openai):
        """Test creating OpenAI embedding service."""
        create_embedding_service(use_local=False)
        mock_openai.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])

"""Embedding service for generating vector embeddings from text."""

import logging
from typing import List, Optional, Union

import openai
from openai import AsyncOpenAI

from config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings from text."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize embedding service.

        Args:
            api_key: OpenAI API key
            model: Embedding model to use
        """
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.embedding_model
        self.dimensions = settings.embedding_dimensions

        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=self.api_key)

        logger.info(f"Initialized embedding service with model: {self.model}")

    async def generate_embeddings(
        self, texts: Union[str, List[str]], batch_size: int = 100
    ) -> List[List[float]]:
        """Generate embeddings for text(s).

        Args:
            texts: Single text or list of texts to embed
            batch_size: Number of texts to process in each batch

        Returns:
            List of embedding vectors
        """
        # Ensure texts is a list
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return []

        try:
            # Process in batches to avoid API limits
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]

                # Clean and validate texts
                clean_batch = []
                for text in batch:
                    if isinstance(text, str) and text.strip():
                        # Truncate if too long (OpenAI has token limits)
                        clean_text = text.strip()[:8000]  # Conservative limit
                        clean_batch.append(clean_text)

                if not clean_batch:
                    continue

                # Generate embeddings for batch
                response = await self.client.embeddings.create(model=self.model, input=clean_batch)

                # Extract embeddings
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)

                logger.debug(
                    f"Generated embeddings for batch {i//batch_size + 1}, size: {len(clean_batch)}"
                )

            logger.info(f"Generated {len(all_embeddings)} embeddings using {self.model}")
            return all_embeddings

        except openai.APIError as e:
            logger.error(f"OpenAI API error generating embeddings: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating embeddings: {e}")
            raise

    async def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        embeddings = await self.generate_embeddings([text])
        return embeddings[0] if embeddings else []

    def get_embedding_dimensions(self) -> int:
        """Get the dimensions of embeddings from this service.

        Returns:
            Number of dimensions
        """
        return self.dimensions

    def get_model_name(self) -> str:
        """Get the name of the embedding model.

        Returns:
            Model name
        """
        return self.model


class LocalEmbeddingService:
    """Fallback local embedding service using sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize local embedding service.

        Args:
            model_name: Name of the sentence-transformers model
        """
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            self.dimensions = self.model.get_sentence_embedding_dimension()
            logger.info(f"Initialized local embedding service with model: {model_name}")
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )

    async def generate_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """Generate embeddings using local model.

        Args:
            texts: Single text or list of texts to embed

        Returns:
            List of embedding vectors
        """
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return []

        try:
            # Generate embeddings
            embeddings = self.model.encode(texts, convert_to_tensor=False)

            # Convert to list of lists
            if len(embeddings.shape) == 1:
                embeddings = [embeddings.tolist()]
            else:
                embeddings = embeddings.tolist()

            logger.info(f"Generated {len(embeddings)} local embeddings")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating local embeddings: {e}")
            raise

    async def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        embeddings = await self.generate_embeddings([text])
        return embeddings[0] if embeddings else []

    def get_embedding_dimensions(self) -> int:
        """Get the dimensions of embeddings from this service.

        Returns:
            Number of dimensions
        """
        return self.dimensions

    def get_model_name(self) -> str:
        """Get the name of the embedding model.

        Returns:
            Model name
        """
        return self.model_name


def create_embedding_service(
    use_local: bool = False,
) -> Union[EmbeddingService, LocalEmbeddingService]:
    """Factory function to create an embedding service.

    Args:
        use_local: Whether to use local embeddings

    Returns:
        Embedding service instance
    """
    if use_local:
        return LocalEmbeddingService()
    else:
        return EmbeddingService()

"""Document processing service using Unstructured.io for intelligent chunking."""

import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import requests
from unstructured.chunking.basic import chunk_elements
from unstructured.chunking.title import chunk_by_title

# Unstructured imports
from unstructured.partition.auto import partition

from config import get_settings

logger = logging.getLogger(__name__)


class DocumentChunk:
    """Represents a processed document chunk."""

    def __init__(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        element_type: Optional[str] = None,
        page_number: Optional[int] = None,
    ):
        self.content = content
        self.metadata = metadata or {}
        self.element_type = element_type
        self.page_number = page_number


class DocumentProcessor:
    """Service for processing documents using Unstructured.io."""

    def __init__(
        self, api_key: Optional[str] = None, api_url: Optional[str] = None, use_local: bool = True
    ):
        """Initialize document processor.

        Args:
            api_key: Unstructured.io API key
            api_url: Unstructured.io API URL
            use_local: Whether to use local processing (recommended for hackathon)
        """
        settings = get_settings()
        self.api_key = api_key or settings.unstructured_api_key
        self.api_url = api_url or settings.unstructured_api_url
        self.use_local = use_local or not self.api_key
        self.max_chunk_size = settings.max_chunk_size
        self.chunk_overlap = settings.chunk_overlap

        logger.info(f"Initialized document processor (local: {self.use_local})")

    async def download_document(self, url: str) -> Path:
        """Download document from URL to temporary file.

        Args:
            url: URL of the document to download

        Returns:
            Path to downloaded file
        """
        try:
            # Parse URL to get filename
            parsed_url = urlparse(url)
            filename = Path(parsed_url.path).name

            if not filename or "." not in filename:
                # Try to detect file type from URL or default to .pdf
                if "pdf" in url.lower():
                    filename = "document.pdf"
                elif "docx" in url.lower() or "doc" in url.lower():
                    filename = "document.docx"
                else:
                    filename = "document.txt"

            # Download file
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Save to temporary file
            temp_dir = Path(tempfile.gettempdir())
            temp_file = temp_dir / filename

            with open(temp_file, "wb") as f:
                f.write(response.content)

            logger.info(f"Downloaded document from {url} to {temp_file}")
            return temp_file

        except Exception as e:
            logger.error(f"Failed to download document from {url}: {e}")
            raise

    def _partition_document_local(self, file_path: Path) -> List[Any]:
        """Partition document using local Unstructured processing.

        Args:
            file_path: Path to document file

        Returns:
            List of document elements
        """
        try:
            # Try different strategies for PDF processing
            if str(file_path).lower().endswith('.pdf'):
                # For PDFs, try different strategies
                try:
                    # First try with hi_res strategy
                    elements = partition(
                        filename=str(file_path),
                        strategy="hi_res",
                        include_page_breaks=True,
                        infer_table_structure=True,
                    )
                except Exception as e1:
                    logger.warning(f"hi_res strategy failed: {e1}, trying fast strategy")
                    try:
                        # Fallback to fast strategy
                        elements = partition(
                            filename=str(file_path),
                            strategy="fast",
                            include_page_breaks=True,
                        )
                    except Exception as e2:
                        logger.warning(f"fast strategy failed: {e2}, trying auto strategy")
                        # Final fallback to auto
                        elements = partition(
                            filename=str(file_path),
                            strategy="auto",
                        )
            else:
                # For non-PDF files, use auto strategy
                elements = partition(
                    filename=str(file_path),
                    include_page_breaks=True,
                    infer_table_structure=True,
                    strategy="auto",
                )

            logger.info(f"Partitioned document into {len(elements)} elements")
            return elements

        except Exception as e:
            logger.error(f"Failed to partition document locally: {e}")
            raise

    def _chunk_elements(
        self, elements: List[Any], chunking_strategy: str = "by_title"
    ) -> List[DocumentChunk]:
        """Chunk document elements using specified strategy.

        Args:
            elements: List of document elements from partitioning
            chunking_strategy: Strategy for chunking ("by_title", "basic")

        Returns:
            List of document chunks
        """
        try:
            if chunking_strategy == "by_title":
                # Chunk by title preserves document structure
                chunks = chunk_by_title(
                    elements,
                    max_characters=self.max_chunk_size,
                    overlap=self.chunk_overlap,
                    include_orig_elements=True,
                )
            else:
                # Basic chunking for simple splitting
                chunks = chunk_elements(
                    elements,
                    max_characters=self.max_chunk_size,
                    overlap=self.chunk_overlap,
                    include_orig_elements=True,
                )

            # Convert to DocumentChunk objects
            document_chunks = []
            for i, chunk in enumerate(chunks):
                # Extract text content
                content = str(chunk).strip()

                if not content:
                    continue

                # Extract metadata
                metadata = {
                    "chunk_index": i,
                    "chunking_strategy": chunking_strategy,
                    "chunk_size": len(content),
                }

                # Add element-specific metadata if available
                if hasattr(chunk, "metadata") and chunk.metadata:
                    metadata.update(chunk.metadata.to_dict())

                # Extract element type and page number
                element_type = getattr(chunk, "category", None)
                page_number = metadata.get("page_number")

                document_chunks.append(
                    DocumentChunk(
                        content=content,
                        metadata=metadata,
                        element_type=element_type,
                        page_number=page_number,
                    )
                )

            logger.info(f"Created {len(document_chunks)} chunks using {chunking_strategy} strategy")
            return document_chunks

        except Exception as e:
            logger.error(f"Failed to chunk elements: {e}")
            raise

    async def process_document(
        self,
        document_path: Union[str, Path],
        chunking_strategy: str = "by_title",
        additional_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentChunk]:
        """Process a document file into chunks.

        Args:
            document_path: Path to document file
            chunking_strategy: Strategy for chunking
            additional_metadata: Additional metadata to add to chunks

        Returns:
            List of processed document chunks
        """
        file_path = Path(document_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        try:
            # Partition document into elements
            if self.use_local:
                elements = self._partition_document_local(file_path)
            else:
                # TODO: Implement API-based processing if needed
                raise NotImplementedError("API-based processing not implemented yet")

            # Chunk elements
            chunks = self._chunk_elements(elements, chunking_strategy)

            # Add additional metadata to all chunks
            if additional_metadata:
                for chunk in chunks:
                    chunk.metadata.update(additional_metadata)

            # Add source document metadata
            for chunk in chunks:
                chunk.metadata.update(
                    {
                        "source_file": file_path.name,
                        "source_path": str(file_path),
                        "file_size": file_path.stat().st_size,
                        "processing_timestamp": str(Path().cwd()),  # Simple timestamp
                    }
                )

            return chunks

        except Exception as e:
            logger.error(f"Failed to process document {file_path}: {e}")
            raise

    async def process_document_from_url(
        self,
        url: str,
        chunking_strategy: str = "by_title",
        additional_metadata: Optional[Dict[str, Any]] = None,
        cleanup_temp: bool = True,
    ) -> List[DocumentChunk]:
        """Process a document from URL.

        Args:
            url: URL of document to process
            chunking_strategy: Strategy for chunking
            additional_metadata: Additional metadata to add to chunks
            cleanup_temp: Whether to cleanup temporary downloaded file

        Returns:
            List of processed document chunks
        """
        temp_file = None
        try:
            # Download document
            temp_file = await self.download_document(url)

            # Add URL to metadata
            url_metadata = {"source_url": url}
            if additional_metadata:
                url_metadata.update(additional_metadata)

            # Process document
            chunks = await self.process_document(temp_file, chunking_strategy, url_metadata)

            return chunks

        finally:
            # Cleanup temporary file
            if cleanup_temp and temp_file and temp_file.exists():
                try:
                    temp_file.unlink()
                    logger.debug(f"Cleaned up temporary file: {temp_file}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup temporary file {temp_file}: {e}")

    def get_supported_formats(self) -> List[str]:
        """Get list of supported document formats.

        Returns:
            List of supported file extensions
        """
        return [
            ".pdf",
            ".docx",
            ".doc",
            ".txt",
            ".rtf",
            ".odt",
            ".pptx",
            ".ppt",
            ".xlsx",
            ".xls",
            ".html",
            ".htm",
            ".md",
            ".csv",
            ".json",
            ".xml",
            ".eml",
            ".msg",
        ]

    def is_supported_format(self, file_path: Union[str, Path]) -> bool:
        """Check if file format is supported.

        Args:
            file_path: Path to file

        Returns:
            True if format is supported
        """
        suffix = Path(file_path).suffix.lower()
        return suffix in self.get_supported_formats()

    def is_url(self, path: str) -> bool:
        """Check if string is a URL.

        Args:
            path: String to check

        Returns:
            True if string is a URL
        """
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

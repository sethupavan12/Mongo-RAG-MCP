"""Document ingestion MCP tool for processing and storing documents."""

import logging
from typing import Any, Dict, List, Optional

from mcp.server.models import Tool
from mcp.types import TextContent

from config import get_settings
from services.embeddings import EmbeddingService
from services.mongodb_client import DocumentChunk, MongoDBVectorStore
from services.unstructured_client import DocumentProcessor

logger = logging.getLogger(__name__)


class DocumentIngestionTool:
    """MCP tool for document ingestion and storage."""

    def __init__(self):
        """Initialize the document ingestion tool."""
        self.mongodb_store = MongoDBVectorStore()
        self.embedding_service = EmbeddingService()
        self.document_processor = DocumentProcessor()
        self.settings = get_settings()

    def get_tool_definition(self) -> Tool:
        """Get the MCP tool definition."""
        return Tool(
            name="ingest_document",
            description="Process and ingest a document into MongoDB vector collection for RAG applications",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_url": {
                        "type": "string",
                        "description": "URL or local path to document (PDF, DOCX, TXT, etc.)",
                    },
                    "collection_name": {
                        "type": "string",
                        "description": "MongoDB collection name to store the document",
                        "default": "documents",
                    },
                    "chunking_strategy": {
                        "type": "string",
                        "description": "Document chunking strategy",
                        "enum": ["by_title", "basic"],
                        "default": "by_title",
                    },
                    "metadata_fields": {
                        "type": "object",
                        "description": "Additional metadata to store with document chunks",
                        "default": {},
                    },
                    "max_chunk_size": {
                        "type": "integer",
                        "description": "Maximum size of document chunks in characters",
                        "default": 1000,
                    },
                    "chunk_overlap": {
                        "type": "integer",
                        "description": "Overlap between chunks in characters",
                        "default": 200,
                    },
                },
                "required": ["document_url"],
            },
        )

    async def execute(
        self,
        document_url: str,
        collection_name: str = "documents",
        chunking_strategy: str = "by_title",
        metadata_fields: Optional[Dict[str, Any]] = None,
        max_chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> List[TextContent]:
        """Execute document ingestion.

        Args:
            document_url: URL or path to document
            collection_name: MongoDB collection name
            chunking_strategy: How to chunk the document
            metadata_fields: Additional metadata
            max_chunk_size: Maximum chunk size
            chunk_overlap: Overlap between chunks

        Returns:
            List of text content with results
        """
        try:
            logger.info(f"Starting document ingestion: {document_url}")

            # Validate inputs
            if not document_url.strip():
                raise ValueError("Document URL cannot be empty")

            # Update processor settings if provided
            if max_chunk_size != self.settings.max_chunk_size:
                self.document_processor.max_chunk_size = max_chunk_size
            if chunk_overlap != self.settings.chunk_overlap:
                self.document_processor.chunk_overlap = chunk_overlap

            # Process document
            if self.document_processor.is_url(document_url):
                chunks = await self.document_processor.process_document_from_url(
                    document_url,
                    chunking_strategy=chunking_strategy,
                    additional_metadata=metadata_fields,
                )
            else:
                chunks = await self.document_processor.process_document(
                    document_url,
                    chunking_strategy=chunking_strategy,
                    additional_metadata=metadata_fields,
                )

            if not chunks:
                return [
                    TextContent(
                        type="text",
                        text="❌ No content extracted from document. Please check the document format and content.",
                    )
                ]

            logger.info(f"Extracted {len(chunks)} chunks from document")

            # Generate embeddings for chunks
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = await self.embedding_service.generate_embeddings(chunk_texts)

            if len(embeddings) != len(chunks):
                raise ValueError(f"Embedding count mismatch: {len(embeddings)} vs {len(chunks)}")

            # Create DocumentChunk objects with embeddings
            document_chunks = []
            for chunk, embedding in zip(chunks, embeddings):
                document_chunk = DocumentChunk(
                    content=chunk.content,
                    embedding=embedding,
                    metadata=chunk.metadata,
                    chunk_id=None,
                )
                document_chunks.append(document_chunk)

            # Store in MongoDB
            source_metadata = {
                "document_url": document_url,
                "chunking_strategy": chunking_strategy,
                "embedding_model": self.embedding_service.get_model_name(),
                "total_chunks": len(document_chunks),
            }
            if metadata_fields:
                source_metadata.update(metadata_fields)

            storage_result = await self.mongodb_store.store_embeddings(
                document_chunks, collection_name, source_metadata
            )

            # Format response
            if storage_result["success"]:
                response_text = f"""✅ **Document Ingestion Successful**

📄 **Document**: {document_url}
📊 **Collection**: {collection_name}
🔢 **Chunks Created**: {storage_result['chunks_stored']}
⚙️ **Chunking Strategy**: {chunking_strategy}
🤖 **Embedding Model**: {self.embedding_service.get_model_name()}
📏 **Chunk Size**: {max_chunk_size} chars (overlap: {chunk_overlap})

**Processing Summary**:
- Extracted {len(chunks)} text elements
- Generated {len(embeddings)} embeddings
- Stored {storage_result['chunks_stored']} chunks successfully

The document is now ready for vector search queries in the '{collection_name}' collection.
"""
            else:
                response_text = f"""❌ **Document Ingestion Failed**

📄 **Document**: {document_url}
📊 **Collection**: {collection_name}
🔢 **Chunks Processed**: {len(chunks)}

**Error**: {storage_result.get('error', 'Unknown storage error')}

Please check your MongoDB connection and try again.
"""

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            logger.error(f"Document ingestion failed: {e}")
            error_text = f"""❌ **Document Ingestion Error**

📄 **Document**: {document_url}
🚫 **Error**: {str(e)}

**Troubleshooting**:
- Check if the document URL is accessible
- Verify the document format is supported
- Ensure MongoDB connection is working
- Check your OpenAI API key for embeddings
"""
            return [TextContent(type="text", text=error_text)]


# Global tool instance
document_ingestion_tool = DocumentIngestionTool()


# MCP tool function
async def ingest_document(
    document_url: str,
    collection_name: str = "documents",
    chunking_strategy: str = "by_title",
    metadata_fields: Optional[Dict[str, Any]] = None,
    max_chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[TextContent]:
    """Process and ingest a document into MongoDB vector collection.

    This tool downloads and processes documents (PDF, DOCX, TXT, etc.),
    chunks them intelligently using Unstructured.io, generates embeddings,
    and stores them in MongoDB for vector search.

    Args:
        document_url: URL or local path to document
        collection_name: MongoDB collection name (default: "documents")
        chunking_strategy: "by_title" or "basic" chunking (default: "by_title")
        metadata_fields: Additional metadata to store (optional)
        max_chunk_size: Maximum chunk size in characters (default: 1000)
        chunk_overlap: Overlap between chunks in characters (default: 200)

    Returns:
        Processing results with chunk count and storage status
    """
    return await document_ingestion_tool.execute(
        document_url=document_url,
        collection_name=collection_name,
        chunking_strategy=chunking_strategy,
        metadata_fields=metadata_fields,
        max_chunk_size=max_chunk_size,
        chunk_overlap=chunk_overlap,
    )

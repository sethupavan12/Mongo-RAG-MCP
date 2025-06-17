"""Vector search MCP tool for retrieving relevant document chunks."""

import logging
from typing import Any, Dict, List, Optional

from mcp.server.models import Tool
from mcp.types import TextContent

from config import get_settings
from services.embeddings import EmbeddingService
from services.mongodb_client import MongoDBVectorStore

logger = logging.getLogger(__name__)


class VectorSearchTool:
    """MCP tool for vector similarity search."""

    def __init__(self):
        """Initialize the vector search tool."""
        self.mongodb_store = MongoDBVectorStore()
        self.embedding_service = EmbeddingService()
        self.settings = get_settings()

    def get_tool_definition(self) -> Tool:
        """Get the MCP tool definition."""
        return Tool(
            name="search_documents",
            description="Search for relevant document chunks using vector similarity in MongoDB",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query text to find relevant document chunks",
                    },
                    "collection_name": {
                        "type": "string",
                        "description": "MongoDB collection name to search in",
                        "default": "documents",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 50,
                    },
                    "similarity_threshold": {
                        "type": "number",
                        "description": "Minimum similarity score (0.0 to 1.0)",
                        "default": 0.7,
                        "minimum": 0.0,
                        "maximum": 1.0,
                    },
                    "metadata_filter": {
                        "type": "object",
                        "description": "Additional filters for document metadata (optional)",
                        "default": {},
                    },
                    "include_similarity_scores": {
                        "type": "boolean",
                        "description": "Whether to include similarity scores in results",
                        "default": True,
                    },
                },
                "required": ["query"],
            },
        )

    async def execute(
        self,
        query: str,
        collection_name: str = "documents",
        limit: int = 5,
        similarity_threshold: float = 0.7,
        metadata_filter: Optional[Dict[str, Any]] = None,
        include_similarity_scores: bool = True,
    ) -> List[TextContent]:
        """Execute vector search.

        Args:
            query: Search query text
            collection_name: MongoDB collection name
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            metadata_filter: Additional metadata filters
            include_similarity_scores: Whether to include scores

        Returns:
            List of text content with search results
        """
        try:
            logger.info(f"Starting vector search: '{query}' in collection '{collection_name}'")

            # Validate inputs
            if not query.strip():
                raise ValueError("Search query cannot be empty")

            if limit <= 0:
                raise ValueError("Limit must be greater than 0")

            if not (0.0 <= similarity_threshold <= 1.0):
                raise ValueError("Similarity threshold must be between 0.0 and 1.0")

            # Generate embedding for query
            query_embedding = await self.embedding_service.generate_single_embedding(query.strip())

            if not query_embedding:
                raise ValueError("Failed to generate embedding for query")

            logger.debug(f"Generated query embedding with {len(query_embedding)} dimensions")

            # Perform vector search
            search_results = await self.mongodb_store.vector_search(
                query_embedding=query_embedding,
                collection_name=collection_name,
                limit=limit,
                similarity_threshold=similarity_threshold,
                metadata_filter=metadata_filter,
            )

            # Format results
            if not search_results:
                response_text = f"""🔍 **Vector Search Results**

**Query**: "{query}"
**Collection**: {collection_name}
**Results**: No relevant documents found

**Search Parameters**:
- Similarity threshold: {similarity_threshold}
- Maximum results: {limit}

Try:
- Lowering the similarity threshold
- Using different keywords
- Checking if documents are properly indexed
"""
                return [TextContent(type="text", text=response_text)]

            # Build formatted response
            response_parts = [
                "🔍 **Vector Search Results**\n",
                f'**Query**: "{query}"',
                f"**Collection**: {collection_name}",
                f"**Found**: {len(search_results)} relevant documents\n",
            ]

            # Add each result
            for i, result in enumerate(search_results, 1):
                content = result.get("content", "").strip()
                metadata = result.get("metadata", {})
                similarity_score = result.get("similarity_score", 0.0)

                # Truncate content if too long
                if len(content) > 500:
                    content = content[:500] + "..."

                result_section = [
                    f"## 📄 Result {i}",
                ]

                if include_similarity_scores:
                    result_section.append(f"**Similarity**: {similarity_score:.3f}")

                # Add source information if available
                source_info = []
                if metadata.get("source_file"):
                    source_info.append(f"File: {metadata['source_file']}")
                if metadata.get("source_url"):
                    source_info.append(f"URL: {metadata['source_url']}")
                if metadata.get("page_number"):
                    source_info.append(f"Page: {metadata['page_number']}")
                if metadata.get("chunk_index") is not None:
                    source_info.append(f"Chunk: {metadata['chunk_index']}")

                if source_info:
                    result_section.append(f"**Source**: {' | '.join(source_info)}")

                result_section.extend(["**Content**:", content, ""])  # Empty line for spacing

                response_parts.extend(result_section)

            # Add search summary
            response_parts.extend(
                [
                    "---",
                    "**Search Summary**:",
                    f"- Embedding model: {self.embedding_service.get_model_name()}",
                    f"- Similarity threshold: {similarity_threshold}",
                    f"- Total results: {len(search_results)}/{limit}",
                ]
            )

            if metadata_filter:
                response_parts.append(f"- Metadata filters applied: {len(metadata_filter)} filters")

            response_text = "\n".join(response_parts)
            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            error_text = f"""❌ **Vector Search Error**

**Query**: "{query}"
**Collection**: {collection_name}
🚫 **Error**: {str(e)}

**Troubleshooting**:
- Check if the collection exists and has documents
- Verify MongoDB vector search index is configured
- Ensure the collection has embedded documents
- Check your OpenAI API key for query embedding
"""
            return [TextContent(type="text", text=error_text)]


class CollectionManagementTool:
    """MCP tool for collection management operations."""

    def __init__(self):
        """Initialize the collection management tool."""
        self.mongodb_store = MongoDBVectorStore()

    def get_tool_definition(self) -> Tool:
        """Get the MCP tool definition."""
        return Tool(
            name="list_collections",
            description="List all available MongoDB collections and their statistics",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_stats": {
                        "type": "boolean",
                        "description": "Whether to include collection statistics",
                        "default": True,
                    }
                },
            },
        )

    async def execute(self, include_stats: bool = True) -> List[TextContent]:
        """Execute collection listing.

        Args:
            include_stats: Whether to include collection statistics

        Returns:
            List of text content with collection information
        """
        try:
            logger.info("Listing MongoDB collections")

            # Get all collections
            collections = await self.mongodb_store.list_collections()

            if not collections:
                response_text = """📊 **MongoDB Collections**

No collections found in the database.

To get started:
1. Use the `ingest_document` tool to process and store documents
2. Documents will be stored in collections for vector search
"""
                return [TextContent(type="text", text=response_text)]

            # Build response
            response_parts = [
                "📊 **MongoDB Collections**\n",
                f"**Database**: {self.mongodb_store.database_name}",
                f"**Total Collections**: {len(collections)}\n",
            ]

            # Get stats for each collection if requested
            for i, collection_name in enumerate(collections, 1):
                collection_section = [f"## {i}. {collection_name}"]

                if include_stats:
                    try:
                        stats = await self.mongodb_store.get_collection_stats(collection_name)

                        if "error" not in stats:
                            collection_section.extend(
                                [
                                    f"- **Documents**: {stats.get('document_count', 0):,}",
                                    f"- **Size**: {stats.get('size_bytes', 0) / 1024 / 1024:.2f} MB",
                                    f"- **Storage Size**: {stats.get('storage_size_bytes', 0) / 1024 / 1024:.2f} MB",
                                ]
                            )

                            avg_size = stats.get("avg_obj_size", 0)
                            if avg_size > 0:
                                collection_section.append(
                                    f"- **Avg Document Size**: {avg_size / 1024:.2f} KB"
                                )
                        else:
                            collection_section.append(
                                f"- **Status**: Error getting stats - {stats['error']}"
                            )

                    except Exception as e:
                        collection_section.append(f"- **Status**: Error - {str(e)}")

                collection_section.append("")  # Empty line
                response_parts.extend(collection_section)

            response_text = "\n".join(response_parts)
            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            error_text = f"""❌ **Collection Listing Error**

🚫 **Error**: {str(e)}

**Troubleshooting**:
- Check MongoDB connection
- Verify database permissions
- Ensure database exists
"""
            return [TextContent(type="text", text=error_text)]


# Global tool instances
vector_search_tool = VectorSearchTool()
collection_management_tool = CollectionManagementTool()


# MCP tool functions
async def search_documents(
    query: str,
    collection_name: str = "documents",
    limit: int = 5,
    similarity_threshold: float = 0.7,
    metadata_filter: Optional[Dict[str, Any]] = None,
    include_similarity_scores: bool = True,
) -> List[TextContent]:
    """Search for relevant document chunks using vector similarity.

    This tool converts your query to an embedding and finds the most
    semantically similar document chunks stored in MongoDB.

    Args:
        query: Search query text
        collection_name: MongoDB collection to search (default: "documents")
        limit: Maximum number of results (default: 5, max: 50)
        similarity_threshold: Minimum similarity score 0.0-1.0 (default: 0.7)
        metadata_filter: Additional filters for document metadata (optional)
        include_similarity_scores: Include similarity scores in results (default: True)

    Returns:
        List of relevant document chunks with metadata and similarity scores
    """
    return await vector_search_tool.execute(
        query=query,
        collection_name=collection_name,
        limit=limit,
        similarity_threshold=similarity_threshold,
        metadata_filter=metadata_filter,
        include_similarity_scores=include_similarity_scores,
    )


async def list_collections(include_stats: bool = True) -> List[TextContent]:
    """List all available MongoDB collections and their statistics.

    This tool shows all collections in the database with document counts
    and storage information to help you understand what data is available.

    Args:
        include_stats: Whether to include detailed collection statistics (default: True)

    Returns:
        List of collections with statistics
    """
    return await collection_management_tool.execute(include_stats=include_stats)

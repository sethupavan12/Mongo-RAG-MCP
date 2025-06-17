#!/usr/bin/env python3
"""MongoDB Vector RAG MCP Server - Main entry point."""

import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional

from mcp.server import FastMCP

from config import get_settings
from services.embeddings import EmbeddingService
from services.mongodb_client import MongoDBVectorStore
from services.unstructured_client import DocumentProcessor
import openai

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
app = FastMCP("MongoDB Vector RAG MCP Server")


@app.tool()
async def ingest_document(
    document_url: str,
    collection_name: str = "documents",
    chunking_strategy: str = "by_title",
    metadata_fields: Optional[Dict[str, Any]] = None,
    max_chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> str:
    """Process and ingest a document into MongoDB vector collection for RAG applications.
    
    Args:
        document_url: URL or local path to document (PDF, DOCX, TXT, etc.)
        collection_name: MongoDB collection name to store the document
        chunking_strategy: Document chunking strategy (by_title or basic)
        metadata_fields: Additional metadata to store with document chunks
        max_chunk_size: Maximum size of document chunks in characters
        chunk_overlap: Overlap between chunks in characters
    
    Returns:
        Success message with ingestion details
    """
    try:
        logger.info(f"Starting document ingestion: {document_url}")

        # Initialize services
        mongodb_store = MongoDBVectorStore()
        embedding_service = EmbeddingService()
        document_processor = DocumentProcessor()
        settings = get_settings()

        # Validate inputs
        if not document_url.strip():
            raise ValueError("Document URL cannot be empty")

        # Update processor settings if provided
        if max_chunk_size != settings.max_chunk_size:
            document_processor.max_chunk_size = max_chunk_size
        if chunk_overlap != settings.chunk_overlap:
            document_processor.chunk_overlap = chunk_overlap

        # Process document
        if document_processor.is_url(document_url):
            chunks = await document_processor.process_document_from_url(
                document_url,
                chunking_strategy=chunking_strategy,
                additional_metadata=metadata_fields,
            )
        else:
            chunks = await document_processor.process_document(
                document_url,
                chunking_strategy=chunking_strategy,
                additional_metadata=metadata_fields,
            )

        if not chunks:
            return "❌ No content extracted from document. Please check the document format and content."

        logger.info(f"Extracted {len(chunks)} chunks from document")

        # Generate embeddings for chunks
        chunk_texts = [chunk.content for chunk in chunks]
        embeddings = await embedding_service.generate_embeddings(chunk_texts)

        if len(embeddings) != len(chunks):
            raise ValueError(f"Embedding count mismatch: {len(embeddings)} vs {len(chunks)}")

        # Create DocumentChunk objects with embeddings
        from services.mongodb_client import DocumentChunk
        
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
            "embedding_model": embedding_service.get_model_name(),
            "total_chunks": len(document_chunks),
        }
        if metadata_fields:
            source_metadata.update(metadata_fields)

        storage_result = await mongodb_store.store_embeddings(
            document_chunks, collection_name, source_metadata
        )

        # Format response
        if storage_result["success"]:
            return f"""✅ **Document Ingestion Successful**

📄 **Document**: {document_url}
📊 **Collection**: {collection_name}
🔢 **Chunks Created**: {storage_result['chunks_stored']}
⚙️ **Chunking Strategy**: {chunking_strategy}
🤖 **Embedding Model**: {embedding_service.get_model_name()}
📏 **Chunk Size**: {max_chunk_size} chars (overlap: {chunk_overlap})

**Processing Summary**:
- Extracted {len(chunks)} text elements
- Generated {len(embeddings)} embeddings
- Stored {storage_result['chunks_stored']} chunks successfully

The document is now ready for vector search queries in the '{collection_name}' collection.
"""
        else:
            return f"""❌ **Document Ingestion Failed**

📄 **Document**: {document_url}
📊 **Collection**: {collection_name}
🔢 **Chunks Processed**: {len(chunks)}

**Error**: {storage_result.get('error', 'Unknown storage error')}

Please check your MongoDB connection and try again.
"""

    except Exception as e:
        logger.error(f"Document ingestion failed: {e}")
        return f"""❌ **Document Ingestion Error**

📄 **Document**: {document_url}
🚫 **Error**: {str(e)}

**Troubleshooting**:
1. Ensure the document URL is accessible
2. Check if the document format is supported (PDF, DOCX, TXT)
3. Verify MongoDB connection and credentials
4. Check OpenAI API key and quota
"""


@app.tool()
async def search_documents(
    query: str,
    collection_name: str = "documents",
    limit: int = 5,
    similarity_threshold: float = 0.7,
    metadata_filter: Optional[Dict[str, Any]] = None,
    include_similarity_scores: bool = True,
) -> str:
    """Search for relevant document chunks using vector similarity in MongoDB.
    
    Args:
        query: Search query text to find relevant document chunks
        collection_name: MongoDB collection name to search in
        limit: Maximum number of results to return (1-50)
        similarity_threshold: Minimum similarity score (0.0 to 1.0)
        metadata_filter: Additional filters for document metadata
        include_similarity_scores: Whether to include similarity scores in results
    
    Returns:
        Formatted search results with relevant document chunks
    """
    try:
        logger.info(f"Searching documents: '{query}' in collection '{collection_name}'")

        # Initialize services
        mongodb_store = MongoDBVectorStore()
        embedding_service = EmbeddingService()

        # Validate inputs
        if not query.strip():
            raise ValueError("Search query cannot be empty")

        if limit < 1 or limit > 50:
            raise ValueError("Limit must be between 1 and 50")

        if similarity_threshold < 0.0 or similarity_threshold > 1.0:
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")

        # Generate query embedding
        query_embedding = await embedding_service.generate_single_embedding(query)

        # Search documents
        search_results = await mongodb_store.vector_search(
            query_embedding=query_embedding,
            collection_name=collection_name,
            limit=limit,
            similarity_threshold=similarity_threshold,
            metadata_filter=metadata_filter or {},
        )

        # Format results
        if not search_results:
            return f"""🔍 **No Results Found**

**Query**: "{query}"
**Collection**: {collection_name}
**Threshold**: {similarity_threshold}

Try:
- Lowering the similarity threshold
- Using different search terms
- Checking if documents exist in the collection
"""

        result_text = f"""🔍 **Search Results**

**Query**: "{query}"
**Collection**: {collection_name}
**Found**: {len(search_results)} results

---

"""

        for i, result in enumerate(search_results, 1):
            similarity_score = result.get("similarity_score", 0.0)
            content = result.get("content", "")
            metadata = result.get("metadata", {})

            result_text += f"**Result {i}**"
            if include_similarity_scores:
                result_text += f" (Score: {similarity_score:.3f})"
            result_text += "\n\n"

            # Add content (truncate if very long)
            if len(content) > 500:
                result_text += f"{content[:500]}...\n\n"
            else:
                result_text += f"{content}\n\n"

            # Add relevant metadata
            if metadata:
                metadata_str = ", ".join([f"{k}: {v}" for k, v in metadata.items() if k not in ["_id", "embedding"]])
                if metadata_str:
                    result_text += f"*Source: {metadata_str}*\n\n"

            result_text += "---\n\n"

        return result_text

    except Exception as e:
        logger.error(f"Document search failed: {e}")
        return f"""❌ **Search Error**

**Query**: "{query}"
**Collection**: {collection_name}
🚫 **Error**: {str(e)}

**Troubleshooting**:
1. Verify the collection exists and has documents
2. Check MongoDB connection
3. Ensure the query is not empty
4. Verify OpenAI API key for query embedding
"""


@app.tool()
async def query_contract(
    question: str,
    collection_name: str = "contract_analysis",
    limit: int = 3,
    similarity_threshold: float = 0.7,
) -> str:
    """Ask questions about contracts and get AI-powered answers based on the document content.
    
    This function searches for relevant contract content and uses AI to provide intelligent 
    responses based on the found information.
    
    Args:
        question: Your question about the contract or document content
        collection_name: MongoDB collection name to search in
        limit: Maximum number of document chunks to consider (1-10)
        similarity_threshold: Minimum similarity score (0.0 to 1.0)
    
    Returns:
        AI-generated response based on relevant contract content
    """
    try:
        logger.info(f"Processing contract query: '{question}' in collection '{collection_name}'")

        # Initialize services
        mongodb_store = MongoDBVectorStore()
        embedding_service = EmbeddingService()
        settings = get_settings()

        # Validate inputs
        if not question.strip():
            raise ValueError("Question cannot be empty")

        if limit < 1 or limit > 10:
            raise ValueError("Limit must be between 1 and 10")

        if similarity_threshold < 0.0 or similarity_threshold > 1.0:
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")

        # Generate query embedding
        query_embedding = await embedding_service.generate_single_embedding(question)

        # Search for relevant documents
        search_results = await mongodb_store.vector_search(
            query_embedding=query_embedding,
            collection_name=collection_name,
            limit=limit,
            similarity_threshold=similarity_threshold,
            metadata_filter={},
        )

        # Check if we found relevant content
        if not search_results:
            return f"""🤖 **AI Assistant Response**

I couldn't find any relevant information in the {collection_name} collection to answer your question: "{question}"

This could mean:
- No documents contain information related to your query
- The similarity threshold ({similarity_threshold}) is too high
- The collection might be empty or not indexed properly

Try rephrasing your question or lowering the similarity threshold.
"""

        # Prepare context from search results
        context_parts = []
        for i, result in enumerate(search_results, 1):
            content = result.get("content", "")
            similarity_score = result.get("similarity_score", 0.0)
            metadata = result.get("metadata", {})
            
            # Get source info if available
            source_info = ""
            if "filename" in metadata:
                source_info = f" (from {metadata['filename']}"
                if "page_number" in metadata:
                    source_info += f", page {metadata['page_number']}"
                source_info += ")"
            
            context_parts.append(f"[Excerpt {i}, similarity: {similarity_score:.3f}{source_info}]\n{content}\n")

        context = "\n".join(context_parts)

        # Create the prompt for OpenAI
        system_prompt = """You are an AI assistant specialized in analyzing contract documents. You have been provided with relevant excerpts from contract documents based on a user's question. 

Your task is to:
1. Analyze the provided contract excerpts carefully
2. Answer the user's question based ONLY on the information provided in the excerpts
3. Be specific and cite relevant parts of the contract when possible
4. If the provided excerpts don't contain enough information to fully answer the question, say so clearly
5. Provide a helpful, professional response that a contract analyst would give

Always base your response on the contract content provided and be honest about the limitations of the available information."""

        user_prompt = f"""Question: {question}

Relevant contract excerpts:
{context}

Please provide a comprehensive answer to the question based on the contract information provided above."""

        # Get AI response using OpenAI
        client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.3,  # Lower temperature for more focused, factual responses
        )

        ai_response = response.choices[0].message.content

        # Format the final response
        result_text = f"""🤖 **AI Contract Analysis**

**Your Question**: "{question}"

**Answer**: {ai_response}

---

**Sources Consulted**: {len(search_results)} relevant contract sections
**Collection**: {collection_name}
**Similarity Scores**: {', '.join([f'{r.get("similarity_score", 0):.3f}' for r in search_results])}
"""

        return result_text

    except Exception as e:
        logger.error(f"Contract query failed: {e}")
        return f"""❌ **Contract Query Error**

**Question**: "{question}"
**Collection**: {collection_name}
🚫 **Error**: {str(e)}

**Troubleshooting**:
1. Verify the collection exists and has contract documents
2. Check MongoDB and OpenAI API connections
3. Ensure your question is clear and specific
4. Try a different similarity threshold if no results found
"""


@app.tool()
async def list_collections(include_stats: bool = True) -> str:
    """List all available MongoDB collections and their statistics.
    
    Args:
        include_stats: Whether to include collection statistics
    
    Returns:
        Formatted list of collections with optional statistics
    """
    try:
        logger.info("Listing MongoDB collections")

        # Initialize MongoDB store
        mongodb_store = MongoDBVectorStore()

        # Get collections and stats
        collection_names = await mongodb_store.list_collections()

        if not collection_names:
            return """📂 **No Collections Found**

The database appears to be empty or there was an issue accessing collections.

To get started:
1. Use the `ingest_document` tool to add documents
2. Verify your MongoDB connection settings
"""

        result_text = "📂 **MongoDB Collections**\n\n"

        for collection_name in collection_names:
            result_text += f"**{collection_name}**\n"

            if include_stats:
                try:
                    stats = await mongodb_store.get_collection_stats(collection_name)
                    doc_count = stats.get("document_count", 0)
                    size = stats.get("size_bytes", 0)
                    avg_size = stats.get("avg_obj_size", 0)

                    result_text += f"- Documents: {doc_count:,}\n"
                    result_text += f"- Size: {size:,} bytes\n"
                    result_text += f"- Average doc size: {avg_size:,.0f} bytes\n"
                except Exception as e:
                    result_text += f"- Stats: Error retrieving ({str(e)[:50]}...)\n"

            result_text += "\n"

        result_text += """
**Available Actions**:
- Use `search_documents` to query any collection
- Use `ingest_document` to add more documents
"""

        return result_text

    except Exception as e:
        logger.error(f"List collections failed: {e}")
        return f"""❌ **Collections List Error**

🚫 **Error**: {str(e)}

**Troubleshooting**:
1. Check MongoDB connection settings
2. Verify database credentials
3. Ensure the database exists
"""


def _validate_config():
    """Validate server configuration."""
    settings = get_settings()
    
    # Check required settings
    if not settings.mongodb_uri:
        raise ValueError("MONGODB_URI is required")

    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required")

    logger.info("Configuration validated successfully")


def main():
    """Main entry point for the MCP server."""
    try:
        # Validate configuration
        _validate_config()
        logger.info("Starting MongoDB Vector RAG MCP Server...")
        
        # Check if we should run in HTTP mode for web frontend
        if len(sys.argv) > 1 and sys.argv[1] == "--http":
            logger.info("Running in SSE HTTP mode for web frontend")
            app.run(transport="sse")
        else:
            # Default STDIO transport for MCP clients
            logger.info("Running in STDIO mode for MCP clients")
            app.run(transport="stdio")
        
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

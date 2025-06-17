"""MongoDB vector store client for document storage and search."""

import logging
import ssl
from typing import Any, Dict, List, Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

from config import get_settings

logger = logging.getLogger(__name__)


class DocumentChunk:
    """Represents a document chunk with metadata."""

    def __init__(
        self,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
        chunk_id: Optional[str] = None,
    ):
        self.content = content
        self.embedding = embedding
        self.metadata = metadata or {}
        self.chunk_id = chunk_id


class MongoDBVectorStore:
    """MongoDB client for vector storage and search operations."""

    def __init__(
        self, connection_string: Optional[str] = None, database_name: Optional[str] = None
    ):
        """Initialize MongoDB vector store.

        Args:
            connection_string: MongoDB connection URI
            database_name: Database name to use
        """
        settings = get_settings()
        self.connection_string = connection_string or settings.mongodb_uri
        self.database_name = database_name or settings.mongodb_database

        try:
            # Add SSL configuration for Atlas connections
            client_options = {
                "serverSelectionTimeoutMS": 5000,  # 5 second timeout
                "socketTimeoutMS": 5000,
                "connectTimeoutMS": 5000,
            }
            
            # If this is an Atlas connection, add SSL settings
            if "mongodb.net" in self.connection_string:
                client_options.update({
                    "ssl": True,
                    "tlsAllowInvalidCertificates": True,  # Less strict for demo
                    "retryWrites": True,
                })
            
            self.client = MongoClient(self.connection_string, **client_options)
            self.database: Database = self.client[self.database_name]
            
            # Test connection
            self.client.server_info()
            logger.info(f"Connected to MongoDB database: {self.database_name}")
        except PyMongoError as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def get_collection(self, collection_name: str) -> Collection:
        """Get a MongoDB collection.

        Args:
            collection_name: Name of the collection

        Returns:
            MongoDB collection instance
        """
        return self.database[collection_name]

    async def store_embeddings(
        self,
        chunks: List[DocumentChunk],
        collection_name: str,
        source_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Store document chunks with embeddings in MongoDB.

        Args:
            chunks: List of document chunks with embeddings
            collection_name: Target collection name
            source_metadata: Additional metadata about the source document

        Returns:
            Dictionary with storage results
        """
        try:
            collection = self.get_collection(collection_name)

            # Prepare documents for insertion
            documents = []
            for i, chunk in enumerate(chunks):
                doc = {
                    "content": chunk.content,
                    "embedding": chunk.embedding,
                    "metadata": {
                        **chunk.metadata,
                        "chunk_index": i,
                        "collection_name": collection_name,
                        **(source_metadata or {}),
                    },
                }
                if chunk.chunk_id:
                    doc["_id"] = chunk.chunk_id

                documents.append(doc)

            # Insert documents
            result = collection.insert_many(documents)

            logger.info(
                f"Stored {len(result.inserted_ids)} chunks in collection '{collection_name}'"
            )

            return {
                "success": True,
                "collection_name": collection_name,
                "chunks_stored": len(result.inserted_ids),
                "inserted_ids": [str(id) for id in result.inserted_ids],
            }

        except PyMongoError as e:
            logger.error(f"Failed to store embeddings: {e}")
            return {
                "success": False,
                "error": str(e),
                "collection_name": collection_name,
                "chunks_stored": 0,
            }

    async def vector_search(
        self,
        query_embedding: List[float],
        collection_name: str,
        limit: int = 5,
        similarity_threshold: Optional[float] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search.

        Args:
            query_embedding: Query vector embedding
            collection_name: Collection to search in
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            metadata_filter: Additional filters for metadata

        Returns:
            List of matching documents with similarity scores
        """
        try:
            collection = self.get_collection(collection_name)

            # Build aggregation pipeline
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": limit * 10,  # Overrequest for better results
                        "limit": limit,
                    }
                },
                {"$addFields": {"similarity_score": {"$meta": "vectorSearchScore"}}},
            ]

            # Add metadata filter if provided
            if metadata_filter:
                pipeline.insert(1, {"$match": metadata_filter})

            # Add similarity threshold filter if provided
            if similarity_threshold:
                pipeline.append({"$match": {"similarity_score": {"$gte": similarity_threshold}}})

            # Project relevant fields
            pipeline.append(
                {"$project": {"content": 1, "metadata": 1, "similarity_score": 1, "_id": 0}}
            )

            # Execute search
            results = list(collection.aggregate(pipeline))

            logger.info(f"Vector search returned {len(results)} results from '{collection_name}'")

            return results

        except PyMongoError as e:
            logger.error(f"Vector search failed: {e}")
            return []

    async def list_collections(self) -> List[str]:
        """List all collections in the database.

        Returns:
            List of collection names
        """
        try:
            return self.database.list_collection_names()
        except PyMongoError as e:
            logger.error(f"Failed to list collections: {e}")
            return []

    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Collection statistics
        """
        try:
            collection = self.get_collection(collection_name)

            # Get basic stats
            stats = self.database.command("collStats", collection_name)

            # Get document count
            doc_count = collection.count_documents({})

            return {
                "collection_name": collection_name,
                "document_count": doc_count,
                "size_bytes": stats.get("size", 0),
                "storage_size_bytes": stats.get("storageSize", 0),
                "avg_obj_size": stats.get("avgObjSize", 0),
            }

        except PyMongoError as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"collection_name": collection_name, "error": str(e)}

    def close(self):
        """Close the MongoDB connection."""
        if hasattr(self, "client"):
            self.client.close()
            logger.info("MongoDB connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

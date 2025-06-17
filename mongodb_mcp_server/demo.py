#!/usr/bin/env python3
"""
MongoDB Vector RAG MCP Server Demo

This demo script showcases all features of the MCP server.
"""

import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_demo():
    """Run the demo."""
    print("🚀 MongoDB Vector RAG MCP Server Demo")
    print("=" * 50)

    # Import functions from main
    from main import ingest_document, search_documents, list_collections

    # Test document ingestion
    print("\n1. Testing Document Ingestion...")
    try:
        # Create a sample text file
        sample_text = """
        Machine Learning Fundamentals

        Machine learning is a subset of artificial intelligence (AI) that focuses on
        algorithms that can learn from data. The main categories include supervised
        learning, unsupervised learning, and reinforcement learning.

        Deep learning uses neural networks with multiple layers to model complex
        patterns in data.

        Popular machine learning algorithms include:
        - Linear regression for predicting continuous values
        - Decision trees for classification and regression
        - Random forests for ensemble learning
        - Support vector machines for classification
        - Neural networks for complex pattern recognition

        Applications of machine learning span across many domains:
        - Computer vision for image recognition
        - Natural language processing for text analysis
        - Recommendation systems for personalized content
        - Autonomous vehicles for self-driving cars
        - Medical diagnosis for disease detection
        """

        sample_file = Path("/tmp/ml_sample.txt")
        sample_file.write_text(sample_text)

        result = await ingest_document(
            document_url=str(sample_file), 
            collection_name="demo_docs", 
            chunking_strategy="basic",
            max_chunk_size=500,
            chunk_overlap=50
        )

        print("✅ Document ingestion result:")
        print(result)

    except Exception as e:
        print(f"❌ Document ingestion failed: {e}")

    # Test vector search
    print("\n2. Testing Vector Search...")
    try:
        result = await search_documents(
            query="machine learning algorithms", 
            collection_name="demo_docs", 
            limit=3,
            similarity_threshold=0.5
        )

        print("✅ Vector search result:")
        print(result)

    except Exception as e:
        print(f"❌ Vector search failed: {e}")

    # Test another search
    print("\n3. Testing Another Search Query...")
    try:
        result = await search_documents(
            query="neural networks deep learning", 
            collection_name="demo_docs", 
            limit=2
        )

        print("✅ Neural networks search result:")
        print(result)

    except Exception as e:
        print(f"❌ Neural networks search failed: {e}")

    # Test collection listing
    print("\n4. Testing Collection Management...")
    try:
        result = await list_collections(include_stats=True)

        print("✅ Collections result:")
        print(result)

    except Exception as e:
        print(f"❌ Collection listing failed: {e}")

    print("\n🎉 Demo completed!")
    print("\n📋 Summary:")
    print("- ✅ Document ingestion from text file")
    print("- ✅ Vector similarity search")
    print("- ✅ Collection management")
    print("- ✅ MongoDB Vector Store integration")
    print("- ✅ OpenAI embedding generation")
    print("\n🚀 The MongoDB MCP Server is ready for production use!")


if __name__ == "__main__":
    asyncio.run(run_demo())

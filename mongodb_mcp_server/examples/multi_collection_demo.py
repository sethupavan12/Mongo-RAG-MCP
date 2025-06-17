#!/usr/bin/env python3
"""
Multi-Collection Vector Search Demo

This demo shows different strategies for managing multiple collections
and vector indexes in a production environment.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from main import ingest_document, search_documents, list_collections
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiCollectionVectorRAG:
    """Demonstrates different collection strategies for vector RAG."""
    
    def __init__(self):
        # Different collection naming strategies
        self.strategies = {
            "single": "all_documents",
            "by_type": "{document_type}_docs", 
            "by_user": "user_{user_id}_docs",
            "hybrid": "{tenant}_{document_type}_docs"
        }
        
        # Sample data for demonstration
        self.sample_documents = [
            {
                "path": "examples/Sample_contract_public.pdf",
                "user_id": "user_123",
                "tenant": "company_abc", 
                "document_type": "contract",
                "title": "Service Agreement"
            },
            # Add more documents here for testing
        ]
    
    def get_collection_name(self, strategy: str, **metadata) -> str:
        """Generate collection name based on strategy and metadata."""
        
        if strategy == "single":
            return "all_documents"
        
        elif strategy == "by_type":
            doc_type = metadata.get("document_type", "general")
            return f"{doc_type}_docs"
        
        elif strategy == "by_user":
            user_id = metadata.get("user_id", "anonymous")
            return f"user_{user_id}_docs"
        
        elif strategy == "hybrid":
            tenant = metadata.get("tenant", "default")
            doc_type = metadata.get("document_type", "general")
            return f"{tenant}_{doc_type}_docs"
        
        else:
            return "default_collection"
    
    async def demonstrate_single_collection(self):
        """Strategy 1: Single collection with metadata filtering."""
        print("\n🔍 **Strategy 1: Single Collection with Metadata**")
        print("=" * 60)
        
        collection_name = "all_documents"
        
        # Process document with rich metadata
        print(f"📄 Processing document into collection: {collection_name}")
        
        # Add comprehensive metadata
        metadata = {
            "user_id": "user_123",
            "tenant": "company_abc",
            "document_type": "contract",
            "title": "Service Agreement",
            "department": "legal",
            "confidentiality": "internal"
        }
        
        try:
            result = await ingest_document(
                document_url="examples/Sample_contract_public.pdf",
                collection_name=collection_name,
                chunking_strategy="basic",
                max_chunk_size=600,
                chunk_overlap=50,
                metadata_fields=metadata
            )
            print("✅ Single collection result:")
            print(result)
            
            # Demonstrate metadata filtering in search
            print(f"\n🔍 **Searching with metadata context**")
            search_result = await search_documents(
                query="What are the payment terms?",
                collection_name=collection_name,
                limit=2,
                similarity_threshold=0.3,
                metadata_filter={"user_id": "user_123", "document_type": "contract"}
            )
            print(search_result)
            
        except Exception as e:
            print(f"❌ Error in single collection demo: {e}")
    
    async def demonstrate_type_based_collections(self):
        """Strategy 2: Separate collections by document type."""
        print("\n📂 **Strategy 2: Collection Per Document Type**")
        print("=" * 60)
        
        document_types = ["contracts", "reports", "manuals"]
        
        for doc_type in document_types:
            collection_name = f"{doc_type}_docs"
            print(f"\n📄 Collection: {collection_name}")
            
            # Each document type can have different processing settings
            if doc_type == "contracts":
                chunk_size, overlap = 800, 100  # Larger chunks for legal text
            elif doc_type == "reports":
                chunk_size, overlap = 600, 75   # Medium chunks for reports
            else:  # manuals
                chunk_size, overlap = 400, 50   # Smaller chunks for procedures
            
            print(f"   - Chunk size: {chunk_size}, Overlap: {overlap}")
            print(f"   - Optimized for: {doc_type}")
            
            # In a real system, you'd process documents here
            # For demo, just show the concept
            print(f"   - Vector index needed: {collection_name}_vector_index")
    
    async def demonstrate_user_based_collections(self):
        """Strategy 3: Separate collections per user."""
        print("\n👤 **Strategy 3: Collection Per User**")
        print("=" * 60)
        
        users = ["user_123", "user_456", "user_789"]
        
        for user_id in users:
            collection_name = f"user_{user_id}_docs"
            print(f"\n👤 User: {user_id}")
            print(f"   - Collection: {collection_name}")
            print(f"   - Complete data isolation")
            print(f"   - User-specific optimizations possible")
            print(f"   - Vector index: {collection_name}_vector_index")
    
    async def demonstrate_hybrid_approach(self):
        """Strategy 4: Hybrid tenant + type approach."""
        print("\n🏢 **Strategy 4: Hybrid Tenant + Document Type**")
        print("=" * 60)
        
        tenants = ["company_abc", "company_xyz"]
        doc_types = ["contracts", "reports"]
        
        for tenant in tenants:
            print(f"\n🏢 Tenant: {tenant}")
            for doc_type in doc_types:
                collection_name = f"{tenant}_{doc_type}_docs"
                print(f"   - {doc_type}: {collection_name}")
        
        print(f"\n✅ Benefits:")
        print(f"   - Tenant isolation")
        print(f"   - Document type optimization")
        print(f"   - Scalable architecture")
        print(f"   - Flexible permissions")
    
    async def show_collection_management_code(self):
        """Show code examples for collection management."""
        print("\n💻 **Collection Management Code Examples**")
        print("=" * 60)
        
        code_examples = """
# 1. Dynamic Collection Selection
def get_user_collection(user_id: str, doc_type: str) -> str:
    return f"user_{user_id}_{doc_type}_docs"

# 2. Metadata-based Filtering  
metadata_filter = {
    "user_id": "user_123",
    "document_type": "contract",
    "department": "legal"
}

# 3. Index Creation Script (MongoDB Shell)
// For each collection, create vector index:
db.user_123_contracts_docs.createSearchIndex(
    "vector_index",
    {
        "definition": {
            "fields": [
                {
                    "type": "vector",
                    "path": "embedding", 
                    "numDimensions": 1536,
                    "similarity": "cosine"
                }
            ]
        }
    }
)

# 4. Multi-collection Search
async def search_across_user_collections(user_id: str, query: str):
    collections = [
        f"user_{user_id}_contracts_docs",
        f"user_{user_id}_reports_docs", 
        f"user_{user_id}_manuals_docs"
    ]
    
    results = []
    for collection in collections:
        result = await search_documents(query, collection)
        results.append(result)
    
    return results
"""
        
        print(code_examples)
    
    async def show_production_recommendations(self):
        """Show production architecture recommendations."""
        print("\n🚀 **Production Recommendations**")
        print("=" * 60)
        
        recommendations = """
📋 **For Small-Medium Applications (< 1000 users):**
   ✅ Strategy 1: Single collection with metadata filtering
   ✅ Simple to manage, one vector index
   ✅ Use metadata filters for user/type isolation
   
📋 **For Large Applications (> 1000 users):**
   ✅ Strategy 4: Hybrid tenant + document type approach
   ✅ Better performance isolation
   ✅ Easier to scale and optimize per use case
   
📋 **For Multi-Tenant SaaS:**
   ✅ Strategy 2 or 4: Separate by tenant
   ✅ Complete data isolation
   ✅ Tenant-specific optimizations
   
📋 **Vector Index Management:**
   ✅ Create indexes programmatically or via Atlas UI
   ✅ Monitor index performance and rebuild if needed
   ✅ Consider different similarity functions per use case
   
📋 **Collection Naming Conventions:**
   ✅ Use consistent patterns: {tenant}_{type}_{purpose}
   ✅ Include version numbers for schema changes
   ✅ Plan for collection limits (Atlas has soft limits)
"""
        
        print(recommendations)
    
    async def run_comprehensive_demo(self):
        """Run the complete multi-collection demonstration."""
        print("🚀 **Multi-Collection Vector RAG Architecture Demo**")
        print("=" * 70)
        
        # Show current collections
        print("\n📊 **Current Collections:**")
        try:
            current_collections = await list_collections(include_stats=True)
            print(current_collections)
        except Exception as e:
            print(f"❌ Could not list collections: {e}")
        
        # Demonstrate each strategy
        await self.demonstrate_single_collection()
        await self.demonstrate_type_based_collections()
        await self.demonstrate_user_based_collections() 
        await self.demonstrate_hybrid_approach()
        
        # Show implementation details
        await self.show_collection_management_code()
        await self.show_production_recommendations()
        
        print("\n🎯 **Key Takeaways:**")
        print("1. Vector indexes are collection-specific (one index per collection)")
        print("2. Choose collection strategy based on your use case and scale")
        print("3. Use metadata filtering for fine-grained access control")
        print("4. Plan your naming conventions early")
        print("5. MongoDB Atlas supports thousands of collections and indexes")


async def main():
    """Main demo function."""
    demo = MultiCollectionVectorRAG()
    await demo.run_comprehensive_demo()


if __name__ == "__main__":
    print("📚 **MongoDB Vector RAG - Multi-Collection Architecture**")
    print("This demo explains different approaches to managing multiple")
    print("collections and vector indexes in production environments.")
    print()
    
    asyncio.run(main()) 
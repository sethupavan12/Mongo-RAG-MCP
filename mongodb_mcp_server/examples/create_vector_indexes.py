#!/usr/bin/env python3
"""
Vector Index Creation Utility

This script helps create MongoDB Atlas Vector Search indexes for different collections.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from services.mongodb_client import MongoDBVectorStore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorIndexManager:
    """Manage vector search indexes for MongoDB collections."""
    
    def __init__(self):
        self.index_templates = {
            "standard": {
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
            },
            "with_metadata": {
                "definition": {
                    "fields": [
                        {
                            "type": "vector", 
                            "path": "embedding",
                            "numDimensions": 1536,
                            "similarity": "cosine"
                        },
                        {
                            "type": "filter",
                            "path": "metadata.user_id"
                        },
                        {
                            "type": "filter", 
                            "path": "metadata.document_type"
                        }
                    ]
                }
            }
        }
    
    def get_collection_strategies(self):
        """Return different collection naming strategies."""
        return {
            "single_collection": ["all_documents"],
            "by_document_type": [
                "contracts_docs",
                "reports_docs", 
                "manuals_docs",
                "emails_docs"
            ],
            "by_user": [
                "user_123_docs",
                "user_456_docs",
                "user_789_docs"
            ],
            "hybrid": [
                "company_abc_contracts_docs",
                "company_abc_reports_docs",
                "company_xyz_contracts_docs", 
                "company_xyz_reports_docs"
            ]
        }
    
    async def check_existing_collections(self):
        """Check what collections currently exist."""
        try:
            store = MongoDBVectorStore()
            collections = await store.list_collections()
            store.close()
            return collections
        except Exception as e:
            logger.error(f"Error checking collections: {e}")
            return []
    
    def generate_index_creation_commands(self, collections: list, strategy: str = "standard"):
        """Generate MongoDB shell commands to create vector indexes."""
        
        commands = []
        template = self.index_templates[strategy]
        
        for collection_name in collections:
            command = f"""
// Create vector search index for {collection_name}
db.{collection_name}.createSearchIndex(
    "vector_index",
    {str(template).replace("'", '"')}
);
"""
            commands.append(command)
        
        return commands
    
    def generate_atlas_ui_instructions(self, collections: list):
        """Generate step-by-step instructions for Atlas UI."""
        
        instructions = f"""
🎯 **MongoDB Atlas UI Instructions for Vector Index Creation**
================================================================

You need to create vector search indexes for {len(collections)} collections:
{chr(10).join(f'   - {col}' for col in collections)}

📋 **Steps for Each Collection:**

1. **Go to MongoDB Atlas Dashboard**
   - Navigate to your cluster
   - Click on the "Search" tab

2. **Create Search Index**
   - Click "Create Search Index"
   - Choose "Vector Search" (not "Search Index")

3. **Configure Index**
   - **Index Name:** vector_index
   - **Database:** vector_rag
   - **Collection:** [use collection name from list above]

4. **Index Definition** (copy this JSON):
```json
{{
  "fields": [
    {{
      "type": "vector",
      "path": "embedding", 
      "numDimensions": 1536,
      "similarity": "cosine"
    }}
  ]
}}
```

5. **Create and Wait**
   - Click "Next" → "Create Search Index"
   - Wait for index to build (2-5 minutes per collection)
   - Status will show "Active" when ready

🔄 **Repeat for each collection in the list above**

✅ **Verification:**
   - Run your MCP server demos to test vector search
   - All searches should return results instead of "No Results Found"
"""
        return instructions
    
    def generate_automation_script(self, collections: list):
        """Generate a Python script to automate index creation (requires Atlas CLI)."""
        
        script = f'''#!/usr/bin/env python3
"""
Automated Vector Index Creation Script

Requires MongoDB Atlas CLI to be installed and configured.
Install with: curl https://atlascli.mongodb.com/install | bash

This script creates vector search indexes for all specified collections.
"""

import subprocess
import time

# Collections that need vector indexes
COLLECTIONS = {collections}

# Atlas configuration (update these)
PROJECT_ID = "your-project-id"  # Get from Atlas dashboard
CLUSTER_NAME = "your-cluster-name"
DATABASE_NAME = "vector_rag"

def create_vector_index(collection_name: str):
    """Create vector search index for a collection using Atlas CLI."""
    
    index_definition = {{
        "name": "vector_index",
        "definition": {{
            "fields": [
                {{
                    "type": "vector",
                    "path": "embedding",
                    "numDimensions": 1536,
                    "similarity": "cosine"
                }}
            ]
        }}
    }}
    
    # Atlas CLI command to create search index
    cmd = [
        "atlas", "clusters", "search", "indexes", "create",
        "--clusterName", CLUSTER_NAME,
        "--projectId", PROJECT_ID,
        "--db", DATABASE_NAME,
        "--collection", collection_name,
        "--file", f"/tmp/{{collection_name}}_index.json"
    ]
    
    # Write index definition to temp file
    import json
    with open(f"/tmp/{{collection_name}}_index.json", "w") as f:
        json.dump(index_definition, f, indent=2)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Created vector index for {{collection_name}}")
            return True
        else:
            print(f"❌ Failed to create index for {{collection_name}}: {{result.stderr}}")
            return False
    except Exception as e:
        print(f"❌ Error creating index for {{collection_name}}: {{e}}")
        return False

def main():
    """Create vector indexes for all collections."""
    print("🚀 Creating Vector Search Indexes...")
    print(f"Collections: {{COLLECTIONS}}")
    print()
    
    success_count = 0
    for collection_name in COLLECTIONS:
        print(f"Creating index for {{collection_name}}...")
        if create_vector_index(collection_name):
            success_count += 1
        time.sleep(2)  # Rate limiting
    
    print(f"\\n🎉 Created {{success_count}}/{{len(COLLECTIONS)}} vector indexes successfully!")
    print("\\n⏳ Indexes are building in the background. Check Atlas UI for status.")

if __name__ == "__main__":
    main()
'''
        return script
    
    async def run_interactive_setup(self):
        """Run interactive setup to help create vector indexes."""
        print("🚀 **Vector Index Creation Helper**")
        print("=" * 50)
        
        # Check existing collections
        print("\n📊 **Checking existing collections...**")
        existing_collections = await self.check_existing_collections()
        
        if existing_collections:
            print(f"Found {len(existing_collections)} collections:")
            for col in existing_collections:
                print(f"   - {col}")
        else:
            print("No collections found or unable to connect.")
        
        # Show collection strategies
        print(f"\n📋 **Collection Strategy Options:**")
        strategies = self.get_collection_strategies()
        
        for i, (strategy_name, collections) in enumerate(strategies.items(), 1):
            print(f"\n{i}. **{strategy_name.replace('_', ' ').title()}**")
            for col in collections:
                status = "✅ EXISTS" if col in existing_collections else "⚠️  NEEDS INDEX"
                print(f"   - {col} {status}")
        
        # Generate Atlas UI instructions
        print(f"\n" + self.generate_atlas_ui_instructions(existing_collections))
        
        # Generate MongoDB shell commands
        print(f"\n💻 **MongoDB Shell Commands** (alternative method):")
        print("=" * 50)
        commands = self.generate_index_creation_commands(existing_collections)
        for cmd in commands:
            print(cmd)
        
        print(f"\n🤖 **Want automation?** Save this script as create_indexes.py:")
        print("=" * 50)
        automation_script = self.generate_automation_script(existing_collections)
        print(automation_script[:500] + "..." if len(automation_script) > 500 else automation_script)


async def main():
    """Main function."""
    manager = VectorIndexManager()
    await manager.run_interactive_setup()


if __name__ == "__main__":
    print("⚡ **MongoDB Vector Search Index Creator**")
    print("This tool helps you create vector search indexes for your collections.")
    print()
    
    asyncio.run(main()) 
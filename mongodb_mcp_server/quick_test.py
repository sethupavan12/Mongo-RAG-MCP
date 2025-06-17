#!/usr/bin/env python3
"""
Quick test to check existing collections and run simple queries via MCP Agent.
"""

import asyncio
import os
from dotenv import load_dotenv

from agents import Agent, Runner
from agents.mcp import MCPServerStdio

# Load environment variables
load_dotenv()

async def quick_test():
    """Quick test of existing collections."""
    print("🚀 Quick Test - MongoDB Collections via MCP Agent")
    print("=" * 50)
    
    # Get the current directory to find our main.py MCP server
    current_dir = os.path.dirname(os.path.abspath(__file__))
    mcp_server_path = os.path.join(current_dir, "main.py")
    
    # Create MCP server configuration
    async with MCPServerStdio(
        name="MongoDB Vector RAG MCP Server",
        params={
            "command": "python",
            "args": [mcp_server_path],
            "cwd": current_dir,
            "env": dict(os.environ),
        },
        cache_tools_list=True,
        client_session_timeout_seconds=30,
    ) as mcp_server:
        
        print("🔌 Connected to MongoDB Vector RAG MCP Server")
        
        # Create a simple agent
        agent = Agent(
            name="MongoDB Assistant",
            instructions="""
            You are a MongoDB assistant. Help users query document collections.
            Use the available tools to list collections and search for documents.
            Be helpful and explain what you find.
            """,
            mcp_servers=[mcp_server]
        )
        
        # Test 1: List collections
        print("\n📋 Test 1: Listing all collections")
        try:
            result = await Runner.run(
                starting_agent=agent,
                input="List all available collections in the database"
            )
            print("✅ Collections:")
            print(result.final_output)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 2: Search in a specific collection if it exists
        print("\n🔍 Test 2: Search for content in contract_analysis collection")
        try:
            result = await Runner.run(
                starting_agent=agent,
                input="Search for any documents in the 'contract_analysis' collection that mention 'party' or 'agreement'"
            )
            print("✅ Search results:")
            print(result.final_output)
        except Exception as e:
            print(f"❌ Error: {e}")
            
        # Test 3: General search
        print("\n🔍 Test 3: General search across all collections")
        try:
            result = await Runner.run(
                starting_agent=agent,
                input="Search for any documents that contain information about 'terms' or 'conditions'"
            )
            print("✅ Search results:")
            print(result.final_output)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n👋 Quick test completed!")

if __name__ == "__main__":
    asyncio.run(quick_test()) 
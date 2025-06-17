#!/usr/bin/env python3
"""
Direct query script that bypasses MCP protocol to call query_contract directly.
This is a workaround for the TaskGroup crash issue in FastMCP STDIO mode.
"""
import asyncio
import sys
import json
from main import query_contract

async def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No query provided"}))
        return
    
    query = sys.argv[1]
    
    try:
        # Call the query_contract function directly
        result = await query_contract(
            question=query,
            collection_name="contract_analysis",
            limit=3,
            similarity_threshold=0.5
        )
        
        # Return the result as JSON
        print(json.dumps({"result": result, "success": True}))
        
    except Exception as e:
        print(json.dumps({"error": str(e), "success": False}))

if __name__ == "__main__":
    asyncio.run(main()) 
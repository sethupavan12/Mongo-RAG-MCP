#!/usr/bin/env python3
"""
Demo: Query Contract Analysis Collection via MCP Agent

This demo shows how to use the OpenAI Agents SDK with our MongoDB Vector RAG MCP server
to query the previously created 'contract_analysis' collection.

The collection was created by running examples/pdf_demo.py with the Sample_contract_public.pdf file.
"""

import asyncio
import os
from dotenv import load_dotenv

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServerStdio

# Load environment variables
load_dotenv()

async def run_contract_query_demo():
    """
    Demo querying the contract_analysis collection via MCP agent.
    """
    print("🚀 MongoDB Vector RAG MCP Agent - Contract Analysis Query Demo")
    print("=" * 70)
    
    # Get the current directory to find our main.py MCP server
    current_dir = os.path.dirname(os.path.abspath(__file__))
    mcp_server_path = os.path.join(current_dir, "main.py")
    
    print(f"📂 MCP Server Path: {mcp_server_path}")
    
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
        
        # Generate trace ID for debugging
        trace_id = gen_trace_id()
        print(f"🔍 Trace ID: {trace_id}")
        print(f"📊 View trace: https://platform.openai.com/traces/{trace_id}")
        print()
        
        with trace(workflow_name="Contract Analysis Query Demo", trace_id=trace_id):
            # Create an agent specialized for contract analysis
            agent = Agent(
                name="Contract Analysis Assistant",
                instructions="""
                You are a legal document analysis assistant that specializes in reviewing contract information.
                
                You have access to a MongoDB collection called 'contract_analysis' that contains chunks from 
                a processed contract document. Use the search_documents tool to find relevant information
                when users ask questions about the contract.
                
                When providing answers:
                1. Search for relevant contract clauses and information
                2. Provide specific quotes from the contract when possible
                3. Explain the legal implications clearly
                4. Be thorough but concise in your responses
                
                Always specify which collection you're searching (contract_analysis) and provide 
                context about the information you find.
                """,
                mcp_servers=[mcp_server]
            )
            
            print("🤖 Contract Analysis Assistant initialized")
            print()
            
            # Demo 1: Check available collections
            print("📋 Demo 1: Checking available collections")
            collections_result = await Runner.run(
                starting_agent=agent,
                input="List all available collections to see what contract data we have"
            )
            print("✅ Available collections:")
            print(collections_result.final_output)
            print()
            
            # Demo 2: Predefined contract analysis queries
            print("📄 Demo 2: Contract Analysis Queries")
            
            contract_queries = [
                "What are the key terms and conditions outlined in the contract?",
                "Are there any payment terms or financial obligations mentioned?",
                "What is the duration or term of this contract?",
                "Are there any termination clauses or conditions?",
                "What are the deliverables or obligations of each party?",
                "Are there any penalties or consequences for breach of contract?",
                "What governing law applies to this contract?",
                "Are there any confidentiality or non-disclosure provisions?",
                "What are the dispute resolution mechanisms mentioned?"
            ]
            
            for i, query in enumerate(contract_queries, 1):
                print(f"❓ Query {i}: {query}")
                
                try:
                    result = await Runner.run(
                        starting_agent=agent,
                        input=f"Search the contract_analysis collection for information about: {query}"
                    )
                    print("📋 Analysis:")
                    print(result.final_output)
                    print("-" * 50)
                    
                except Exception as e:
                    print(f"❌ Error processing query: {e}")
                    print("-" * 50)
            
            # Demo 3: Interactive contract Q&A
            print("\n💬 Demo 3: Interactive Contract Q&A")
            print("Ask specific questions about the contract!")
            print("Type 'quit' or 'exit' to end the demo.")
            print()
            
            while True:
                try:
                    user_input = input("🗣️  Ask about the contract: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', '']:
                        break
                    
                    result = await Runner.run(
                        starting_agent=agent,
                        input=f"Based on the contract_analysis collection, please answer: {user_input}"
                    )
                    
                    print("🤖 Contract Assistant:")
                    print(result.final_output)
                    print()
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    print()
    
    print("👋 Contract analysis demo completed!")

async def main():
    """Main entry point."""
    try:
        await run_contract_query_demo()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure the 'contract_analysis' collection exists (run examples/pdf_demo.py first)")
        print("2. Ensure vector search index is created in MongoDB Atlas")
        print("3. Ensure OpenAI API key is set in environment")
        print("4. Ensure MongoDB Atlas connection is configured")

if __name__ == "__main__":
    asyncio.run(main()) 
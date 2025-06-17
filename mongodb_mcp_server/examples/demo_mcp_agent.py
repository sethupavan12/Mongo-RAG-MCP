#!/usr/bin/env python3
"""
Demo: OpenAI Agents SDK + MongoDB Vector RAG MCP Server

This demo shows how to properly use the OpenAI Agents SDK to connect to our MongoDB Vector RAG MCP server
and perform document processing and vector search through the MCP protocol.

Unlike demo.py which imports functions directly, this demo uses the MCP server as intended:
- Spawns our MCP server as a subprocess using MCPServerStdio
- Agent discovers tools via MCP's list_tools()
- Agent calls tools via MCP's call_tool()
- Full MCP protocol compliance

Requirements:
- pip install openai-agents
- OpenAI API key in environment or .env file
- MongoDB Atlas connection configured
"""

import asyncio
import os
import shutil
from dotenv import load_dotenv

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServerStdio

# Load environment variables
load_dotenv()

async def run_mcp_agent_demo():
    """
    Run a demo that properly uses the OpenAI Agents SDK with our MongoDB Vector RAG MCP server.
    """
    print("🚀 Starting MongoDB Vector RAG MCP Agent Demo")
    print("=" * 60)
    
    # Check if python is available (needed to run our MCP server)
    if not shutil.which("python"):
        raise RuntimeError("Python is not available in PATH. Please ensure Python is installed.")
    
    # Get the current directory to find our main.py MCP server
    current_dir = os.path.dirname(os.path.abspath(__file__))
    mcp_server_path = os.path.join(current_dir, "main.py")
    
    if not os.path.exists(mcp_server_path):
        raise RuntimeError(f"MCP server not found at {mcp_server_path}. Please ensure main.py exists.")
    
    print(f"📂 MCP Server Path: {mcp_server_path}")
    
    # Create MCP server configuration for stdio transport
    # This will spawn our main.py as a subprocess and communicate via stdin/stdout
    async with MCPServerStdio(
        name="MongoDB Vector RAG MCP Server",
        params={
            "command": "python",
            "args": [mcp_server_path],
            "cwd": current_dir,
            "env": dict(os.environ),  # Pass through all environment variables
        },
        # Cache tools list since our server tools won't change during runtime
        cache_tools_list=True,
        # Increase timeout for MongoDB operations
        client_session_timeout_seconds=30,
    ) as mcp_server:
        
        print("🔌 Connected to MongoDB Vector RAG MCP Server")
        
        # Generate trace ID for debugging (optional)
        trace_id = gen_trace_id()
        print(f"🔍 Trace ID: {trace_id}")
        print(f"📊 View trace: https://platform.openai.com/traces/{trace_id}")
        print()
        
        with trace(workflow_name="MongoDB Vector RAG Demo", trace_id=trace_id):
            # Create an agent that uses our MCP server
            agent = Agent(
                name="MongoDB Vector RAG Assistant",
                instructions="""
                You are a helpful assistant that can process documents and perform vector searches using MongoDB.
                
                Available capabilities:
                1. Ingest documents from URLs - automatically chunk and embed them
                2. Search for similar document chunks using vector similarity
                3. List available collections
                
                When a user asks you to process a document, use the ingest_document tool.
                When a user asks questions about processed documents, use the search_documents tool to find relevant information.
                Always be helpful and explain what you're doing.
                """,
                mcp_servers=[mcp_server]
            )
            
            print("🤖 Agent initialized with MongoDB Vector RAG capabilities")
            print()
            
            # Demo 1: List available tools
            print("📋 Demo 1: Listing available MCP tools")
            tools = await mcp_server.list_tools()
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"  • {tool.name}: {tool.description}")
            print()
            
            # Demo 2: Process a document
            print("📄 Demo 2: Processing a document about machine learning")
            document_url = "https://raw.githubusercontent.com/microsoft/generative-ai-for-beginners/main/04-prompt-engineering-fundamentals/README.md"
            
            ingest_result = await Runner.run(
                starting_agent=agent, 
                input=f"Please ingest and process this document about prompt engineering: {document_url}"
            )
            print("✅ Document processing result:")
            print(ingest_result.final_output)
            print()
            
            # Demo 3: Search for information
            print("🔍 Demo 3: Searching for information in processed documents")
            
            search_queries = [
                "What are the key principles of prompt engineering?",
                "How do you create effective prompts?",
                "What are common prompt engineering techniques?"
            ]
            
            for query in search_queries:
                print(f"❓ Query: {query}")
                
                search_result = await Runner.run(
                    starting_agent=agent,
                    input=f"Search for information about: {query}"
                )
                print("📋 Search result:")
                print(search_result.final_output)
                print("-" * 40)
            
            # Demo 4: Interactive mode (optional)
            print("💬 Demo 4: Interactive mode")
            print("You can now ask questions about the processed documents!")
            print("Type 'quit' or 'exit' to end the demo.")
            print()
            
            while True:
                try:
                    user_input = input("🗣️  Ask a question: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', '']:
                        break
                    
                    result = await Runner.run(
                        starting_agent=agent,
                        input=user_input
                    )
                    
                    print("🤖 Assistant:")
                    print(result.final_output)
                    print()
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    print()
    
    print("👋 Demo completed! MCP server connection closed.")

async def main():
    """Main entry point."""
    try:
        await run_mcp_agent_demo()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure OpenAI API key is set in environment or .env file")
        print("2. Ensure MongoDB Atlas connection is configured")
        print("3. Ensure all required dependencies are installed:")
        print("   pip install openai-agents python-dotenv")
        print("4. Ensure main.py (MCP server) exists in the same directory")

if __name__ == "__main__":
    asyncio.run(main()) 
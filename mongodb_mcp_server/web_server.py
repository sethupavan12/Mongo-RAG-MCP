#!/usr/bin/env python3
"""
FastAPI web server for MongoDB RAG contract analysis.
Exposes the query_contract functionality as a REST API for cloud deployment.
"""
import os
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging

# Import our main query function
from main import query_contract

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MongoDB RAG MCP Demo API",
    description="AI-powered contract analysis using MongoDB Vector Search",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    collection_name: Optional[str] = "contract_analysis"
    limit: Optional[int] = 3
    similarity_threshold: Optional[float] = 0.5

class QueryResponse(BaseModel):
    response: str
    success: bool
    mode: str = "cloud-api"

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "MongoDB RAG MCP Demo API",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": "mongodb-rag-mcp-demo",
        "version": "1.0.0"
    }

@app.post("/api/query", response_model=QueryResponse)
async def query_contract_api(request: QueryRequest):
    """
    Query contract documents using AI-powered analysis.
    
    This endpoint performs vector search on contract documents and uses
    OpenAI GPT-4o-mini to provide intelligent responses.
    """
    try:
        logger.info(f"Processing query: '{request.query}'")
        
        # Call our main query function
        result = await query_contract(
            question=request.query,
            collection_name=request.collection_name,
            limit=request.limit,
            similarity_threshold=request.similarity_threshold
        )
        
        return QueryResponse(
            response=result,
            success=True,
            mode="cloud-api"
        )
        
    except Exception as e:
        logger.error(f"Query failed: {e}")
        error_message = f"""❌ **Contract Query Error**

**Question**: "{request.query}"
**Collection**: {request.collection_name}
🚫 **Error**: {str(e)}

**Troubleshooting**:
1. Verify the collection exists and has contract documents
2. Check MongoDB and OpenAI API connections
3. Ensure your question is clear and specific
4. Try a different similarity threshold if no results found
"""
        
        return QueryResponse(
            response=error_message,
            success=False,
            mode="cloud-api-error"
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        "web_server:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 
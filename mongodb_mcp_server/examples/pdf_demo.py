#!/usr/bin/env python3
"""
PDF Document Analysis Demo using MongoDB Vector RAG MCP Server

This demo shows how to:
1. Process a PDF contract document
2. Store it in MongoDB with vector embeddings
3. Answer specific questions about the document content

Usage:
    python examples/pdf_demo.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path to import main modules
sys.path.append(str(Path(__file__).parent.parent))

from main import ingest_document, search_documents, list_collections
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFContractAnalyzer:
    """Analyze PDF contracts using MongoDB Vector RAG."""
    
    def __init__(self):
        self.pdf_path = "examples/Sample_contract_public.pdf"
        self.collection_name = "contract_analysis"
        
        # Predefined questions about the contract
        # TODO: Add your specific questions here
        self.questions = [
            "What is the contract effective date?",
            "Who are the parties involved in this contract?", 
            "What are the key terms and conditions?",
            "What is the contract duration or term length?",
            "What are the payment terms mentioned?",
            "Are there any termination clauses?",
            "What are the obligations of each party?",
            "Are there any confidentiality provisions?",
            "What happens in case of breach of contract?",
            "Are there any renewal or extension options?"
        ]
    
    async def process_pdf_document(self):
        """Process the PDF document and store in MongoDB."""
        print("📄 **Processing PDF Contract Document**")
        print("=" * 50)
        
        # Check if PDF exists
        if not os.path.exists(self.pdf_path):
            print(f"❌ Error: PDF file not found at {self.pdf_path}")
            return False
        
        print(f"📁 Processing: {self.pdf_path}")
        
        try:
            # Ingest the PDF document
            result = await ingest_document(
                document_url=self.pdf_path,
                collection_name=self.collection_name,
                chunking_strategy="basic",
                max_chunk_size=800,  # Larger chunks for contract analysis
                chunk_overlap=100
            )
            
            print("✅ Document processing result:")
            print(result)
            return True
            
        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
            return False
    
    async def answer_questions(self):
        """Answer predefined questions about the contract."""
        print("\n🔍 **Contract Analysis Q&A**")
        print("=" * 50)
        
        for i, question in enumerate(self.questions, 1):
            print(f"\n**Question {i}:** {question}")
            print("-" * 40)
            
            try:
                # Search for relevant content
                result = await search_documents(
                    query=question,
                    collection_name=self.collection_name,
                    limit=3,
                    similarity_threshold=0.4,  # Lower threshold for broader matching
                    include_similarity_scores=True
                )
                
                print(result)
                
            except Exception as e:
                print(f"❌ Error searching for question {i}: {e}")
            
            print()  # Add spacing between questions
    
    async def show_collection_stats(self):
        """Display collection statistics."""
        print("\n📊 **Collection Statistics**")
        print("=" * 30)
        
        try:
            result = await list_collections(include_stats=True)
            print(result)
        except Exception as e:
            print(f"❌ Error getting collection stats: {e}")
    
    async def run_demo(self):
        """Run the complete PDF analysis demo."""
        print("🚀 **PDF Contract Analysis Demo**")
        print("Using MongoDB Vector RAG MCP Server")
        print("=" * 60)
        
        # Step 1: Process the PDF
        success = await self.process_pdf_document()
        if not success:
            print("❌ Demo failed during PDF processing")
            return
        
        # Step 2: Show collection stats
        await self.show_collection_stats()
        
        # Step 3: Answer questions
        await self.answer_questions()
        
        print("\n🎉 **Demo Complete!**")
        print("\n💡 **Next Steps:**")
        print("1. Add your specific questions to the questions list")
        print("2. Adjust similarity thresholds based on your needs")
        print("3. Modify chunk size and overlap for different document types")
        print("4. Use different embedding models if needed")


async def main():
    """Main demo function."""
    analyzer = PDFContractAnalyzer()
    await analyzer.run_demo()


if __name__ == "__main__":
    print("📋 **MongoDB Vector RAG - PDF Contract Analysis**")
    print("Make sure you have:")
    print("1. Configured your .env file with MongoDB and OpenAI credentials")
    print("2. Created vector search index in MongoDB Atlas")
    print("3. The PDF file exists in the examples/ directory")
    print()
    
    # Run the demo
    asyncio.run(main()) 
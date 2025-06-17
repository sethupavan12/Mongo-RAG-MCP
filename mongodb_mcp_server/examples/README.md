# Examples - MongoDB Vector RAG MCP Server

This folder contains example scripts demonstrating how to use the MongoDB Vector RAG MCP Server with real documents.

## 📄 PDF Contract Analysis Demo

### Overview
The `pdf_demo.py` script demonstrates how to:
- Process PDF documents (contracts, reports, etc.)
- Store them in MongoDB with vector embeddings
- Answer specific questions about the document content
- Perform semantic search across document chunks

### Files
- `pdf_demo.py` - Main demo script for PDF analysis
- `Sample_contract_public.pdf` - Sample contract document for testing

### Usage

1. **Make sure your environment is set up:**
   ```bash
   # Activate virtual environment
   source venv/bin/activate
   
   # Ensure .env file is configured with:
   # - MONGODB_URI (your MongoDB Atlas connection string)
   # - OPENAI_API_KEY (your OpenAI API key)
   ```

2. **Run the PDF demo:**
   ```bash
   python examples/pdf_demo.py
   ```

### What the Demo Does

1. **Document Processing:**
   - Loads the PDF contract document
   - Extracts text using unstructured.io
   - Chunks the content into 800-character segments
   - Generates embeddings using OpenAI
   - Stores in MongoDB collection `contract_analysis`

2. **Question Answering:**
   - Runs 10 predefined questions about the contract
   - Uses vector similarity search to find relevant chunks
   - Returns the most relevant passages with similarity scores

3. **Analysis Questions (Placeholders):**
   - Contract effective date
   - Parties involved
   - Key terms and conditions
   - Contract duration
   - Payment terms
   - Termination clauses
   - Party obligations
   - Confidentiality provisions
   - Breach consequences
   - Renewal options

### Customization

#### Add Your Own Questions
Edit the `questions` list in `PDFContractAnalyzer.__init__()`:

```python
self.questions = [
    "Your custom question here?",
    "Another specific question about the document?",
    # Add more questions...
]
```

#### Adjust Processing Parameters
Modify the document processing settings:

```python
result = await ingest_document(
    document_url=self.pdf_path,
    collection_name=self.collection_name,
    chunking_strategy="basic",
    max_chunk_size=800,    # Increase for longer passages
    chunk_overlap=100,     # Adjust overlap between chunks
    metadata_fields={"document_type": "contract"}  # Optional metadata
)
```

#### Fine-tune Search Parameters
Adjust the search sensitivity:

```python
result = await search_documents(
    query=question,
    collection_name=self.collection_name,
    limit=3,                    # Number of results to return
    similarity_threshold=0.4,   # Lower = more results, higher = more precise
    include_similarity_scores=True
)
```

### Expected Output

The demo will show:
- Document processing progress and statistics
- Collection information (number of chunks, size, etc.)
- For each question:
  - The question being asked
  - Relevant document chunks found
  - Similarity scores
  - Source metadata (page, chunk index, etc.)

### Tips for Best Results

1. **Chunk Size:** 
   - Larger chunks (800-1200) for detailed analysis
   - Smaller chunks (300-500) for precise fact finding

2. **Similarity Threshold:**
   - 0.3-0.4: Broader search, more results
   - 0.6-0.8: Precise search, fewer but more relevant results

3. **Question Design:**
   - Be specific about what you're looking for
   - Use keywords that likely appear in the document
   - Ask one concept per question for best results

### Adding More Documents

To analyze additional PDFs:
1. Place them in the `examples/` folder
2. Update `self.pdf_path` in the script
3. Change `self.collection_name` for different document types

### Integration with AI Agents

This demo shows how any AI agent can use the MCP server to:
- Process documents automatically
- Answer questions about document content
- Perform semantic search across large document collections
- Extract specific information from contracts, reports, manuals, etc.

Perfect for hackathon projects involving document analysis, legal tech, compliance checking, or knowledge management systems!

## 🏗️ Multi-Collection Architecture Demo

### Overview
The `multi_collection_demo.py` script explains different strategies for organizing collections and vector indexes in production environments.

### Usage
```bash
python examples/multi_collection_demo.py
# or
make multi-demo
```

### Collection Strategies Explained

#### 1. **Single Collection Strategy**
- All documents in one collection: `all_documents`
- Use metadata filtering to separate users/types
- ✅ Simple: Only one vector index needed
- ✅ Easy to manage and search across document types
- ❌ Less performance isolation
- **Best for:** Small-medium applications (< 1000 users)

#### 2. **Collection Per Document Type**
- Separate collections: `contracts_docs`, `reports_docs`, `manuals_docs`
- Each collection optimized for specific document type
- ✅ Type-specific optimizations (chunk size, processing)
- ✅ Clean data separation
- ❌ Multiple vector indexes to manage
- **Best for:** Applications with distinct document workflows

#### 3. **Collection Per User**
- User-specific collections: `user_123_docs`, `user_456_docs`
- Complete user data isolation
- ✅ Perfect privacy and security
- ✅ User-specific optimizations
- ❌ Many collections and indexes
- **Best for:** High-security, multi-tenant applications

#### 4. **Hybrid Approach**
- Combines tenant + document type: `company_abc_contracts_docs`
- Best of both worlds
- ✅ Tenant isolation + type optimization
- ✅ Scalable architecture
- **Best for:** Large enterprise or SaaS applications

## ⚡ Vector Index Creation Helper

### Overview
The `create_vector_indexes.py` script helps you create MongoDB Atlas Vector Search indexes for your collections.

### Usage
```bash
python examples/create_vector_indexes.py
```

### What It Does
1. **Scans your database** to see what collections exist
2. **Shows different collection strategies** and which need indexes
3. **Provides Atlas UI instructions** step-by-step
4. **Generates MongoDB shell commands** for automation
5. **Creates automation scripts** for batch index creation

### Key Points About Vector Indexes

#### **Vector Indexes are Collection-Specific**
- Each collection needs its own vector search index
- One index per collection that will use vector search
- Index definition specifies embedding field path and dimensions

#### **Index Creation Options**
1. **Atlas UI** (Recommended for beginners)
   - Visual interface, step-by-step
   - Good for understanding the process
   
2. **MongoDB Shell/mongosh**
   - Command-line interface
   - Good for scripting and automation
   
3. **Atlas CLI**
   - Best for CI/CD and large-scale deployments
   - Requires setup but very powerful

#### **Production Recommendations**

**For Your Hackathon:**
- Start with **single collection** strategy (`all_documents`)
- Create one vector index for that collection
- Use metadata filtering for user/document separation
- Simple and effective!

**For Production Scale:**
- **< 1000 users:** Single collection with metadata filtering
- **> 1000 users:** Hybrid tenant + document type approach
- **Enterprise:** Separate collections per tenant for data isolation
- **Performance critical:** Document-type specific collections

#### **MCP Agent Integration**

Your MCP server automatically handles:
- **Dynamic collection selection** based on parameters
- **Metadata filtering** for user/tenant isolation  
- **Multi-collection search** across user's documents
- **Automatic index requirements** detection

```python
# Example: AI agent using MCP server
await ingest_document(
    document_url="contract.pdf",
    collection_name="user_123_contracts",  # User-specific collection
    metadata_fields={"user_id": "123", "department": "legal"}
)

await search_documents(
    query="payment terms",
    collection_name="user_123_contracts",
    metadata_filter={"department": "legal"}  # Additional filtering
)
```

This architecture makes your MCP server production-ready for any scale! 
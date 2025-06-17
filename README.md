# MongoDB RAG MCP Demo 🚀

A cutting-edge AI-powered document analysis system built for the MongoDB & GitLab hackathon, showcasing the power of MongoDB Vector Search combined with Model Context Protocol (MCP) architecture.

## 🎯 Project Overview

This project demonstrates a complete Retrieval-Augmented Generation (RAG) pipeline using:
- **MongoDB Atlas Vector Search** for intelligent document retrieval
- **FastMCP Server** for scalable AI tool integration
- **OpenAI GPT-4o-mini** for intelligent document analysis
- **Next.js 15** with terminal-style UI for professional presentation

### 🏆 Hackathon Challenge
**MongoDB Track**: AI-driven solution using MongoDB's search and vector search capabilities with Google Cloud integrations to help users understand and interact with document data.

## ✨ Key Features

- 🔍 **Real-time Vector Search** - Semantic similarity search across 666+ contract document chunks
- 🤖 **AI-Powered Analysis** - Natural language responses based on actual document content
- 🖥️ **Terminal Interface** - Authentic terminal aesthetic with real-time processing logs
- 🔄 **MCP Architecture** - Scalable Model Context Protocol server implementation
- 📊 **Smart Ranking** - Similarity scores and source attribution for transparency
- ⚡ **Fast Performance** - Optimized vector embeddings with text-embedding-ada-002

## 🏗️ Project Architecture

```
mongodb_gitlab/
├── mongodb_mcp_server/          # FastMCP Server Implementation
│   ├── main.py                  # Core MCP tools: query_contract, search_documents, ingest_document
│   ├── config.py                # Environment configuration
│   ├── services/                # Core business logic
│   │   ├── mongodb_client.py    # MongoDB Atlas vector operations
│   │   ├── embeddings.py        # OpenAI embedding generation
│   │   └── unstructured_client.py # Document processing
│   ├── tools/                   # Document processing utilities
│   └── examples/                # Sample documents and demos
│
├── contract-analyzer-ui/        # Next.js 15 Frontend
│   ├── src/app/
│   │   ├── page.tsx            # Main terminal interface
│   │   ├── layout.tsx          # App layout and metadata
│   │   └── api/query-mcp/      # Backend API integration
│   ├── package.json            # Dependencies and scripts
│   └── vercel.json            # Deployment configuration
│
└── README.md                   # This comprehensive documentation
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+ with pip
- MongoDB Atlas account with vector search enabled
- OpenAI API key

### 1. Clone and Setup
```bash
git clone <your-repo>
cd mongodb_gitlab
```

### 2. Configure MCP Server
```bash
cd mongodb_mcp_server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB Atlas and OpenAI credentials
```

### 3. Launch Frontend
```bash
cd contract-analyzer-ui
npm install
npm run dev
```

### 4. Access Demo
Open http://localhost:3000 (or 3001 if 3000 is busy)

**The MCP server will start automatically when you make queries!**

### Optional: Test MCP Server Manually
```bash
# Get server information
python start_mcp_server.py

# Run server in HTTP mode for testing
python start_mcp_server.py --http
```

## 🔧 Environment Configuration

Create `mongodb_mcp_server/.env`:
```env
# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://your-cluster.mongodb.net/
MONGODB_DATABASE=vector_rag
MONGODB_COLLECTION=contract_analysis

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Vector Search Configuration
VECTOR_INDEX_NAME=vector_index
EMBEDDING_DIMENSION=1536
SIMILARITY_THRESHOLD=0.7
```

## 📊 Core Components

### MCP Server Tools (`mongodb_mcp_server/main.py`)

#### `query_contract(question, collection_name, limit, similarity_threshold)`
- **Purpose**: AI-powered contract analysis with natural language responses
- **Process**: Vector search → Context preparation → GPT analysis → Formatted response
- **Returns**: Professional contract analysis with source citations

#### `search_documents(query, collection_name, limit, similarity_threshold)`
- **Purpose**: Raw vector search for document chunks
- **Returns**: Ranked document excerpts with similarity scores

#### `ingest_document(document_url, collection_name, chunking_strategy)`
- **Purpose**: Process and store new documents in vector database
- **Supports**: PDF, DOCX, TXT files via Unstructured.io

### Frontend Interface (`contract-analyzer-ui/src/app/page.tsx`)

- **Terminal Simulation**: Authentic command-line experience
- **Real-time Logs**: Processing visualization
- **Markdown Rendering**: Properly formatted AI responses
- **Responsive Design**: Works on desktop and mobile

### API Integration (`contract-analyzer-ui/src/app/api/query-mcp/route.ts`)

- **HTTP Client**: Connects to standalone MCP server via Streamable HTTP
- **MCP Protocol**: Uses proper JSON-RPC calls to MCP tools
- **Error Handling**: Graceful fallbacks and helpful error messages

## 🎨 UI Design Philosophy

**Terminal Aesthetic**:
- Pure black background (`bg-black`)
- Classic terminal colors (green, cyan, orange, blue)
- Monospace fonts for authentic feel
- Mac-style window controls
- Real-time processing logs

**Markdown Styling**:
- Bold text in yellow for emphasis
- Headers in orange/cyan for structure
- Code blocks with green terminal colors
- Proper spacing and typography

## 📈 Performance & Scale

**Current Dataset**:
- **666 document chunks** from sample contract
- **1536-dimensional embeddings** (OpenAI ada-002)
- **Sub-second query response** times
- **Production-ready** error handling

**Scalability**:
- Supports unlimited documents via MongoDB Atlas
- Horizontal scaling through MCP architecture
- Efficient vector indexing for large datasets

## 🚀 Deployment

### Vercel (Frontend)
```bash
cd contract-analyzer-ui
npm run build
# Deploy to Vercel with MongoDB MCP server accessible
```

### Production Considerations
- Ensure MongoDB Atlas whitelist includes deployment IPs
- Set production environment variables
- Configure CORS for API access
- Monitor OpenAI API usage and rate limits

## 🛠️ Technology Stack

**Backend**:
- **FastMCP**: Model Context Protocol server framework
- **MongoDB Atlas**: Vector database with semantic search
- **OpenAI API**: Embeddings (ada-002) and completion (GPT-4o-mini)
- **Unstructured.io**: Document processing and chunking

**Frontend**:
- **Next.js 15**: React framework with Turbopack
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **React Markdown**: Formatted AI response rendering

**DevOps**:
- **Vercel**: Frontend deployment platform
- **Python venv**: Isolated server environment
- **npm**: Package management and build tools

## 📝 Sample Queries

Try these example queries in the demo:

```
"What are the payment terms in this contract?"
"Can you explain clause 16.1.2?"
"What happens if either party wants to terminate?"
"Who is responsible for delivery of services?"
"What are the liability limitations?"
"Can you summarize the key obligations?"
```

## 🎯 Hackathon Achievements

**Technical Innovation**:
- Novel combination of MongoDB Vector Search + MCP architecture
- Real-time AI analysis with source attribution
- Production-ready deployment configuration

**User Experience**:
- Intuitive terminal interface design
- Professional markdown formatting
- Real-time processing transparency

**Scalability**:
- Modular MCP server architecture
- Cloud-native MongoDB Atlas integration
- Extensible for multiple document types

## 🔮 Future Enhancements

- **Multi-language Support**: Expand beyond English documents
- **Advanced Chunking**: Implement intelligent semantic chunking
- **Real-time Collaboration**: Multi-user document analysis
- **Custom Models**: Fine-tuned embedding models for legal documents
- **Integration APIs**: REST/GraphQL APIs for external systems

## 🏆 Live Demo

Visit the deployed application: [Your Deployment URL]

**Demo Credentials**: No authentication required - fully functional demo with sample contract data.

## 📧 Contact

Built for MongoDB & GitLab Hackathon 2024
- **Developer**: [Your Name]
- **GitHub**: [Your GitHub Profile]
- **Demo Video**: [Your 3-minute demo video URL]

---

*This project showcases the powerful combination of MongoDB's intelligent data platform with cutting-edge AI technologies, creating a scalable foundation for document analysis applications across industries.* 
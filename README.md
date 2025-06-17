# 🚀 MongoDB RAG MCP Demo

An AI-powered document analysis system showcasing the power of **MongoDB Atlas Vector Search** and **Model Context Protocol (MCP)** — built for the AI in Action by GCP 2025.

---

## 🎯 Overview

This project rethinks RAG architecture by placing an **Agentic System (via MCP)** at its core — not retrieval, not orchestration. Built as a full-stack, production-ready demo, it answers natural language questions about contracts using:

- **MongoDB Atlas** for vector similarity search  
- **OpenAI GPT-4o-mini** for context-aware reasoning  
- **FastMCP** protocol server for AI-database abstraction  
- **Next.js 15 frontend** with a terminal-style UI  

---

## ✨ Key Features

- 🔍 **Semantic Vector Search** — Real-time similarity search across 600+ contract chunks  
- 🤖 **AI-Powered Legal Analysis** — Ask: _“What are the payment terms?”_  
- 🧠 **MCP Architecture** — RAG lives inside the agent, not outside  
- 🖥️ **Terminal UI** — Command-line aesthetic with real-time logs  
- 📊 **Source Attribution** — Each answer includes origin excerpts + similarity score  
- ⚡ **Fast Performance** — Sub-10s E2E latency, backed by `text-embedding-ada-002`  

---

## 🏗️ Architecture

![Screenshot 2025-06-18 at 3 10 34 AM](https://github.com/user-attachments/assets/05ffa152-adbd-46e0-b1f3-45c69f8e12b1)


## 🚀 Quick Start

### Prerequisites

- Node.js 18+, Python 3.9+  
- MongoDB Atlas w/ Vector Search  
- OpenAI API Key  

### 1. Backend

```bash
cd mongodb_mcp_server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add MongoDB + OpenAI keys
```

### 2. Frontend
```bash
cd contract-analyzer-ui
npm install
npm run dev
```

Open http://localhost:3000
MCP server is called automatically through the API.

### ENV
```
# MongoDB Atlas
MONGODB_URI=mongodb+srv://your-cluster.mongodb.net/
MONGODB_DATABASE=vector_rag
MONGODB_COLLECTION=contract_analysis

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Vector Index
VECTOR_INDEX_NAME=vector_index
EMBEDDING_DIMENSION=1536
SIMILARITY_THRESHOLD=0.7

```

## 📊 Core Components

### MCP Server Tools (`main.py`)
- `query_contract(question, collection_name, limit, similarity_threshold)`  
  → Full RAG pipeline with semantic grounding and source attribution  
- `search_documents(query, collection_name, limit, similarity_threshold)`  
  → Pure vector search with similarity scoring  
- `ingest_document(document_url, collection_name, chunking_strategy)`  
  → Adds new documents to vector DB (PDF, DOCX, TXT via Unstructured.io)

### Frontend Interface (`page.tsx`)
- Terminal-style interaction with real-time logs  
- GPT responses with markdown rendering  
- Responsive design (desktop/mobile)

### API Integration (`query-mcp/route.ts`)
- Connects frontend to MCP server using streamable JSON-RPC  
- Handles timeouts, errors, and invalid queries gracefully  



## 🎨 UI Design Philosophy

### Terminal Aesthetic
- Black background  
- Classic terminal colors (green, orange, cyan)  
- Monospace fonts  
- Mac-style window chrome  
- Real-time processing log feedback  

### Markdown Rendering
- Yellow bolds, cyan/orange headers  
- Code blocks with terminal themes  
- Structured output and readable formatting  


## 📈 Performance & Scale
- ✅ 666 embedded chunks (OpenAI ada-002)  
- ⚡ Sub-second vector search  
- 🧠 Sub-10s total roundtrip latency  
- 🌐 Horizontally scalable via MongoDB + FastMCP  


## 🛠️ Technology Stack

### Backend
- FastAPI + Python (MCP Server)  
- MongoDB Atlas (Vector DB)  
- OpenAI GPT-4o-mini  
- Unstructured.io (Document Parsing)

### Frontend
- Next.js 15 + TypeScript  
- Tailwind CSS  
- React Markdown

### DevOps
- Vercel (Frontend Hosting)  
- Google Cloud Run (MCP Backend)  
- Python venv + npm  

---

## 📝 Sample Queries

Try these:
- “What are the payment terms?”  
- “Can you summarize clause 16?”  
- “Who can terminate the agreement?”  
- “What are the liability limitations?”  
- “Can you list key obligations?”  


## 🔮 Future Enhancements
- 📤 Upload pipeline for custom docs  
- 🧠 Intelligent semantic chunking  
- 🔐 Role-based multi-user access  
- 🌍 Multi-language support  
- 🧩 REST & GraphQL APIs  
- 📈 Real-time collab on contracts  


## 🏆 Hackathon Achievements

### Technical
- Modular MCP server design  
- Real-time vector-backed agent reasoning  
- Cloud-native infra w/ production config  

### UX
- Terminal-style UI that feels familiar  
- Structured answers w/ full citations  
- Live status logs, zero setup friction  

### Scalability
- Works across domains: law, HR, policy, docs  
- Plug-and-play MongoDB collections  
- Built to support 1 → ∞ documents  

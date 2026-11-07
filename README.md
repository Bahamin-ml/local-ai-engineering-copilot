# 🚀 ML Engineering Copilot

A production-grade, local, and privacy-preserving AI Desktop Copilot designed for Machine Learning Engineers, MLOps practitioners, and Python Developers. Powered by **FastAPI**, **FAISS Vector Search**, **Ollama local LLMs**, and an enterprise-styled **PyQt5** desktop interface.

---

## 🏗️ System Architecture
```text
┌────────────────────────────────────────────────────────┐
│             PyQt5 Desktop Client (UI Layer)            │
│  - Modern Slate/Blue Dark Theme                        │
│  - ChatView (Rich HTML Markdown & Code Formatting)    │
│  - Mode Switcher & Real-time Metrics (Latency, Chars) │
│  - Local SQLite Session Store (Threads & Messages)     │
└───────────────────────────┬────────────────────────────┘
│ HTTP POST (SSE Stream)
▼
┌────────────────────────────────────────────────────────┐
│             FastAPI Backend (Orchestration)            │
│  - SSE Streaming Pipeline (/api/chat/stream)           │
│  - Dynamic Role Persona & Prompt Synthesis             │
│  - Sliding Window Context Management                   │
└──────────────┬──────────────────────────┬──────────────┘
│                          │
Retrieval Query                     │ Prompt + Context Chunks
▼                          ▼
┌──────────────────────────────┐ ┌──────────────────────┐
│      FAISS Vector Store      │ │     Ollama Service   │
│  - 768-dim Index             │ │  - Embedding:        │
│  - 1,050 Indexed Chunks      │ │    nomic-embed-text  │
│  - Cosine / L2 Search        │ │  - Core Inference:   │
│  - Source Attribution        │ │    qwen3:4b          │
└──────────────────────────────┘ └──────────────────────┘
 Key Capabilities
Strictly Local & Offline-First: Fully private inference powered by Ollama; zero external telemetry or cloud leakage.
High-Performance Dense Retrieval (RAG):
Embedding Engine: nomic-embed-text:latest (768 dimensions).
Index Corpus: 1,050 curated vectors encompassing:
Python Code Bug & Fix Pairs (500 records)
Stack Overflow Curated ML Q&A (250 records)
Glaive Python Code QA Dataset (300 records)
Specialized Copilot Modes:
general_ml: ML workflows, model selection, loss functions, and evaluation metrics.
debugger: Root-cause stack trace analysis, memory leaks, CUDA out-of-memory errors.
architecture: Scalable pipeline designs, microservices, model serving patterns.
optimization: Vectorized NumPy/Pandas operations, ONNX runtime, TensorRT quantization.
explainer: Conceptual breakdown with math formulas, intuition, and reference code.
Zero-Flicker Streaming UI: Server-Sent Events (SSE) streaming directly into PyQt5 with whitespace-preserving cursor offsets and syntax highlighting.
Dual Persistence Strategy: Local SQLite thread/message database for desktop UI and sliding window in-memory state on the backend.
📋 Technology Stack
GUI Framework: PyQt5 (5.15.11) with customized QSS stylesheet.
API Framework: FastAPI, Uvicorn, Starlette, Pydantic v2.
Retrieval Engine: FAISS (Facebook AI Similarity Search), NumPy.
LLM Engine: Ollama (qwen3:4b, nomic-embed-text:latest, qwen2.5:1.5b).
Database: SQLite3.
Testing Suite: pytest, pytest-asyncio (5 comprehensive test suites, 100% passing).
⚡ Quick Start Guide
Prerequisites
OS: Windows 10/11 (64-bit).
Python: 3.10.x.
Ollama: Installed and running locally (http://127.0.0.1:11434).
Pull the required Ollama models:

bash
ollama pull nomic-embed-text:latest
ollama pull qwen3:4b
ollama pull qwen2.5:1.5b
Installation
Clone or extract the project repository:
bash
   cd "D:\resume\10 - chatbot"
   
Create and activate a virtual environment:
cmd
   python -m venv rag_env
   rag_env\Scripts\activate.bat
   
Install required dependencies:
cmd
   pip install -r requirements.txt
   
🚀 Running the Application
Option A: One-Click Launchers (Recommended)
Double-click run_backend.bat to launch the FastAPI server.
Double-click run_desktop.bat to open the PyQt5 desktop client.
Option B: Manual Terminal Execution
Terminal 1 (Backend Server):

cmd
rag_env\Scripts\activate.bat
uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 --reload
Terminal 2 (Desktop Client):

cmd
rag_env\Scripts\activate.bat
python -m desktop.main
🧪 Automated Testing & Verification
Run the full end-to-end and unit test suite:

cmd
pytest -o asyncio_mode=auto -q tests/
Test Coverage Highlights
tests/test_indexer.py: Preprocessing, chunking, and FAISS indexing pipeline.
tests/test_memory.py: Sliding context window and session lifecycle.
tests/test_rag_core.py: Vector dimensions, similarity metrics, and metadata lookups.
tests/test_api_live.py: Real-time SSE streaming protocol and health checks.
📁 Repository Structure
text
10 - chatbot/
├── backend/
│   ├── api/
│   │   ├── main.py              # FastAPI server entry point
│   │   ├── routes_chat.py       # SSE streaming endpoints & contracts
│   │   └── schemas.py           # Pydantic models for request/response
│   ├── config.py                # Centralized configuration & environment vars
│   ├── llm/
│   │   └── ollama_client.py     # Local Ollama client & streaming wrapper
│   └── rag/
│       ├── indexer.py           # Dataset ingestion & chunking logic
│       ├── preprocessor.py      # HTML cleanup & code block normalizer
│       └── vector_store.py      # FAISS vector store wrapper
├── data/
│   ├── faiss.index              # Serialized FAISS index (1,050 vectors)
│   └── metadata.json            # Document metadata store
├── desktop/
│   ├── app.py                   # PyQt5 application bootstrap
│   ├── main.py                  # Desktop runner script
│   ├── resources/
│   │   └── styles.qss           # Modern dark Slate/Blue stylesheet
│   ├── services/
│   │   ├── api_client.py        # SSE async/threaded client
│   │   └── session_store.py     # SQLite persistence for chat threads
│   └── ui/
│       ├── chat_view.py         # Custom chat viewer with HTML bubbles
│       └── main_window.py       # Main application layout & state
├── tests/                       # Automated test suites
├── requirements.txt             # Frozen dependencies
├── run_backend.bat              # Windows launcher for backend
├── run_desktop.bat              # Windows launcher for desktop client
└── README.md                    # Engineering documentation
🔒 Security & Privacy
Zero Cloud Footprint: No queries, source code snippets, or proprietary prompts leave the local machine.
Local SQLite Storage: Chat records and session indices are stored locally and support full cascading deletion.
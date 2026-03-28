# Enterprise Multi-Agent RAG Architecture

An enterprise-grade, event-driven Multi-Agent RAG (Retrieval-Augmented Generation) pipeline featuring semantic routing, Redis-based caching, asynchronous workers, and Groq-powered Generative AI.

## 🚀 System Architecture (v1.0.0 - Production Ready)

1. **API Gateway (FastAPI):** High-performance asynchronous entry point with dynamic routing and job-status polling (`/ask` and `/status/{job_id}`).
2. **Semantic Traffic Cop:** Intercepts incoming queries and mathematically categorizes user intent (Fast Search vs. Heavy Research) using local embeddings (`all-MiniLM-L6-v2`).
3. **Semantic Cache (Upstash Redis):** Hashes incoming queries and serves exact matches instantly (<30ms latency), completely bypassing the LLM layer to reduce API costs.
4. **Vector AI Brain (Qdrant):** Embeds and retrieves highly relevant semantic context from local vector databases.
5. **Asynchronous Task Queue (arq + Redis):** Heavy tasks are instantly offloaded to a background message queue, preventing API timeouts and ensuring scalability.
6. **Generative AI Agent (Groq + Llama 3.1):** Background worker utilizes custom LPUs via Groq to perform deep research and generate comprehensive Markdown reports at lightning speed.

## 🗺️ Architectural Roadmap & Audit
This project was built against a strict enterprise blueprint. Here is the current status:

* ✅ **API Gateway:** Core asynchronous routing and polling built. *(Pending: JWT Auth & Rate Limiting)*.
* ✅ **Semantic Router:** Complete. Zero-cost local routing engine live.
* 🟡 **Semantic Cache:** Live for exact-string matches. *(Pending: Upgrading to math-vector similarity matching)*.
* ✅ **Agentic Workers:** Complete. Async `arq` queue and Groq worker are fully operational. *(Pending: Expanding worker tools to include SQL and live Web Search)*.
* 🟡 **Hybrid RAG:** Vector search is live. *(Pending: Integration of Neo4j Knowledge Graphs for multi-hop queries)*.

## 🛠️ Tech Stack
* **Framework:** Python, FastAPI, Uvicorn
* **Routing & AI Embeddings:** Hugging Face `sentence-transformers` (PyTorch)
* **Vector Database:** Qdrant (Local deployment)
* **Caching & Message Queue:** Upstash Serverless Redis, `arq`
* **Generative LLM:** Groq Cloud (`llama-3.1-8b-instant`)

## 💻 Local Setup Instructions

**1. Clone the repository:**
```bash
git clone [https://github.com/YOUR_USERNAME/enterprise-multi-agent-rag.git](https://github.com/YOUR_USERNAME/enterprise-multi-agent-rag.git)
cd enterprise-multi-agent-rag
```

**2. Set up the virtual environment:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**3. Configure Environment Variables (`.env`):**
```env
UPSTASH_REDIS_URL=your_url_here
UPSTASH_REDIS_TOKEN=your_token_here
UPSTASH_REDIS_URI=rediss://default:YOUR_PASSWORD@your-endpoint.upstash.io:6379
GROQ_API_KEY=gsk_your_groq_api_key
```

**4. Start the Background Worker (Terminal 1):**
```powershell
python -m app.services.worker
```

**5. Start the API Gateway (Terminal 2):**
```powershell
uvicorn app.main:app --reload
```
Navigate to `http://127.0.0.1:8000/docs` and use the `POST /ask` endpoint!
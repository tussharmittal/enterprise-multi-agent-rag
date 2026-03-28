# Enterprise Multi-Agent RAG Architecture

An enterprise-grade, event-driven Multi-Agent RAG (Retrieval-Augmented Generation) pipeline featuring semantic routing, Redis-based caching, and asynchronous background workers for cost-optimized LLM orchestration.

## 🚀 System Architecture
Currently at **v0.5.0** (Routing & Asynchronous Processing Complete).

1. **API Gateway (FastAPI):** High-performance asynchronous entry point for user queries.
2. **Semantic Traffic Cop (SentenceTransformers):** Intercepts incoming queries and mathematically categorizes user intent (Fast Search vs. Heavy Research) using zero-cost local embeddings.
3. **Semantic Cache (Upstash Redis):** Hashes incoming queries and serves exact matches instantly (<30ms latency), bypassing the AI layer to dramatically reduce API costs.
4. **Vector AI Brain (Qdrant + SentenceTransformers):** Uses `all-MiniLM-L6-v2` locally to embed and retrieve highly relevant semantic context from real-world enterprise datasets.
5. **Asynchronous Task Queue (arq + Redis):** Heavy tasks are instantly offloaded from the main web server to a background message queue, preventing API timeouts and ensuring scalable processing.
6. **Data Pipeline (Hugging Face Datasets):** Automated ingestion of real-world business and tech news (`ag_news`) for robust testing.

## 🛠️ Tech Stack
* **Framework:** Python, FastAPI, Uvicorn
* **Routing & AI Embeddings:** Hugging Face `sentence-transformers` (PyTorch)
* **Vector Database:** Qdrant (Local deployment)
* **Caching & Message Queue:** Upstash Serverless Redis, `arq`
* **Environment:** `python-dotenv` for secure secret management

## 💻 Local Setup Instructions

**1. Clone the repository:**
```bash
git clone [https://github.com/tussharmittal/enterprise-multi-agent-rag.git](https://github.com/tussharmittal/enterprise-multi-agent-rag.git)
cd enterprise-multi-agent-rag
```

**2. Set up the virtual environment:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**3. Configure Environment Variables:**
Create a `.env` file in the root directory and add your Upstash credentials:
```env
UPSTASH_REDIS_URL=your_url_here
UPSTASH_REDIS_TOKEN=your_token_here
UPSTASH_REDIS_URI=rediss://default:YOUR_PASSWORD@your-endpoint.upstash.io:6379
```

**4. Ingest the AI Training Data:**
```powershell
python -m app.services.ingest
```

**5. Start the Background Worker (Terminal 1):**
```powershell
# Make sure your venv is active!
# Enterprise Multi-Agent RAG Architecture

An enterprise-grade, event-driven Multi-Agent RAG (Retrieval-Augmented Generation) pipeline featuring semantic routing, Redis-based caching, and asynchronous workers for cost-optimized LLM orchestration.

## 🚀 System Architecture
Currently in **Phase 2** of development. 

1. **API Gateway (FastAPI):** High-performance asynchronous entry point for user queries.
2. **Semantic Cache (Upstash Redis):** Hashes incoming queries and serves exact matches instantly (<30ms latency), completely bypassing the AI layer to save LLM API costs.
3. **Vector AI Brain (Qdrant + SentenceTransformers):** Uses `all-MiniLM-L6-v2` locally to embed and retrieve highly relevant semantic context from real-world enterprise datasets.
4. **Data Pipeline (Hugging Face Datasets):** Automated ingestion of real-world business and tech news (`ag_news`) for robust testing.

## 🛠️ Tech Stack
* **Framework:** Python, FastAPI, Uvicorn
* **Vector Database:** Qdrant (Local deployment)
* **Caching:** Upstash Serverless Redis
* **AI Embeddings:** Hugging Face `sentence-transformers`
* **Environment:** `python-dotenv` for secure secret management

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

**3. Configure Environment Variables:**
Create a `.env` file in the root directory and add your Upstash credentials:
```env
UPSTASH_REDIS_URL=your_url_here
UPSTASH_REDIS_TOKEN=your_token_here
```

**4. Ingest the AI Training Data:**
```powershell
python -m app.services.ingest
```

**5. Start the API Gateway:**
```powershell
uvicorn app.main:app --reload
```
Navigate to `http://127.0.0.1:8000/docs` to test the endpoints!
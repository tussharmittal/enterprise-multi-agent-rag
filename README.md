# Enterprise Multi-Agent RAG Architecture

An enterprise-grade, event-driven Multi-Agent RAG (Retrieval-Augmented Generation) pipeline featuring semantic routing, Redis-based caching, asynchronous workers, live web scraping, and a conversational UI.

## 🚀 System Architecture (v1.2.0)

1. **Frontend UI (Streamlit):** A conversational, Perplexity-style web interface featuring real-time session state management and background job polling.
2. **API Gateway (FastAPI):** High-performance asynchronous entry point with dynamic routing and Redis-backed Rate Limiting (`fastapi-limiter`) to prevent API abuse.
3. **Semantic Traffic Cop:** Intercepts incoming queries and mathematically categorizes user intent (Fast Search vs. Heavy Research) using local embeddings (`all-MiniLM-L6-v2`).
4. **Semantic Cache (Upstash Redis):** Hashes incoming queries and serves exact matches instantly (<30ms latency), completely bypassing the LLM layer to reduce API costs.
5. **Vector AI Brain (Qdrant):** Embeds and retrieves highly relevant semantic context from local vector databases.
6. **Asynchronous Task Queue (arq + Redis):** Heavy tasks are instantly offloaded to a background message queue, preventing API timeouts and ensuring scalability.
7. **Web-Search Agent (Groq + Llama 3.1):** Background worker utilizes custom LPUs and `duckduckgo-search` to autonomously scrape the live internet, synthesizing real-time data into comprehensive Markdown reports.

## 🗺️ Architectural Roadmap
* ✅ **API Security:** Redis-based rate limiting implemented.
* ✅ **Web-Search Agent:** Live DuckDuckGo integration complete.
* ✅ **Frontend:** Streamlit chat interface deployed.
* 🟡 **Hybrid RAG:** Vector search is live. *(Pending: Integration of Neo4j Knowledge Graphs for complex multi-hop reasoning)*.

## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **Backend Framework:** Python, FastAPI, Uvicorn
* **Routing & AI Embeddings:** Hugging Face `sentence-transformers` (PyTorch)
* **Vector Database:** Qdrant (Local deployment)
* **Caching, Security, & Queue:** Upstash Serverless Redis, `arq`, `fastapi-limiter`
* **Generative LLM:** Groq Cloud (`llama-3.1-8b-instant`)

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

**3. Configure Environment Variables (`.env`):**
```env
UPSTASH_REDIS_URL=your_url_here
UPSTASH_REDIS_TOKEN=your_token_here
UPSTASH_REDIS_URI=rediss://default:YOUR_PASSWORD@your-endpoint.upstash.io:6379
GROQ_API_KEY=gsk_your_groq_api_key
```

**4. Start the Application (Requires 3 Terminals):**

* **Terminal 1 (Background Worker):**
```powershell
python -m app.services.worker
```

* **Terminal 2 (API Gateway):**
```powershell
uvicorn app.main:app --reload
```

* **Terminal 3 (Frontend UI):**
```powershell
streamlit run app_ui.py
```
Navigate to `http://localhost:8501` to interact with your AI!

## 📊 Architecture Presentation & Video
I used NotebookLM to generate a comprehensive slide deck and video breakdown of this system's routing logic and infrastructure. 

* [📄 View the Architecture Slide Deck (PDF)](./docs/Enterprise_RAG_Architecture.pdf)
* [🎥 Watch the Architecture Walkthrough Video](./docs/Enterprise_RAG_Architecture.mp4)
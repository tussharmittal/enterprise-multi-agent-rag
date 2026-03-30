import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from arq.connections import RedisSettings
from arq.worker import Worker
from groq import AsyncGroq
from duckduckgo_search import DDGS  # <-- Our free gateway to the internet!
from tavily import TavilyClient

# Force Python to find the .env file
env_path = find_dotenv()
load_dotenv(env_path)

REDIS_URI = os.getenv("UPSTASH_REDIS_URI")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SEARCH_PROVIDER = os.getenv("SEARCH_PROVIDER", "duckduckgo")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not REDIS_URI:
    raise ValueError("🚨 Missing UPSTASH_REDIS_URI in .env file!")
if not GROQ_API_KEY:
    raise ValueError("🚨 Missing GROQ_API_KEY in .env file!")
if SEARCH_PROVIDER == "tavily" and not TAVILY_API_KEY:
    raise ValueError("🚨 Missing TAVILY_API_KEY in .env file!")

# Initialize the Groq client
groq_client = AsyncGroq(api_key=GROQ_API_KEY)

# Initialize Tavily client at module level (if configured)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY) if SEARCH_PROVIDER == "tavily" else None

def scrape_live_web(query: str, max_results: int = 3):
    """Sync function to quickly grab the top search snippets from DuckDuckGo."""
    try:
        results = DDGS().text(query, max_results=max_results)
        context = ""
        for i, res in enumerate(results):
            context += f"Source {i+1}: {res.get('title')}\nSnippet: {res.get('body')}\n\n"
        return context
    except Exception as e:
        print(f"⚠️ Search failed: {e}")
        return "No live web data available."

def scrape_live_web_tavily(query: str, max_results: int = 3):
    """Sync function to grab search results from Tavily."""
    try:
        response = tavily_client.search(query, max_results=max_results)
        context = ""
        for i, res in enumerate(response["results"]):
            context += f"Source {i+1}: {res.get('title')}\nSnippet: {res.get('content')}\n\n"
        return context
    except Exception as e:
        print(f"⚠️ Tavily search failed: {e}")
        return "No live web data available."

async def run_research_agent(ctx, query: str):
    job_id = ctx['job_id']
    print(f"\n[👷 Worker {job_id}] 📥 Picked up heavy task: '{query}'")
    
    # 1. RETRIEVE: Go to the live internet first
    print(f"[👷 Worker {job_id}] 🌐 Scraping the live web for current context (provider: {SEARCH_PROVIDER})...")
    # We use asyncio.to_thread so the synchronous search doesn't block our async worker
    if SEARCH_PROVIDER == "tavily":
        live_context = await asyncio.to_thread(scrape_live_web_tavily, query)
    else:
        live_context = await asyncio.to_thread(scrape_live_web, query)
    
    # 2. GENERATE: Pass everything to the LLM
    print(f"[👷 Worker {job_id}] 🧠 Consulting Llama 3.1 with live data...")
    try:
        chat_completion = await groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an elite enterprise research agent. "
                        "You have been provided with LIVE WEB CONTEXT. "
                        "Use this live data to write a comprehensive, accurate Markdown report answering the user's request. "
                        "If the web data is insufficient, use your general knowledge, but always prioritize the live context for recent events."
                    )
                },
                {
                    "role": "user",
                    "content": f"User Request: {query}\n\n=== LIVE WEB CONTEXT ===\n{live_context}\n========================"
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3,
        )
        
        final_report = chat_completion.choices[0].message.content
        print(f"[👷 Worker {job_id}] ✅ Research complete!")
        return final_report

    except Exception as e:
        print(f"[👷 Worker {job_id}] ❌ Error during research: {str(e)}")
        return f"Task failed: {str(e)}"

async def main():
    redis_settings = RedisSettings.from_dsn(REDIS_URI)
    worker = Worker(functions=[run_research_agent], redis_settings=redis_settings)
    
    print("🚀 Starting Web-Enabled AI Worker...")
    await worker.main()

if __name__ == "__main__":
    asyncio.run(main())
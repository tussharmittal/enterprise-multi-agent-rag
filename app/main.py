from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
import os
from dotenv import load_dotenv, find_dotenv
from arq import create_pool
from arq.connections import RedisSettings

# Import our custom services
from app.services.search import search_documents
from app.services.cache import get_cached_results, set_cached_results
from app.services.router import determine_route

# Load our environment variables
load_dotenv(find_dotenv())
REDIS_URI = os.getenv("UPSTASH_REDIS_URI")

app = FastAPI(
    title="Enterprise Multi-Agent RAG API",
    description="API Gateway for routing, caching, and processing LLM queries.",
    version="0.5.0" # Bumped to 0.5.0 for the Asynchronous Queue!
)

class QueryRequest(BaseModel):
    query: str
    limit: int = 2

# We will store our connection to the message queue here
queue_pool = None

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}

@app.post("/ask", tags=["Agentic Routing"])
async def ask_system(request: QueryRequest):
    global queue_pool
    start_time = time.time()
    
    try:
        route = determine_route(request.query)
        
        # Branch A: Heavy Research Task (Queue it!)
        if route == "heavy_research_task":
            # 1. Connect to the queue if we haven't already
            if queue_pool is None:
                queue_pool = await create_pool(RedisSettings.from_dsn(REDIS_URI))
            
            # 2. Push the job to the background worker
            job = await queue_pool.enqueue_job('run_research_agent', request.query)
            
            # Stop the stopwatch! This measures how fast the API routed and queued the task.
            process_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                "status": "accepted",
                "route_decision": route,
                "job_id": job.job_id,
                "process_time_ms": process_time,  # <-- Added consistency!
                "message": "Task queued successfully. The background worker is processing it.",
                "data": None
            }
            
        # Branch B: Fast Vector Search
        cached_data = get_cached_results(request.query)
        if cached_data:
            process_time = round((time.time() - start_time) * 1000, 2)
            return {
                "status": "success",
                "route_decision": route,
                "source": "redis_cache",
                "process_time_ms": process_time,
                "data": cached_data
            }
            
        results = search_documents(query=request.query, limit=request.limit)
        set_cached_results(query=request.query, results=results)
        
        process_time = round((time.time() - start_time) * 1000, 2)
        return {
            "status": "success",
            "route_decision": route,
            "source": "qdrant_vector_db",
            "process_time_ms": process_time,
            "data": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
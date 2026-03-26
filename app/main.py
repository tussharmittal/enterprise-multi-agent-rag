from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time

# Import our custom services
from app.services.search import search_documents
from app.services.cache import get_cached_results, set_cached_results

app = FastAPI(
    title="Enterprise Multi-Agent RAG API",
    description="API Gateway for routing, caching, and processing LLM queries.",
    version="0.3.0"
)

class QueryRequest(BaseModel):
    query: str
    limit: int = 2

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}

@app.post("/search", tags=["RAG Core"])
async def semantic_search(request: QueryRequest):
    """
    Checks Redis cache first. If cache miss, routes to Qdrant Vector DB, 
    caches the result, and returns the data.
    """
    start_time = time.time()
    
    try:
        # 1. Check the Redis Cache
        cached_data = get_cached_results(request.query)
        
        if cached_data:
            # CACHE HIT: Return instantly
            process_time = round((time.time() - start_time) * 1000, 2)
            return {
                "status": "success",
                "source": "redis_cache",
                "process_time_ms": process_time,
                "data": cached_data
            }
            
        # 2. CACHE MISS: Run the heavy AI Vector Search
        results = search_documents(query=request.query, limit=request.limit)
        
        # 3. Save the new results to Redis for the next user
        set_cached_results(query=request.query, results=results)
        
        process_time = round((time.time() - start_time) * 1000, 2)
        return {
            "status": "success",
            "source": "qdrant_vector_db",
            "process_time_ms": process_time,
            "data": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
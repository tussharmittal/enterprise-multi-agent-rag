from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time

# Import our custom services
from app.services.search import search_documents
from app.services.cache import get_cached_results, set_cached_results
from app.services.router import determine_route  # <-- Our new Traffic Cop!

app = FastAPI(
    title="Enterprise Multi-Agent RAG API",
    description="API Gateway for routing, caching, and processing LLM queries.",
    version="0.4.0" # The Multi-Agent Routing Engine
)

class QueryRequest(BaseModel):
    query: str
    limit: int = 2

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}

@app.post("/ask", tags=["Agentic Routing"])
async def ask_system(request: QueryRequest):
    """
    The main entry point. Routes the user's query to either the fast Vector DB 
    or the heavy Background Worker based on semantic intent.
    """
    start_time = time.time()
    
    try:
        # 1. Ask the Traffic Cop where this should go
        route = determine_route(request.query)
        
        # 2. Branch A: Heavy Research Task
        if route == "heavy_research_task":
            # This is our placeholder until we build the Message Queue!
            return {
                "status": "accepted",
                "route_decision": route,
                "message": "This is a complex task. It has been routed to the background research agent.",
                "data": None
            }
            
        # 3. Branch B: Fast Vector Search (The code we already built)
        # Check Cache First
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
            
        # Cache Miss -> Search Qdrant
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
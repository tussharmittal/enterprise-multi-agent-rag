from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.search import search_documents

# Initialize the FastAPI application with professional metadata
app = FastAPI(
    title="Enterprise Multi-Agent RAG API",
    description="API Gateway for routing, caching, and processing LLM queries.",
    version="0.1.0"
)

# Define the exact structure we expect from the user
class QueryRequest(BaseModel):
    query: str
    limit: int = 2  # Default to returning the top 2 matches

@app.get("/", tags=["General"])
async def root():
    """Root endpoint to verify the API is running."""
    return {"message": "Welcome to the Enterprise Multi-Agent RAG API Gateway"}

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for future container orchestration (Docker/K8s)."""
    return {"status": "healthy", "service": "api-gateway"}

@app.post("/search", tags=["RAG Core"])
async def semantic_search(request: QueryRequest):
    """
    Takes a natural language query, converts it to an embedding, 
    and retrieves relevant context from the Qdrant vector database.
    """
    try:
        # Call the search brain we built earlier!
        results = search_documents(query=request.query, limit=request.limit)
        
        return {
            "status": "success",
            "original_query": request.query,
            "data": results
        }
    except Exception as e:
        # If the database fails or the model crashes, return a clean 500 error
        raise HTTPException(status_code=500, detail=str(e))
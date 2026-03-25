from fastapi import FastAPI

# Initialize the FastAPI application with professional metadata
app = FastAPI(
    title="Enterprise Multi-Agent RAG API",
    description="API Gateway for routing, caching, and processing LLM queries.",
    version="0.1.0"
)

@app.get("/", tags=["General"])
async def root():
    """Root endpoint to verify the API is running."""
    return {"message": "Welcome to the Enterprise Multi-Agent RAG API Gateway"}

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for future container orchestration (Docker/K8s)."""
    return {"status": "healthy", "service": "api-gateway"}
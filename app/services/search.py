from sentence_transformers import SentenceTransformer
from app.services.vector_store import get_db_client, COLLECTION_NAME

# We MUST use the exact same model we used for ingestion, 
# otherwise the math won't match up in the vector space!
print("Loading embedding model...")
encoder = SentenceTransformer("all-MiniLM-L6-v2")

def search_documents(query: str, limit: int = 2):
    """Converts a user query to a vector and retrieves the most relevant documents."""
    client = get_db_client()
    
    # 1. Convert the user's question into a mathematical vector
    query_vector = encoder.encode(query).tolist()
    
    # 2. Search Qdrant using the new v1.10+ query_points API
    print(f"\n🔍 Searching for: '{query}'")
    search_response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit # How many results to bring back
    )
    search_results = search_response.points
    
    # 3. Format and return the results
    results = []
    for result in search_results:
        # result.score is the confidence/similarity metric (closer to 1.0 is better)
        formatted_result = {
            "score": round(result.score, 4),
            "text": result.payload["text"],
            "source": result.payload["source"]
        }
        results.append(formatted_result)
        
    return results

if __name__ == "__main__":
    # Let's test it with a natural language question that doesn't use exact keywords
    test_query = "What programming language do we use for the backend?"
    
    top_matches = search_documents(test_query)
    
    print("\n✅ Top Matches Found:")
    for match in top_matches:
        print(f" - [Score: {match['score']}] {match['text']}")
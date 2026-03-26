from sentence_transformers import SentenceTransformer, util
import torch

print("Loading semantic router...")
encoder = SentenceTransformer("all-MiniLM-L6-v2")

# 1. TUNED PROMPTS: Notice how we focus heavily on the verbs now!
ROUTE_PROMPTS = {
    "vector_search": [
        "What is the policy?",
        "Find the document about",
        "Retrieve information regarding",
        "Search the database for"
    ],
    "heavy_research_task": [
        "Write a comprehensive essay",
        "Generate a detailed summary report",
        "Analyze multiple sources and draft a document",
        "Compare and contrast the data into a presentation"
    ]
}

ROUTE_EMBEDDINGS = {
    route: encoder.encode(prompts, convert_to_tensor=True)
    for route, prompts in ROUTE_PROMPTS.items()
}

def determine_route(user_query: str) -> str:
    query_embedding = encoder.encode(user_query, convert_to_tensor=True)
    
    highest_score = -1.0
    winning_route = "vector_search" 
    
    print(f"\n🧠 Analyzing Query: '{user_query}'")
    
    for route_name, prompt_embeddings in ROUTE_EMBEDDINGS.items():
        cosine_scores = util.cos_sim(query_embedding, prompt_embeddings)
        max_score = round(torch.max(cosine_scores).item(), 4) # Rounding for clean reading
        
        # X-RAY VISION: Print the math for debugging
        print(f"  ↳ {route_name} match score: {max_score}")
        
        if max_score > highest_score:
            highest_score = max_score
            winning_route = route_name
            
    return winning_route

if __name__ == "__main__":
    test_queries = [
        "Do we have a hybrid work from home policy?",
        "Please write a comprehensive research paper on 2004 tech news."
    ]
    
    print("\n🚦 Testing Tuned Semantic Router...")
    for q in test_queries:
        decision = determine_route(q)
        print(f"✅ WINNER: Routed to [{decision}]\n")
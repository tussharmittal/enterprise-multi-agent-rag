from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
import uuid

# Import the database client we built earlier
from app.services.vector_store import get_db_client, COLLECTION_NAME

# Load a fast, lightweight open-source embedding model
# This runs locally on your machine, so it costs $0 in API fees!
print("Loading embedding model... (this might take a few seconds the first time)")
encoder = SentenceTransformer("all-MiniLM-L6-v2")

def ingest_documents(documents: list[str]):
    """Converts a list of text documents into embeddings and saves them to Qdrant."""
    client = get_db_client()
    
    print(f"Processing {len(documents)} documents...")
    
    # 1. Convert the text into vectors
    # encoder.encode returns a list of numerical arrays (the embeddings)
    embeddings = encoder.encode(documents)
    
    # 2. Prepare the data points for Qdrant
    points = []
    for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
        point_id = str(uuid.uuid4()) # Generate a unique ID for each document
        
        # A PointStruct contains the ID, the vector, and the raw data (payload)
        point = PointStruct(
            id=point_id,
            vector=embedding.tolist(),
            payload={"text": doc, "source": f"doc_{i}"}
        )
        points.append(point)
        
    # 3. Upload (Upsert) the data into the database
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print("✅ Documents successfully embedded and stored in Qdrant!")

if __name__ == "__main__":
    # Let's create some dummy "Enterprise Data" to test our system
    sample_company_data = [
        "The company's Q3 revenue grew by 15% due to the new cloud infrastructure product.",
        "Employees are allowed to work remotely up to 3 days a week under the new hybrid policy.",
        "The standard tech stack for backend development in the organization is Python and FastAPI.",
        "All database migrations must be reviewed by the Lead Architect before being pushed to production."
    ]
    
    ingest_documents(sample_company_data)
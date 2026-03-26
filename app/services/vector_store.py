from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import os

# Define where the local database will be saved
DB_PATH = os.path.join(os.getcwd(), "local_qdrant_data")
COLLECTION_NAME = "enterprise_docs"

# We use 384 because it is the standard dimension output for lightweight, fast open-source embedding models like 'all-MiniLM-L6-v2'
VECTOR_SIZE = 384 

def get_db_client():
    """Initializes and returns the Qdrant client."""
    client = QdrantClient(path=DB_PATH)
    return client

def setup_collection():
    """Creates the vector collection if it doesn't already exist."""
    client = get_db_client()
    
    if not client.collection_exists(collection_name=COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        print(f"✅ Collection '{COLLECTION_NAME}' created successfully.")
    else:
        print(f"⚡ Collection '{COLLECTION_NAME}' already exists. Ready to go.")

# This allows us to run this file directly to test the setup
if __name__ == "__main__":
    setup_collection()
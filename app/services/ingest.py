from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
import uuid
from datasets import load_dataset  # The new industry-standard tool
import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Import the database client we built earlier
from app.services.vector_store import get_db_client, COLLECTION_NAME

print("Loading embedding model...")
encoder = SentenceTransformer("all-MiniLM-L6-v2")

def ingest_real_data(num_docs: int = 100):
    """Fetches real-world news articles and ingests them into Qdrant."""
    client = get_db_client()
    
    print(f"📥 Downloading top {num_docs} articles from Hugging Face (ag_news)...")
    # We pull the 'train' split, but slice it so we don't download 120,000 articles at once!
    dataset = load_dataset("ag_news", split=f"train[:{num_docs}]")
    
    # Extract the raw text from the dataset
    documents = dataset['text']
    
    print(f"🧠 Embedding {len(documents)} documents. This may take 10-30 seconds on a CPU...")
    embeddings = encoder.encode(documents)
    
    # Prepare the data points for Qdrant
    points = []
    for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
        point_id = str(uuid.uuid4())
        
        # We save the text AND the label (category) as the payload
        point = PointStruct(
            id=point_id,
            vector=embedding.tolist(),
            payload={
                "text": doc, 
                "source": "HuggingFace: ag_news",
                "label": dataset['label'][i]
            }
        )
        points.append(point)
        
    # Upload (Upsert) the data into the database
    print("💾 Saving to Qdrant...")
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"✅ Successfully embedded and stored {num_docs} real-world articles!")

if __name__ == "__main__":
    # We are pulling 150 articles. You can increase this to 1000+ later, 
    # but keep it small for now so your local machine processes it quickly.
    ingest_real_data(num_docs=150)
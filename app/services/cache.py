import os
import json
import hashlib
from upstash_redis import Redis
from dotenv import load_dotenv

# Load the secret variables from the .env file
load_dotenv()

REDIS_URL = os.getenv("UPSTASH_REDIS_URL")
REDIS_TOKEN = os.getenv("UPSTASH_REDIS_TOKEN")

if not REDIS_URL or not REDIS_TOKEN:
    raise ValueError("🚨 Missing Upstash credentials in .env file!")

# Initialize the Serverless Redis client
redis_client = Redis(url=REDIS_URL, token=REDIS_TOKEN)

def generate_cache_key(query: str) -> str:
    """
    Creates a unique, consistent hash for the user's exact query.
    We hash it so that really long paragraphs don't take up massive space in Redis.
    """
    # Convert the query to lowercase and remove leading/trailing spaces for consistency
    clean_query = query.strip().lower()
    return hashlib.md5(clean_query.encode()).hexdigest()

def get_cached_results(query: str):
    """Checks if the query results are already stored in Redis."""
    cache_key = generate_cache_key(query)
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        print("⚡ CACHE HIT! Serving results instantly from Redis.")
        # Upstash returns JSON strings, so we parse it back into a Python dictionary
        return json.loads(cached_data) if isinstance(cached_data, str) else cached_data
    
    print("🐢 CACHE MISS. Routing to Vector Database...")
    return None

def set_cached_results(query: str, results: list, expiration_seconds: int = 3600):
    """Saves the Qdrant results into Redis with an expiration timer (default 1 hour)."""
    cache_key = generate_cache_key(query)
    
    # We must convert the Python list of results into a JSON string to store it
    # Passing purely positional arguments so Upstash doesn't throw a keyword error!
    redis_client.setex(cache_key, expiration_seconds, json.dumps(results))
import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from arq.connections import RedisSettings
from arq.worker import Worker  # <-- Importing the Worker directly

# Force Python to find the .env file, wherever it is!
env_path = find_dotenv()
print(f"🔍 Worker found .env file at: {env_path}")
load_dotenv(env_path)

# Grab the live-stream Redis connection
REDIS_URI = os.getenv("UPSTASH_REDIS_URI")

if not REDIS_URI:
    raise ValueError("🚨 Missing UPSTASH_REDIS_URI in .env file!")

async def run_research_agent(ctx, query: str):
    """
    This is our heavy-lifting background agent. 
    It runs completely separately from our FastAPI web server.
    """
    job_id = ctx['job_id']
    print(f"\n[👷 Worker {job_id}] 📥 Picked up heavy task: '{query}'")
    
    # Simulate a 15-second massive research task.
    print(f"[👷 Worker {job_id}] 🧠 Simulating deep research...")
    await asyncio.sleep(15) 
    
    print(f"[👷 Worker {job_id}] ✅ Research complete!")
    return f"Comprehensive summary generated for: {query}"


async def main():
    """Explicitly create and run the worker in a modern async loop."""
    redis_settings = RedisSettings.from_dsn(REDIS_URI)
    
    # Initialize the worker programmatically
    worker = Worker(
        functions=[run_research_agent],
        redis_settings=redis_settings
    )
    
    print("🚀 Starting Background AI Worker...")
    await worker.main()

if __name__ == "__main__":
    # asyncio.run() properly creates the strict event loop that modern Python requires
    asyncio.run(main())
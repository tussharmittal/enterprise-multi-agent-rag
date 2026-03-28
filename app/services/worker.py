import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from arq.connections import RedisSettings
from arq.worker import Worker
from groq import AsyncGroq  # <-- Our new LLM brain!

# Force Python to find the .env file
env_path = find_dotenv()
load_dotenv(env_path)

REDIS_URI = os.getenv("UPSTASH_REDIS_URI")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not REDIS_URI:
    raise ValueError("🚨 Missing UPSTASH_REDIS_URI in .env file!")
if not GROQ_API_KEY:
    raise ValueError("🚨 Missing GROQ_API_KEY in .env file!")

# Initialize the blazing fast Groq client
groq_client = AsyncGroq(api_key=GROQ_API_KEY)

async def run_research_agent(ctx, query: str):
    """
    This background agent takes the heavy task, sends it to Llama-3 via Groq, 
    and waits for the massive response to stream back.
    """
    job_id = ctx['job_id']
    print(f"\n[👷 Worker {job_id}] 📥 Picked up heavy task: '{query}'")
    print(f"[👷 Worker {job_id}] 🧠 Consulting Llama-3 for deep research...")
    
    try:
        # We use Llama 3 8B because it is lightning fast and brilliant at summaries
        chat_completion = await groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an elite enterprise research agent. Provide a comprehensive, well-structured Markdown report based on the user's request. Be highly analytical."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3, # Keep it professional and focused
        )
        
        # Extract the AI's response
        final_report = chat_completion.choices[0].message.content
        
        print(f"[👷 Worker {job_id}] ✅ Research complete!")
        return final_report

    except Exception as e:
        print(f"[👷 Worker {job_id}] ❌ Error during research: {str(e)}")
        return f"Task failed: {str(e)}"

async def main():
    """Explicitly create and run the worker in a modern async loop."""
    redis_settings = RedisSettings.from_dsn(REDIS_URI)
    
    worker = Worker(
        functions=[run_research_agent],
        redis_settings=redis_settings
    )
    
    print("🚀 Starting Background AI Worker with Groq Integration...")
    await worker.main()

if __name__ == "__main__":
    asyncio.run(main())
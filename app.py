from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
import os
from typing import List, Dict
import logging

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_KEY", "")
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/match")
async def match_subscribers(signal: Dict):
    try:
        # Get all active subscribers
        response = supabase.table("subscribers").select("*").eq("is_active", True).execute()
        subscribers = response.data
        
        # Get signal details
        symbol = signal.get("symbol", "").upper()
        timeframe = signal.get("timeframe", "")
        
        matched_subscribers = []
        
        for subscriber in subscribers:
            # Check if subscriber has access to this symbol and timeframe
            subscribed_symbols = subscriber.get("symbols", [])
            subscribed_timeframes = subscriber.get("timeframes", [])
            
            if (not subscribed_symbols or symbol in subscribed_symbols) and \
               (not subscribed_timeframes or timeframe in subscribed_timeframes):
                matched_subscribers.append({
                    "chat_id": subscriber["chat_id"],
                    "name": subscriber.get("name", "Unknown"),
                    "subscription_level": subscriber.get("subscription_level", "basic")
                })
        
        return {
            "matched_subscribers": matched_subscribers,
            "total_matches": len(matched_subscribers)
        }
        
    except Exception as e:
        logger.error(f"Error matching subscribers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000))) 
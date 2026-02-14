import asyncio
import aiohttp
import logging
import random
import time
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
DURATION_HOURS = 24
REQUEST_INTERVAL_SECONDS = 5 # Average time between requests
CONCURRENT_USERS = 5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("24h_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("24h_test")

async def simulate_user(user_id: int):
    async with aiohttp.ClientSession() as session:
        logger.info(f"User {user_id} started session")
        
        start_time = time.time()
        end_time = start_time + (DURATION_HOURS * 3600)
        
        request_count = 0
        error_count = 0
        
        while time.time() < end_time:
            try:
                # 1. Randomly decide action: Submit Ticket or Check Status
                action = random.choice(["submit", "status", "status", "submit"])
                
                if action == "submit":
                    payload = {
                        "name": f"Test User {user_id}",
                        "email": f"user{user_id}@example.com",
                        "subject": f"Automated Test Ticket {request_count}",
                        "message": "This is a test message to verify system stability.",
                        "category": random.choice(["general", "technical", "billing"])
                    }
                    async with session.post(f"{API_URL}/support/submit", json=payload) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            ticket_id = data.get("ticket_id")
                            logger.info(f"User {user_id}: Created ticket {ticket_id}")
                        else:
                            error_count += 1
                            logger.error(f"User {user_id}: Submit failed {resp.status}")

                elif action == "status":
                    # For simplicity, check a hardcoded ID or one we just made (complex state tracking omitted for brevity)
                    # We'll just hit health check mostly to keep load up if no ID
                    async with session.get(f"{API_URL}/health") as resp:
                         if resp.status != 200:
                            error_count += 1
                            logger.error(f"User {user_id}: Health check failed {resp.status}")

                request_count += 1
                
                # Sleep random amount
                await asyncio.sleep(random.uniform(1, REQUEST_INTERVAL_SECONDS * 2))
                
            except Exception as e:
                error_count += 1
                logger.error(f"User {user_id}: Exception {e}")
                await asyncio.sleep(5) # Backoff

        logger.info(f"User {user_id} finished. Requests: {request_count}, Errors: {error_count}")

async def main():
    logger.info(f"Starting 24-hour stability test with {CONCURRENT_USERS} users...")
    logger.info(f"Target URL: {API_URL}")
    
    tasks = []
    for i in range(CONCURRENT_USERS):
        tasks.append(simulate_user(i))
        
    await asyncio.gather(*tasks)
    logger.info("Test completed.")

if __name__ == "__main__":
    # To run this: python test_24_hour_operation.py
    # Ensure backend is running locally or port-forwarded
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")

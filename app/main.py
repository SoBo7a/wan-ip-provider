import os
import threading
import time
from .utils.env_vars import API_HOST, API_PORT, UPDATE_INTERVAL
from .database.database import init_db
from .api.api import app
from .utils.logger import logger
from .utils.ip_fetch_and_store import fetch_and_store_ips
import uvicorn

def fetch_ips_periodically():
    while True:
        fetch_and_store_ips()
        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    init_db()
        
    # Start the background task
    threading.Thread(target=fetch_ips_periodically, daemon=True).start()
        
    # Start FastAPI application using uvicorn in the same process
    uvicorn.run(app, host=API_HOST, port=API_PORT)

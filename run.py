"""Simple script to run the FastAPI application."""

import uvicorn
from config.settings import settings

if __name__ == "__main__":
    # Ensure logs directory exists
    import os
    os.makedirs("logs", exist_ok=True)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )

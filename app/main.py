"""FastAPI application entrypoint."""

import logging
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.router import Router
from app.lark_webhook import router as lark_webhook_router
from config.settings import settings
from services.scheduler import NewsScheduler

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Agent Platform",
    description="MVP AI multi-agent system",
    version="1.0.0"
)

# Include Lark webhook router
app.include_router(lark_webhook_router)

# Initialize router
router = Router()

# Initialize scheduler for automatic NewsBot runs
news_scheduler = NewsScheduler(router)


# Request/Response models
class ComplianceQueryRequest(BaseModel):
    """Request model for compliance queries."""
    question: str


class ComplianceQueryResponse(BaseModel):
    """Response model for compliance queries."""
    answer: str
    sources: list[str]
    confidence: str
    disclaimer: str
    execution_time_seconds: float


class NewsResponse(BaseModel):
    """Response model for news requests."""
    success: bool
    summary: str | None = None
    headlines_count: int | None = None
    timestamp: str
    execution_time_seconds: float
    error: str | None = None


# Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/news/run", response_model=NewsResponse)
async def run_news():
    """Trigger NewsBot manually."""
    logger.info("Received news run request")
    result = router.handle_news_request()
    return NewsResponse(**result)


@app.post("/compliance/query", response_model=ComplianceQueryResponse)
async def query_compliance(request: ComplianceQueryRequest):
    """Handle compliance query."""
    logger.info(f"Received compliance query: {request.question[:50]}...")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    result = router.handle_compliance_query(request.question)
    return ComplianceQueryResponse(**result)


@app.get("/scheduler/status")
async def scheduler_status():
    """Get scheduler status and next run time."""
    next_run = news_scheduler.get_next_run_time()
    return {
        "scheduler_running": news_scheduler.scheduler.running,
        "next_run_time": next_run.isoformat() if next_run else None,
        "timezone": "Asia/Hong_Kong"
    }


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Start scheduler when app starts."""
    news_scheduler.start()
    next_run = news_scheduler.get_next_run_time()
    logger.info(f"Scheduler started. Next NewsBot run: {next_run}")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop scheduler when app shuts down."""
    news_scheduler.stop()
    logger.info("Scheduler stopped")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )

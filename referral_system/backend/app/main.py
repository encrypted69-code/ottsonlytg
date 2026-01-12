"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from .config import settings
from .routers import admin_auth, admin_dashboard, api
from .scheduler import start_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OTT Referral System API",
    description="Complete referral and admin panel system for Telegram OTT business",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "*"],  # Allow frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin_auth.router)
app.include_router(admin_dashboard.router)
app.include_router(api.user_router)
app.include_router(api.order_router)
app.include_router(api.wallet_router)
app.include_router(api.withdrawal_router)
app.include_router(api.fraud_router)
app.include_router(api.settings_router)
app.include_router(api.referral_router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Starting OTT Referral System API...")
    
    # Start background scheduler
    scheduler = start_scheduler()
    app.state.scheduler = scheduler
    
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutting down...")
    
    # Stop scheduler
    if hasattr(app.state, 'scheduler'):
        app.state.scheduler.shutdown()
        logger.info("Scheduler stopped")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "OTT Referral System API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc) if settings.ENVIRONMENT == "development" else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )

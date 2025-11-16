from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.core.config import settings
from app.api import recordings, analysis, matches, users, auth

# Optional sentry integration
try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    logger.warning("Sentry SDK not installed. Error monitoring disabled.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events
    """
    # Startup
    logger.info("Starting Lyncsea Platform...")

    # Initialize database
    from app.core.database import init_db, check_db_connection
    if check_db_connection():
        logger.info("Database connection successful")
        init_db()
    else:
        logger.error("Database connection failed!")

    # Initialize Sentry (optional)
    if SENTRY_AVAILABLE and settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.APP_ENV,
            traces_sample_rate=0.1,
        )
        logger.info("Sentry error monitoring initialized")
    elif settings.SENTRY_DSN:
        logger.warning("Sentry DSN configured but sentry_sdk not installed")

    logger.info("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Lyncsea Platform...")
    # Cleanup tasks here


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered lead generation platform using wearable device recordings",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.api import recordings_v2, events, leads, action_items, dashboard

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(recordings_v2.router, prefix="/api/v1/recordings", tags=["Recordings"])
app.include_router(events.router, prefix="/api/v1/events", tags=["Events"])
app.include_router(leads.router, prefix="/api/v1/leads", tags=["Leads"])
app.include_router(action_items.router, prefix="/api/v1/action-items", tags=["Action Items"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(matches.router, prefix="/api/v1/matches", tags=["Matches"])


@app.get("/")
async def root():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "0.1.0",
        "environment": settings.APP_ENV,
    }


@app.get("/health")
async def health():
    """
    Detailed health check
    """
    # TODO: Add database and service health checks
    return {
        "status": "healthy",
        "services": {
            "api": "up",
            "database": "unknown",
            "neo4j": "unknown",
            "redis": "unknown",
        }
    }

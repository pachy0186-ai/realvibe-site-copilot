"""
RealVibe Site Copilot - Main FastAPI Application

AI-powered clinical trial feasibility questionnaire auto-fill SaaS
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
import os
from dotenv import load_dotenv

from app.api import auth, sites, files, questionnaires, runs, dashboard
from app.core.config import settings
from app.core.database import init_db

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="RealVibe Site Copilot API",
    description="AI-powered clinical trial feasibility questionnaire auto-fill SaaS",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(sites.router, prefix="/api/v1/sites", tags=["Sites"])
app.include_router(files.router, prefix="/api/v1/files", tags=["Files"])
app.include_router(questionnaires.router, prefix="/api/v1/questionnaires", tags=["Questionnaires"])
app.include_router(runs.router, prefix="/api/v1/runs", tags=["Runs"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    await init_db()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RealVibe Site Copilot API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "realvibe-site-copilot-api"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )


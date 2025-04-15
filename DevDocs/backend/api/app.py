"""
FastAPI application for the backend API.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .openrouter_api import router as openrouter_router
from .financial_agents_api import router as financial_router
from .ocr_test_api import router as ocr_test_router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Financial Document Processing API",
    description="API for processing financial documents using OpenRouter's Optimus Alpha model",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routers
app.include_router(openrouter_router, prefix="/api/openrouter", tags=["OpenRouter"])
app.include_router(financial_router, tags=["Financial"])
app.include_router(ocr_test_router, prefix="/api/ocr-test", tags=["OCR Test"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Financial Document Processing API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "api_key_configured": bool(os.environ.get("OPENROUTER_API_KEY"))
    }

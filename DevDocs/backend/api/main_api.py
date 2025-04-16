"""
Main API router for the backend.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

# Import API routers
from .financial_agents_api import router as financial_router
# Import other routers as needed

# Create main router
api_router = APIRouter()

# Include routers
api_router.include_router(financial_router)
# Include other routers as needed

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "API is running"
    }

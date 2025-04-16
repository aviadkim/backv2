"""
FastAPI application for the Financial Document Processor.
"""
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from financial_document_processor.api.routes import router
from financial_document_processor.database.db import Database

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Financial Document Processor",
    description="API for processing financial documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    """Create database tables on startup."""
    db = Database(os.environ.get("DATABASE_URL"))
    db.create_tables()
    db.close()

# Include API routes
app.include_router(router)

# Mount static files
uploads_dir = os.environ.get("UPLOAD_DIR", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Financial Document Processor API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

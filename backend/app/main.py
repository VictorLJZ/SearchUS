"""FastAPI main application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from app.api.search import router as search_router

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="SearchUS API",
    description="API for searching San Francisco Street View images",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Next.js default port
    "http://localhost:3001",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SearchUS API",
        "version": "1.0.0",
        "endpoints": {
            "text_search": "/api/search/text",
            "image_search": "/api/search/image",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={"status": "healthy", "service": "SearchUS API"})


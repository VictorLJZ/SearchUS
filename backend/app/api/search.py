"""Search API endpoints"""
import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel

from app.services.search_service import search_by_text_query, search_by_image_file
from app.utils.image_utils import validate_image_file, save_uploaded_file

router = APIRouter(prefix="/api/search", tags=["search"])


class TextSearchRequest(BaseModel):
    """Text search request model"""
    query: str
    top_k: Optional[int] = 10


@router.post("/text")
async def search_text(request: TextSearchRequest):
    """
    Search by text query.
    
    Request body:
    {
        "query": "urban street scene",
        "top_k": 10
    }
    """
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        result = search_by_text_query(
            query=request.query.strip(),
            top_k=request.top_k or 10
        )
        
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image")
async def search_image(file: UploadFile = File(...), top_k: int = Form(10)):
    """
    Search by image upload.
    
    Form data:
    - file: Image file (multipart/form-data)
    - top_k: Number of results (optional, default 10)
    """
    try:
        # Validate file
        if not validate_image_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an image (jpg, png, gif, webp)"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            tmp_path = tmp_file.name
            content = await file.read()
            tmp_file.write(content)
        
        try:
            # Perform search
            result = search_by_image_file(
                image_path=tmp_path,
                top_k=top_k
            )
            
            return JSONResponse(content=result)
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


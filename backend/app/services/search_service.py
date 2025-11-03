"""Search service wrapping embed/search_images.py functions"""
import os
import sys
from typing import List, Dict, Any, Optional

# Add parent directory to path to import embed module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from embed.search_images import search_by_text, search_by_image


def format_search_result(match: Any) -> Dict[str, Any]:
    """
    Format a Pinecone match result into a JSON-serializable dictionary.
    
    Args:
        match: Pinecone match object
        
    Returns:
        Formatted result dictionary
    """
    metadata = match.metadata or {}
    return {
        "filename": metadata.get("filename", "unknown"),
        "score": float(match.score),
        "lat": float(metadata.get("lat", 0)),
        "lon": float(metadata.get("lon", 0)),
        "heading": int(metadata.get("heading", 0)),
        "city": metadata.get("city", ""),
        "country": metadata.get("country", "USA"),
        "metadata": metadata
    }


def search_by_text_query(query: str, top_k: int = 10, filter_dict: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Search by text query.
    
    Args:
        query: Text search query
        top_k: Number of results to return
        filter_dict: Optional Pinecone filter dictionary
        
    Returns:
        Dictionary with results and query type
    """
    try:
        results = search_by_text(query, top_k=top_k, filter_dict=filter_dict)
        formatted_results = [format_search_result(match) for match in results.matches]
        
        return {
            "results": formatted_results,
            "query_type": "text",
            "query": query,
            "total_results": len(formatted_results)
        }
    except Exception as e:
        raise Exception(f"Error searching by text: {str(e)}")


def search_by_image_file(image_path: str, top_k: int = 10, filter_dict: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Search by image file.
    
    Args:
        image_path: Path to image file
        top_k: Number of results to return
        filter_dict: Optional Pinecone filter dictionary
        
    Returns:
        Dictionary with results and query type
    """
    try:
        results = search_by_image(image_path, top_k=top_k, filter_dict=filter_dict)
        formatted_results = [format_search_result(match) for match in results.matches]
        
        return {
            "results": formatted_results,
            "query_type": "image",
            "total_results": len(formatted_results)
        }
    except Exception as e:
        raise Exception(f"Error searching by image: {str(e)}")


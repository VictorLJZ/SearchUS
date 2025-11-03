"""Image processing utilities"""
import os
import base64
from io import BytesIO
from PIL import Image
from typing import BinaryIO


def image_to_data_uri(image_path: str) -> str:
    """
    Convert an image file to a data URI.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Data URI string
    """
    img = Image.open(image_path)
    
    # Convert RGBA to RGB if necessary (JPEG doesn't support transparency)
    if img.mode in ('RGBA', 'LA', 'P'):
        # Create a white background
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        img = rgb_img
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"


def save_uploaded_file(upload_file: BinaryIO, save_path: str) -> str:
    """
    Save an uploaded file to disk.
    
    Args:
        upload_file: File-like object from FastAPI UploadFile
        save_path: Path where to save the file
        
    Returns:
        Path to saved file
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    with open(save_path, "wb") as f:
        content = upload_file.read()
        f.write(content)
    
    return save_path


def validate_image_file(filename: str) -> bool:
    """
    Validate that the file is an image.
    
    Args:
        filename: Name of the file
        
    Returns:
        True if valid image, False otherwise
    """
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_extensions


"""
Files API routes for RealVibe Site Copilot
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List
from app.api.auth import get_current_user, TokenData

router = APIRouter()


@router.get("/")
async def get_files(current_user: TokenData = Depends(get_current_user)):
    """Get all files for the current site"""
    # TODO: Implement file listing
    return {"message": "Files endpoint - to be implemented"}


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user)
):
    """Upload a new file"""
    # TODO: Implement file upload
    return {"message": f"File upload endpoint - {file.filename} - to be implemented"}


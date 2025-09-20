"""
Files API endpoints for RealVibe Site Copilot.
Handles file upload, processing, and management.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
import asyncio

from app.services.file_service import FileService
from app.services.vector_service import VectorService
from app.api.auth import get_current_user, TokenData

router = APIRouter()

# Initialize services
file_service = FileService()
vector_service = VectorService()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user)
):
    """Upload and process a document file."""
    try:
        # Validate file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        file_content = await file.read()
        
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum size is 50MB."
            )
        
        # Upload and process file
        upload_result = await file_service.upload_file(
            file_content=file_content,
            filename=file.filename,
            site_id=current_user.site_id,
            content_type=file.content_type
        )
        
        # If not a duplicate, create embeddings
        if not upload_result.get("duplicate", False):
            # Get file content for embedding
            file_data = await file_service.get_file_content(
                upload_result["file_id"], current_user.site_id
            )
            
            if file_data and file_data.get("text_content"):
                # Process document for vector search (async)
                asyncio.create_task(
                    vector_service.process_document(
                        upload_result["file_id"],
                        file_data["text_content"]
                    )
                )
        
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "File uploaded successfully" if not upload_result.get("duplicate") else "File already exists",
                "data": upload_result
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )


@router.get("/")
async def list_files(current_user: TokenData = Depends(get_current_user)):
    """Get list of uploaded files for the site."""
    try:
        files = await file_service.get_file_list(current_user.site_id)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "files": files,
                    "total_count": len(files)
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve files: {str(e)}"
        )


@router.get("/{file_id}")
async def get_file_details(
    file_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get detailed information about a specific file."""
    try:
        file_data = await file_service.get_file_content(file_id, current_user.site_id)
        
        if not file_data:
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        # Remove sensitive data from response
        response_data = {
            "id": file_data["id"],
            "filename": file_data["filename"],
            "content_type": file_data["content_type"],
            "file_size": file_data["file_size"],
            "page_count": file_data["page_count"],
            "upload_time": file_data["upload_time"],
            "processing_status": file_data["processing_status"],
            "text_length": len(file_data.get("text_content", ""))
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": response_data
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve file details: {str(e)}"
        )


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a file and its associated data."""
    try:
        # Delete embeddings first
        await vector_service.delete_document_embeddings(file_id)
        
        # Delete file
        success = await file_service.delete_file(file_id, current_user.site_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "File deleted successfully"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )


@router.post("/search")
async def search_documents(
    query: str = Form(...),
    limit: int = Form(5),
    current_user: TokenData = Depends(get_current_user)
):
    """Search for relevant document chunks based on query."""
    try:
        if not query.strip():
            raise HTTPException(
                status_code=400,
                detail="Search query cannot be empty"
            )
        
        results = await vector_service.search_similar_chunks(
            query=query.strip(),
            site_id=current_user.site_id,
            limit=min(limit, 20)  # Cap at 20 results
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "query": query,
                    "results": results,
                    "total_found": len(results)
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/stats/embeddings")
async def get_embedding_stats(current_user: TokenData = Depends(get_current_user)):
    """Get statistics about document embeddings for the site."""
    try:
        stats = await vector_service.get_embedding_stats(current_user.site_id)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": stats
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve embedding stats: {str(e)}"
        )


@router.post("/{file_id}/reprocess")
async def reprocess_file(
    file_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Reprocess a file to regenerate embeddings."""
    try:
        # Get file content
        file_data = await file_service.get_file_content(file_id, current_user.site_id)
        
        if not file_data:
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        # Delete existing embeddings
        await vector_service.delete_document_embeddings(file_id)
        
        # Recreate embeddings
        if file_data.get("text_content"):
            processing_result = await vector_service.process_document(
                file_id,
                file_data["text_content"]
            )
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "File reprocessed successfully",
                    "data": processing_result
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="File has no text content to process"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reprocess file: {str(e)}"
        )


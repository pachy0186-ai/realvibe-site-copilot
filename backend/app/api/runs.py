"""
Runs API routes for RealVibe Site Copilot
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.api.auth import get_current_user, TokenData

router = APIRouter()


@router.get("/")
async def get_runs(current_user: TokenData = Depends(get_current_user)):
    """Get all autofill runs for the current site"""
    # TODO: Implement runs listing
    return {"message": "Runs endpoint - to be implemented"}


@router.get("/{run_id}")
async def get_run(run_id: str, current_user: TokenData = Depends(get_current_user)):
    """Get specific run details"""
    # TODO: Implement run details
    return {"message": f"Run {run_id} endpoint - to be implemented"}


"""
Sites API routes for RealVibe Site Copilot
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.site import Site, SiteCreate, SiteUpdate, SiteResponse
from app.api.auth import get_current_user, TokenData
from app.core.database import get_supabase

router = APIRouter()


@router.get("/", response_model=List[SiteResponse])
async def get_sites(current_user: TokenData = Depends(get_current_user)):
    """Get all sites (for admin) or current user's site"""
    try:
        supabase = get_supabase()
        
        # For now, return the current user's site
        response = supabase.table('sites').select('*').eq('id', current_user.site_id).execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch sites: {str(e)}"
        )


@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(site_id: str, current_user: TokenData = Depends(get_current_user)):
    """Get specific site by ID"""
    # Ensure user can only access their own site
    if site_id != current_user.site_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this site"
        )
    
    try:
        supabase = get_supabase()
        response = supabase.table('sites').select('*').eq('id', site_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site not found"
            )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch site: {str(e)}"
        )


@router.post("/", response_model=SiteResponse)
async def create_site(site: SiteCreate, current_user: TokenData = Depends(get_current_user)):
    """Create a new site"""
    try:
        supabase = get_supabase()
        
        response = supabase.table('sites').insert({
            'name': site.name
        }).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create site"
            )
        
        return response.data[0]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create site: {str(e)}"
        )


@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: str, 
    site_update: SiteUpdate, 
    current_user: TokenData = Depends(get_current_user)
):
    """Update site information"""
    # Ensure user can only update their own site
    if site_id != current_user.site_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this site"
        )
    
    try:
        supabase = get_supabase()
        
        update_data = {}
        if site_update.name is not None:
            update_data['name'] = site_update.name
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        response = supabase.table('sites').update(update_data).eq('id', site_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site not found"
            )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update site: {str(e)}"
        )


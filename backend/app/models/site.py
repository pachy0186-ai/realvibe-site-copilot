"""
Site model for RealVibe Site Copilot
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class SiteBase(BaseModel):
    """Base site model"""
    name: str = Field(..., min_length=1, max_length=255)


class SiteCreate(SiteBase):
    """Site creation model"""
    pass


class SiteUpdate(BaseModel):
    """Site update model"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class Site(SiteBase):
    """Site model with all fields"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SiteResponse(Site):
    """Site response model"""
    pass


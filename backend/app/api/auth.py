"""
Authentication API routes for RealVibe Site Copilot
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta
from app.core.config import settings

router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Login request model"""
    email: str
    password: str
    site_id: Optional[str] = None


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    site_id: str


class TokenData(BaseModel):
    """Token data model"""
    email: Optional[str] = None
    site_id: Optional[str] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        site_id: str = payload.get("site_id")
        
        if email is None or site_id is None:
            raise credentials_exception
            
        token_data = TokenData(email=email, site_id=site_id)
        
    except jwt.PyJWTError:
        raise credentials_exception
    
    return token_data


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return access token"""
    # TODO: Implement actual authentication logic with Supabase
    # For now, return a mock token for development
    
    if not request.email or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    # Mock authentication - replace with real logic
    if request.email == "demo@realvibe.ai" and request.password == "demo123":
        site_id = request.site_id or "demo-site-001"
        
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": request.email, "site_id": site_id},
            expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            expires_in=settings.access_token_expire_minutes * 60,
            site_id=site_id
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )


@router.post("/logout")
async def logout(current_user: TokenData = Depends(get_current_user)):
    """Logout user (invalidate token)"""
    # TODO: Implement token blacklisting if needed
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """Get current user information"""
    return {
        "email": current_user.email,
        "site_id": current_user.site_id
    }


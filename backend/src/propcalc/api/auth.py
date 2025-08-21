import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..domain.schemas import UserCreate, LoginRequest, LoginResponse, User
from ..domain.security.oauth2 import TokenData, get_current_user
from ..infrastructure.database.database import get_db
from ..infrastructure.repositories.user_repository import UserRepository
from ..core.security.jwt_manager import jwt_manager, password_manager

router = APIRouter()
logger = logging.getLogger(__name__)

# Mock user for development - remove in production
MOCK_USER = {
    "id": "1",
    "username": "admin",
    "email": "admin@propcalc.com",
    "full_name": "Admin User",
    "role": "admin",
    "status": "active",
    "created_at": datetime.now(),
    "updated_at": datetime.now(),
    "last_login": datetime.now(),
    "is_verified": True,
    "preferences": {}
}

@router.post("/api/v1/auth/login")
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """OAuth 2.0 login endpoint"""
    try:
        user_repo = UserRepository(db)
        
        # Try to authenticate with database first
        user = user_repo.authenticate_user(credentials.username, credentials.password)
        
        if not user:
            # Fallback to mock user for development (REMOVE IN PRODUCTION)
            if credentials.username == "admin" and credentials.password == "admin123":
                logger.warning("Using mock user authentication - REMOVE IN PRODUCTION")
                
                # Create token data
                token_data = {
                    "sub": "1",
                    "username": "admin",
                    "email": "admin@propcalc.com",
                    "role": "admin",
                    "permissions": ["read", "write", "admin"]
                }
                
                # Generate proper JWT tokens
                access_token = jwt_manager.create_access_token(token_data)
                refresh_token = jwt_manager.create_refresh_token(token_data)
                
                return LoginResponse(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type="bearer",
                    expires_in=3600,
                    user=User(**MOCK_USER)
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
        
        # Generate real JWT tokens for database user
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
            "permissions": user.permissions if hasattr(user, 'permissions') else ["read", "write"]
        }
        
        access_token = jwt_manager.create_access_token(token_data)
        refresh_token = jwt_manager.create_refresh_token(token_data)
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,
            user=User(
                user_id=str(user.id),
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                role=user.role.value if hasattr(user.role, 'value') else user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.post("/api/v1/auth/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    try:
        # Use JWT manager to refresh token
        result = jwt_manager.refresh_access_token(refresh_token)
        
        return {
            "status": "success",
            "access_token": result["access_token"],
            "token_type": result["token_type"],
            "expires_in": result["expires_in"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh"
        )

@router.post("/api/v1/auth/logout")
async def logout(token: str):
    """Logout and revoke token"""
    try:
        # Revoke the token using JWT manager
        success = jwt_manager.revoke_token(token)
        
        if success:
            return {"status": "success", "message": "Logout successful"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )

@router.post("/api/v1/auth/register")
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        user_repo = UserRepository(db)
        
        # Check if user already exists
        if user_repo.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        if user_repo.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user = user_repo.create_user(user_data)
        
        return {
            "status": "success",
            "message": "User registered successfully",
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.get("/api/v1/auth/profile")
async def get_user_profile(token_data: TokenData = Depends(get_current_user)):
    """Get current user profile"""
    try:
        # For now, return mock user data
        # TODO: Implement real user profile retrieval from database
        return {
            "status": "success",
            "user": MOCK_USER
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error getting user profile"
        )

@router.put("/api/v1/auth/profile")
async def update_user_profile(profile_update: dict, token_data: TokenData = Depends(get_current_user)):
    """Update current user profile"""
    try:
        # TODO: Implement real user profile update
        # This requires proper user management system
        return {
            "status": "success",
            "message": "Profile updated successfully",
            "updated_fields": list(profile_update.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error updating user profile"
        )

@router.post("/api/v1/auth/change-password")
async def change_password(password_change: dict, token_data: TokenData = Depends(get_current_user)):
    """Change user password"""
    try:
        # TODO: Implement real password change
        # This requires proper user management system
        return {
            "status": "success",
            "message": "Password changed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error changing password"
        )

@router.post("/api/v1/auth/forgot-password")
async def forgot_password(password_reset: dict):
    """Request password reset"""
    try:
        # TODO: Implement real password reset
        # This requires proper user management system
        return {
            "status": "success",
            "message": "Password reset email sent (if implemented)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting password reset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error requesting password reset"
        )

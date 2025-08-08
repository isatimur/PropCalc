import logging

from fastapi import APIRouter, Depends, HTTPException

from ..domain.schemas import PasswordChange, PasswordReset, UserCreate
from ..domain.security.oauth2 import TokenData, auth_manager, get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/api/v1/auth/login")
async def login(credentials: dict):
    """OAuth 2.0 login endpoint"""
    try:
        # Mock user authentication (in production, verify against database)
        user_data = {
            "sub": "user_123",
            "email": credentials.get("email"),
            "role": "user",
            "permissions": ["read", "write"]
        }

        # Create tokens using the auth manager
        access_token = auth_manager._create_access_token(user_data)
        refresh_token = auth_manager._create_refresh_token(user_data["sub"])

        return {
            "status": "success",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800  # 30 minutes
        }

    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.post("/api/v1/auth/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    try:
        # Verify refresh token
        token_data = auth_manager._decode_token(refresh_token)

        # Create new access token
        user_data = {
            "sub": token_data.user_id,
            "email": token_data.email,
            "role": token_data.role.value,
            "permissions": token_data.permissions
        }

        new_access_token = auth_manager._create_access_token(user_data)

        return {
            "status": "success",
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 1800
        }

    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/api/v1/auth/logout")
async def logout(token: str):
    """Logout and revoke token"""
    try:
        success = await auth_manager.logout(token)

        if success:
            return {"status": "success", "message": "Token revoked successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to revoke token")

    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=400, detail="Logout failed")

@router.post("/api/v1/auth/register")
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        oauth_manager = get_oauth_manager()

        # Check if user already exists
        existing_user = oauth_manager.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")

        # Create new user
        user_id = oauth_manager.create_user(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            password=user_data.password,
            role=user_data.role.value
        )

        # Create tokens for immediate login
        user_info = {
            "sub": user_id,
            "email": user_data.email,
            "role": user_data.role.value,
            "permissions": oauth_manager.get_user_role_permissions(user_data.role.value)
        }

        access_token = oauth_manager.create_access_token(user_info)
        refresh_token = oauth_manager.create_refresh_token(user_info)

        return {
            "status": "success",
            "message": "User registered successfully",
            "user_id": user_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.get("/api/v1/auth/profile")
async def get_user_profile(token_data: TokenData = Depends(get_current_user)):
    """Get current user profile"""
    try:
        oauth_manager = get_oauth_manager()
        user = oauth_manager.get_user_by_id(token_data.user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "status": "success",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "last_login": user.last_login
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@router.put("/api/v1/auth/profile")
async def update_user_profile(profile_update: dict, token_data: TokenData = Depends(get_current_user)):
    """Update current user profile"""
    try:
        oauth_manager = get_oauth_manager()
        success = oauth_manager.update_user_profile(token_data.user_id, profile_update)

        if success:
            return {"status": "success", "message": "Profile updated successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to update profile")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

@router.post("/api/v1/auth/change-password")
async def change_password(password_change: PasswordChange, token_data: TokenData = Depends(get_current_user)):
    """Change user password"""
    try:
        oauth_manager = get_oauth_manager()
        success = oauth_manager.change_user_password(
            token_data.user_id,
            password_change.current_password,
            password_change.new_password
        )

        if success:
            return {"status": "success", "message": "Password changed successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to change password")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(status_code=500, detail="Failed to change password")

@router.post("/api/v1/auth/forgot-password")
async def forgot_password(password_reset: PasswordReset):
    """Request password reset"""
    try:
        oauth_manager = get_oauth_manager()
        success = oauth_manager.request_password_reset(password_reset.email)

        if success:
            return {"status": "success", "message": "Password reset email sent"}
        else:
            raise HTTPException(status_code=400, detail="Failed to send reset email")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting password reset: {e}")
        raise HTTPException(status_code=500, detail="Failed to request password reset")

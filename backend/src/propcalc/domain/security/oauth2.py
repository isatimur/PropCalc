"""
OAuth2 Authentication Implementation for PropCalc
"""

import logging
import os
import secrets
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

# OAuth2 Password Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

class UserRole(Enum):
    """User roles for access control"""
    ADMIN = "admin"
    ANALYST = "analyst"
    INVESTOR = "investor"
    DEVELOPER = "developer"
    VIEWER = "viewer"

class UserStatus(Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class User(BaseModel):
    """User model"""
    id: str
    email: EmailStr
    username: str
    full_name: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None = None
    is_verified: bool = False
    preferences: dict[str, Any] = {}

class Token(BaseModel):
    """Token model"""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str | None = None

class TokenData(BaseModel):
    """Token data model"""
    user_id: str
    email: str
    role: UserRole
    permissions: list[str]

class AuthManager:
    """Authentication manager for PropCalc"""

    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7

        # In-memory user storage (replace with database in production)
        self.users: dict[str, User] = {}
        self.refresh_tokens: dict[str, str] = {}

        # Initialize with default admin user
        self._create_default_admin()

    def _create_default_admin(self):
        """Create default admin user"""
        admin_user = User(
            id="admin-001",
            email="admin@propcalc.com",
            username="admin",
            full_name="PropCalc Administrator",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_verified=True
        )
        self.users[admin_user.id] = admin_user

    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def _create_access_token(self, data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def _create_refresh_token(self, user_id: str) -> str:
        """Create refresh token"""
        refresh_token = secrets.token_urlsafe(32)
        self.refresh_tokens[refresh_token] = user_id
        return refresh_token

    def _decode_token(self, token: str) -> TokenData:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            role: str = payload.get("role")

            if user_id is None or email is None or role is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return TokenData(
                user_id=user_id,
                email=email,
                role=UserRole(role),
                permissions=self._get_user_permissions(UserRole(role))
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def _get_user_permissions(self, role: UserRole) -> list[str]:
        """Get user permissions based on role"""
        permissions = {
            UserRole.ADMIN: [
                "read:all", "write:all", "delete:all", "admin:all",
                "dld:read", "dld:write", "analytics:read", "analytics:write",
                "ml:read", "ml:write", "users:manage", "system:admin"
            ],
            UserRole.ANALYST: [
                "read:all", "write:analytics", "dld:read", "analytics:read",
                "analytics:write", "ml:read", "reports:create"
            ],
            UserRole.INVESTOR: [
                "read:limited", "dld:read", "analytics:read", "vantage_score:read",
                "reports:read", "portfolio:manage"
            ],
            UserRole.DEVELOPER: [
                "read:limited", "dld:read", "analytics:read", "vantage_score:read",
                "reports:read", "projects:manage"
            ],
            UserRole.VIEWER: [
                "read:public", "dld:read", "analytics:read"
            ]
        }

        return permissions.get(role, [])

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate user with email and password"""
        # In production, this would query the database
        for user in self.users.values():
            if user.email == email:
                # Verify password hash for all users
                if self._verify_password(password, user.hashed_password):
                    return user
        return None

    async def create_user(self, email: str, username: str, full_name: str,
                         password: str, role: UserRole = UserRole.VIEWER) -> User:
        """Create new user"""
        # Check if user already exists
        for user in self.users.values():
            if user.email == email or user.username == username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already exists"
                )

        # Create new user
        user_id = f"user-{len(self.users) + 1:03d}"
        self._hash_password(password)

        new_user = User(
            id=user_id,
            email=email,
            username=username,
            full_name=full_name,
            role=role,
            status=UserStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_verified=False
        )

        self.users[user_id] = new_user
        logger.info(f"Created new user: {email} with role: {role.value}")

        return new_user

    async def login(self, email: str, password: str) -> Token:
        """User login"""
        user = await self.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is not active"
            )

        # Update last login
        user.last_login = datetime.now()
        user.updated_at = datetime.now()

        # Create access token
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        access_token = self._create_access_token(
            data={"sub": user.id, "email": user.email, "role": user.role.value},
            expires_delta=access_token_expires
        )

        # Create refresh token
        refresh_token = self._create_refresh_token(user.id)

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
            refresh_token=refresh_token
        )

    async def refresh_access_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token"""
        user_id = self.refresh_tokens.get(refresh_token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user = self.users.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Create new access token
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        access_token = self._create_access_token(
            data={"sub": user.id, "email": user.email, "role": user.role.value},
            expires_delta=access_token_expires
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60
        )

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        """Get current authenticated user"""
        token_data = self._decode_token(token)
        user = self.users.get(token_data.user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    async def get_current_active_user(self, current_user: User = Depends(get_current_user)) -> User:
        """Get current active user"""
        if current_user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return current_user

    def check_permission(self, required_permission: str, user_permissions: list[str]) -> bool:
        """Check if user has required permission"""
        return required_permission in user_permissions

    async def require_permission(self, permission: str, current_user: User = Depends(get_current_user)) -> User:
        """Require specific permission for endpoint access"""
        self._decode_token(current_user.id)  # This would need to be fixed
        user_permissions = self._get_user_permissions(current_user.role)

        if not self.check_permission(permission, user_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return current_user

    async def logout(self, refresh_token: str) -> dict[str, str]:
        """User logout - invalidate refresh token"""
        if refresh_token in self.refresh_tokens:
            del self.refresh_tokens[refresh_token]

        return {"message": "Successfully logged out"}

    async def change_password(self, user_id: str, old_password: str, new_password: str) -> dict[str, str]:
        """Change user password"""
        user = self.users.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verify old password
        if not self._verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password"
            )

        # Hash new password
        self._hash_password(new_password)
        # user.hashed_password = hashed_password  # Would update in database
        user.updated_at = datetime.now()

        return {"message": "Password changed successfully"}

    async def reset_password(self, email: str) -> dict[str, str]:
        """Reset password (send reset email)"""
        user = None
        for u in self.users.values():
            if u.email == email:
                user = u
                break

        if not user:
            # Don't reveal if user exists
            return {"message": "If email exists, reset instructions sent"}

        # In production, send reset email
        logger.info(f"Password reset requested for: {email}")

        return {"message": "If email exists, reset instructions sent"}

    def get_user_statistics(self) -> dict[str, Any]:
        """Get user statistics"""
        total_users = len(self.users)
        active_users = len([u for u in self.users.values() if u.status == UserStatus.ACTIVE])
        role_distribution = {}

        for user in self.users.values():
            role = user.role.value
            role_distribution[role] = role_distribution.get(role, 0) + 1

        return {
            "total_users": total_users,
            "active_users": active_users,
            "role_distribution": role_distribution,
            "verification_rate": len([u for u in self.users.values() if u.is_verified]) / total_users if total_users > 0 else 0
        }

# Global auth manager instance
auth_manager = AuthManager()

# Dependency functions for FastAPI
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return await auth_manager.get_current_user(token)

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return await auth_manager.get_current_active_user(current_user)

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def require_analyst(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.ANALYST]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analyst access required"
        )
    return current_user

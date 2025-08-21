"""
JWT Token Manager for PropCalc
Handles token creation, validation, and refresh
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from ...config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


class JWTManager:
    """Manages JWT token operations"""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a new access token"""
        try:
            to_encode = data.copy()
            
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
            to_encode.update({"exp": expire, "iat": datetime.utcnow()})
            
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Access token created for user: {data.get('sub', 'unknown')}")
            
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create access token"
            )
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a new refresh token with longer expiration"""
        try:
            to_encode = data.copy()
            # Refresh tokens last 7 days
            expire = datetime.utcnow() + timedelta(days=7)
            
            to_encode.update({
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "refresh"
            })
            
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Refresh token created for user: {data.get('sub', 'unknown')}")
            
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create refresh token"
            )
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type for refresh tokens
            if token_type == "refresh" and payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has no expiration"
                )
            
            if datetime.utcnow() > datetime.fromtimestamp(exp):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            # Check if token is issued in the future (clock skew protection)
            iat = payload.get("iat")
            if iat and datetime.utcnow() < datetime.fromtimestamp(iat) - timedelta(minutes=5):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token issued in the future"
                )
            
            logger.info(f"Token verified for user: {payload.get('sub', 'unknown')}")
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token verification failed"
            )
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an access token using a valid refresh token"""
        try:
            # Verify refresh token
            payload = self.verify_token(refresh_token, token_type="refresh")
            
            # Create new access token
            user_data = {
                "sub": payload.get("sub"),
                "username": payload.get("username"),
                "email": payload.get("email"),
                "role": payload.get("role"),
                "permissions": payload.get("permissions", [])
            }
            
            new_access_token = self.create_access_token(user_data)
            
            logger.info(f"Access token refreshed for user: {payload.get('sub', 'unknown')}")
            
            return {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to refresh access token"
            )
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a token (add to blacklist)"""
        try:
            # In a production system, you would add this token to a blacklist
            # For now, we'll just log the revocation
            payload = self.verify_token(token)
            logger.info(f"Token revoked for user: {payload.get('sub', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False


class PasswordManager:
    """Manages password operations"""
    
    def __init__(self):
        self.pwd_context = pwd_context
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Password hashing error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to hash password"
            )
    
    def validate_password_strength(self, password: str) -> bool:
        """Validate password strength"""
        if len(password) < 8:
            return False
        
        if not any(c.isupper() for c in password):
            return False
        
        if not any(c.islower() for c in password):
            return False
        
        if not any(c.isdigit() for c in password):
            return False
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False
        
        return True


# Global instances
jwt_manager = JWTManager()
password_manager = PasswordManager()

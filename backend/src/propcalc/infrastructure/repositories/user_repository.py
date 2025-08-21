"""
User repository for database operations
"""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uuid

from ..database.models import User, UserSession, UserActivity, UserRoleEnum, UserStatusEnum
from ...domain.schemas import UserCreate, UserUpdate


class UserRepository:
    """Repository for user-related database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # For now, use a simple hash - in production use proper password hashing
        hashed_password = f"hashed_{user_data.password}"
        
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role,
            status=UserStatusEnum.PENDING_VERIFICATION,
            is_active=True,
            email_verified=False
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_uuid(self, user_uuid: str) -> Optional[User]:
        """Get user by UUID"""
        return self.db.query(User).filter(User.uuid == user_uuid).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password"""
        user = self.get_user_by_username(username)
        if not user:
            user = self.get_user_by_email(username)
        
        if not user or not user.is_active:
            return None
        
        # Simple password verification for now
        if user.hashed_password != f"hashed_{password}":
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        """Change user password"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # For now, use a simple hash - in production use proper password hashing
        user.hashed_password = f"hashed_{new_password}"
        user.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def create_session(self, user_id: int, session_token: str, refresh_token: str, 
                      expires_at: datetime, ip_address: str = None, user_agent: str = None) -> UserSession:
        """Create a new user session"""
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def get_session_by_token(self, session_token: str) -> Optional[UserSession]:
        """Get session by session token"""
        return self.db.query(UserSession).filter(
            and_(
                UserSession.session_token == session_token,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
        ).first()
    
    def get_session_by_refresh_token(self, refresh_token: str) -> Optional[UserSession]:
        """Get session by refresh token"""
        return self.db.query(UserSession).filter(
            and_(
                UserSession.refresh_token == refresh_token,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
        ).first()
    
    def deactivate_session(self, session_token: str) -> bool:
        """Deactivate a session (logout)"""
        session = self.get_session_by_token(session_token)
        if not session:
            return False
        
        session.is_active = False
        session.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def deactivate_all_user_sessions(self, user_id: int) -> bool:
        """Deactivate all sessions for a user"""
        sessions = self.db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        ).all()
        
        for session in sessions:
            session.is_active = False
            session.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        expired_sessions = self.db.query(UserSession).filter(
            UserSession.expires_at <= datetime.utcnow()
        ).all()
        
        count = len(expired_sessions)
        for session in expired_sessions:
            self.db.delete(session)
        
        self.db.commit()
        return count
    
    def log_user_activity(self, user_id: int, activity_type: str, description: str = None,
                         ip_address: str = None, user_agent: str = None, metadata: dict = None) -> UserActivity:
        """Log user activity"""
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata
        )
        
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        
        return activity
    
    def get_user_activities(self, user_id: int, limit: int = 100) -> List[UserActivity]:
        """Get user activities"""
        return self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).order_by(UserActivity.created_at.desc()).limit(limit).all()
    
    def verify_email(self, token: str) -> bool:
        """Verify user email with verification token"""
        user = self.db.query(User).filter(
            and_(
                User.email_verification_token == token,
                User.email_verified == False
            )
        ).first()
        
        if not user:
            return False
        
        user.email_verified = True
        user.status = UserStatusEnum.ACTIVE
        user.email_verification_token = None
        user.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def request_password_reset(self, email: str) -> Optional[str]:
        """Request password reset and return reset token"""
        user = self.get_user_by_email(email)
        if not user or not user.is_active:
            return None
        
        # Generate reset token
        reset_token = str(uuid.uuid4())
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
        user.updated_at = datetime.utcnow()
        self.db.commit()
        
        return reset_token
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using reset token"""
        user = self.db.query(User).filter(
            and_(
                User.password_reset_token == token,
                User.password_reset_expires > datetime.utcnow()
            )
        ).first()
        
        if not user:
            return False
        
        # For now, use a simple hash - in production use proper password hashing
        user.hashed_password = f"hashed_{new_password}"
        user.password_reset_token = None
        user.password_reset_expires = None
        user.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def get_users_by_role(self, role: UserRoleEnum, limit: int = 100) -> List[User]:
        """Get users by role"""
        return self.db.query(User).filter(
            and_(
                User.role == role,
                User.is_active == True
            )
        ).limit(limit).all()
    
    def get_active_users_count(self) -> int:
        """Get count of active users"""
        return self.db.query(User).filter(User.is_active == True).count()
    
    def search_users(self, query: str, limit: int = 50) -> List[User]:
        """Search users by username, email, or full name"""
        return self.db.query(User).filter(
            and_(
                User.is_active == True,
                or_(
                    User.username.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                    User.full_name.ilike(f"%{query}%")
                )
            )
        ).limit(limit).all()

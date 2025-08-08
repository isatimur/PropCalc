"""
Base repository pattern for PropCalc
Modern SQLAlchemy repository with async support
"""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any, Union
from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

from ..database.models import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """Base repository with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get a single record by ID"""
        return db.query(self.model).filter(self.model.id == id).first()
    
    async def get_async(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Get a single record by ID (async)"""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none()
    
    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination and filtering"""
        query = db.query(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        return query.offset(skip).limit(limit).all()
    
    async def get_multi_async(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination and filtering (async)"""
        query = select(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record"""
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    async def create_async(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record (async)"""
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    def update(
        self, 
        db: Session, 
        *, 
        db_obj: ModelType, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record"""
        obj_data = db_obj.__dict__
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    async def update_async(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: ModelType, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record (async)"""
        obj_data = db_obj.__dict__
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: int) -> ModelType:
        """Delete a record"""
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
    
    async def remove_async(self, db: AsyncSession, *, id: int) -> ModelType:
        """Delete a record (async)"""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        obj = result.scalar_one_or_none()
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj
    
    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering"""
        query = db.query(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        return query.count()
    
    async def count_async(self, db: AsyncSession, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering (async)"""
        query = select(func.count(self.model.id))
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        result = await db.execute(query)
        return result.scalar()
    
    def exists(self, db: Session, id: Any) -> bool:
        """Check if a record exists"""
        return db.query(self.model).filter(self.model.id == id).first() is not None
    
    async def exists_async(self, db: AsyncSession, id: Any) -> bool:
        """Check if a record exists (async)"""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none() is not None
    
    def bulk_create(self, db: Session, *, objs_in: List[CreateSchemaType]) -> List[ModelType]:
        """Create multiple records in bulk"""
        db_objs = []
        for obj_in in objs_in:
            obj_data = obj_in.model_dump()
            db_obj = self.model(**obj_data)
            db_objs.append(db_obj)
        
        db.add_all(db_objs)
        db.commit()
        
        for db_obj in db_objs:
            db.refresh(db_obj)
        
        return db_objs
    
    async def bulk_create_async(self, db: AsyncSession, *, objs_in: List[CreateSchemaType]) -> List[ModelType]:
        """Create multiple records in bulk (async)"""
        db_objs = []
        for obj_in in objs_in:
            obj_data = obj_in.model_dump()
            db_obj = self.model(**obj_data)
            db_objs.append(db_obj)
        
        db.add_all(db_objs)
        await db.commit()
        
        for db_obj in db_objs:
            await db.refresh(db_obj)
        
        return db_objs
    
    def bulk_update(self, db: Session, *, objs_in: List[ModelType]) -> List[ModelType]:
        """Update multiple records in bulk"""
        for obj in objs_in:
            db.add(obj)
        db.commit()
        
        for obj in objs_in:
            db.refresh(obj)
        
        return objs_in
    
    async def bulk_update_async(self, db: AsyncSession, *, objs_in: List[ModelType]) -> List[ModelType]:
        """Update multiple records in bulk (async)"""
        for obj in objs_in:
            db.add(obj)
        await db.commit()
        
        for obj in objs_in:
            await db.refresh(obj)
        
        return objs_in


class CRUDRepository(BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]):
    """CRUD repository with additional convenience methods"""
    
    def get_by_field(self, db: Session, field: str, value: Any) -> Optional[ModelType]:
        """Get a record by a specific field"""
        if hasattr(self.model, field):
            return db.query(self.model).filter(getattr(self.model, field) == value).first()
        return None
    
    async def get_by_field_async(self, db: AsyncSession, field: str, value: Any) -> Optional[ModelType]:
        """Get a record by a specific field (async)"""
        if hasattr(self.model, field):
            result = await db.execute(
                select(self.model).filter(getattr(self.model, field) == value)
            )
            return result.scalar_one_or_none()
        return None
    
    def get_or_create(
        self, 
        db: Session, 
        *, 
        defaults: Optional[Dict[str, Any]] = None, 
        **kwargs
    ) -> tuple[ModelType, bool]:
        """Get a record or create it if it doesn't exist"""
        obj = db.query(self.model).filter_by(**kwargs).first()
        if obj:
            return obj, False
        
        if defaults:
            kwargs.update(defaults)
        
        obj = self.model(**kwargs)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj, True
    
    async def get_or_create_async(
        self, 
        db: AsyncSession, 
        *, 
        defaults: Optional[Dict[str, Any]] = None, 
        **kwargs
    ) -> tuple[ModelType, bool]:
        """Get a record or create it if it doesn't exist (async)"""
        result = await db.execute(select(self.model).filter_by(**kwargs))
        obj = result.scalar_one_or_none()
        
        if obj:
            return obj, False
        
        if defaults:
            kwargs.update(defaults)
        
        obj = self.model(**kwargs)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj, True
    
    def update_or_create(
        self, 
        db: Session, 
        *, 
        defaults: Optional[Dict[str, Any]] = None, 
        **kwargs
    ) -> tuple[ModelType, bool]:
        """Update a record or create it if it doesn't exist"""
        obj = db.query(self.model).filter_by(**kwargs).first()
        if obj:
            if defaults:
                for field, value in defaults.items():
                    setattr(obj, field, value)
                db.add(obj)
                db.commit()
                db.refresh(obj)
            return obj, False
        
        if defaults:
            kwargs.update(defaults)
        
        obj = self.model(**kwargs)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj, True
    
    async def update_or_create_async(
        self, 
        db: AsyncSession, 
        *, 
        defaults: Optional[Dict[str, Any]] = None, 
        **kwargs
    ) -> tuple[ModelType, bool]:
        """Update a record or create it if it doesn't exist (async)"""
        result = await db.execute(select(self.model).filter_by(**kwargs))
        obj = result.scalar_one_or_none()
        
        if obj:
            if defaults:
                for field, value in defaults.items():
                    setattr(obj, field, value)
                db.add(obj)
                await db.commit()
                await db.refresh(obj)
            return obj, False
        
        if defaults:
            kwargs.update(defaults)
        
        obj = self.model(**kwargs)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj, True 
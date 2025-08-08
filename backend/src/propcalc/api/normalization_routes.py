"""
PropCalc Address Normalization API Routes
Provides access to normalization lookup tables and statistics
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from ..core.normalization_lookup import normalization_lookup
from ..domain.security.oauth2 import User, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/normalization", tags=["normalization"])

@router.get("/demo")
async def get_normalization_demo() -> dict:
    """
    Public demo endpoint for normalization lookup (no authentication required)

    Returns:
        Dictionary with demo normalization examples
    """
    try:
        # Demo examples
        demo_examples = {
            "area_normalization": {
                "Marsa Dubai": normalization_lookup.normalize_area("Marsa Dubai"),
                "Burj Khalifa": normalization_lookup.normalize_area("Burj Khalifa"),
                "Palm Jumeirah": normalization_lookup.normalize_area("Palm Jumeirah"),
                "Business Bay": normalization_lookup.normalize_area("Business Bay")
            },
            "property_type_normalization": {
                "Unit": normalization_lookup.normalize_property_type("Unit"),
                "Land": normalization_lookup.normalize_property_type("Land"),
                "Building": normalization_lookup.normalize_property_type("Building"),
                "Apartment": normalization_lookup.normalize_property_type("Apartment")
            },
            "developer_normalization": {
                "Emaar": normalization_lookup.normalize_developer("Emaar"),
                "DAMAC": normalization_lookup.normalize_developer("DAMAC"),
                "Nakheel": normalization_lookup.normalize_developer("Nakheel")
            },
            "project_normalization": {
                "Marina Heights": normalization_lookup.normalize_project("Marina Heights"),
                "Palm Vista Villa": normalization_lookup.normalize_project("Palm Vista Villa"),
                "Downtown Tower": normalization_lookup.normalize_project("Downtown Tower")
            }
        }

        # Get statistics
        stats = normalization_lookup.get_normalization_stats()

        return {
            "status": "success",
            "message": "Normalization lookup demo",
            "data": {
                "demo_examples": demo_examples,
                "statistics": stats
            }
        }

    except Exception as e:
        logger.error(f"Error in normalization demo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get normalization demo: {str(e)}")

@router.get("/stats")
async def get_normalization_stats(
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get normalization statistics and overview

    Returns:
        Dictionary with normalization statistics
    """
    try:
        stats = normalization_lookup.get_normalization_stats()

        return {
            "status": "success",
            "data": stats,
            "message": "Normalization statistics retrieved successfully"
        }

    except Exception as e:
        logger.error(f"Error getting normalization stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get normalization stats: {str(e)}")

@router.get("/area-mapping")
async def get_area_mapping(
    search: str | None = Query(None, description="Search in area names"),
    category: str | None = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get area name mapping from DLD to normalized names

    Args:
        search: Optional search term to filter areas
        category: Optional category filter
        current_user: Authenticated user

    Returns:
        Dictionary with area mapping data
    """
    try:
        mapping = normalization_lookup.area_mapping

        # Apply filters
        if search:
            search_lower = search.lower()
            mapping = {
                k: v for k, v in mapping.items()
                if search_lower in k.lower() or search_lower in v.normalized_value.lower()
            }

        if category:
            mapping = {
                k: v for k, v in mapping.items()
                if v.category.lower() == category.lower()
            }

        # Convert to response format
        area_data = []
        for dld_name, entry in mapping.items():
            area_data.append({
                "dld_name": dld_name,
                "normalized_name": entry.normalized_value,
                "category": entry.category,
                "confidence": entry.confidence,
                "notes": entry.notes
            })

        return {
            "status": "success",
            "data": {
                "areas": area_data,
                "total_count": len(area_data)
            },
            "message": "Area mapping retrieved successfully"
        }

    except Exception as e:
        logger.error(f"Error getting area mapping: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get area mapping: {str(e)}")

@router.get("/property-type-mapping")
async def get_property_type_mapping(
    search: str | None = Query(None, description="Search in property types"),
    category: str | None = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get property type mapping from DLD to normalized types

    Args:
        search: Optional search term to filter property types
        category: Optional category filter
        current_user: Authenticated user

    Returns:
        Dictionary with property type mapping data
    """
    try:
        mapping = normalization_lookup.property_type_mapping

        # Apply filters
        if search:
            search_lower = search.lower()
            mapping = {
                k: v for k, v in mapping.items()
                if search_lower in k.lower() or search_lower in v.normalized_value.lower()
            }

        if category:
            mapping = {
                k: v for k, v in mapping.items()
                if v.category.lower() == category.lower()
            }

        # Convert to response format
        property_type_data = []
        for dld_type, entry in mapping.items():
            property_type_data.append({
                "dld_type": dld_type,
                "normalized_type": entry.normalized_value,
                "category": entry.category,
                "confidence": entry.confidence,
                "notes": entry.notes
            })

        return {
            "status": "success",
            "data": {
                "property_types": property_type_data,
                "total_count": len(property_type_data)
            },
            "message": "Property type mapping retrieved successfully"
        }

    except Exception as e:
        logger.error(f"Error getting property type mapping: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get property type mapping: {str(e)}")

@router.get("/developer-mapping")
async def get_developer_mapping(
    search: str | None = Query(None, description="Search in developer names"),
    category: str | None = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get developer name mapping for consistency

    Args:
        search: Optional search term to filter developers
        category: Optional category filter
        current_user: Authenticated user

    Returns:
        Dictionary with developer mapping data
    """
    try:
        mapping = normalization_lookup.developer_mapping

        # Apply filters
        if search:
            search_lower = search.lower()
            mapping = {
                k: v for k, v in mapping.items()
                if search_lower in k.lower() or search_lower in v.normalized_value.lower()
            }

        if category:
            mapping = {
                k: v for k, v in mapping.items()
                if v.category.lower() == category.lower()
            }

        # Convert to response format
        developer_data = []
        for dld_name, entry in mapping.items():
            developer_data.append({
                "dld_name": dld_name,
                "normalized_name": entry.normalized_value,
                "category": entry.category,
                "confidence": entry.confidence,
                "notes": entry.notes
            })

        return {
            "status": "success",
            "data": {
                "developers": developer_data,
                "total_count": len(developer_data)
            },
            "message": "Developer mapping retrieved successfully"
        }

    except Exception as e:
        logger.error(f"Error getting developer mapping: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get developer mapping: {str(e)}")

@router.get("/project-mapping")
async def get_project_mapping(
    search: str | None = Query(None, description="Search in project names"),
    category: str | None = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get project name mapping for consistency

    Args:
        search: Optional search term to filter projects
        category: Optional category filter
        current_user: Authenticated user

    Returns:
        Dictionary with project mapping data
    """
    try:
        mapping = normalization_lookup.project_mapping

        # Apply filters
        if search:
            search_lower = search.lower()
            mapping = {
                k: v for k, v in mapping.items()
                if search_lower in k.lower() or search_lower in v.normalized_value.lower()
            }

        if category:
            mapping = {
                k: v for k, v in mapping.items()
                if v.category.lower() == category.lower()
            }

        # Convert to response format
        project_data = []
        for dld_name, entry in mapping.items():
            project_data.append({
                "dld_name": dld_name,
                "normalized_name": entry.normalized_value,
                "category": entry.category,
                "confidence": entry.confidence,
                "notes": entry.notes
            })

        return {
            "status": "success",
            "data": {
                "projects": project_data,
                "total_count": len(project_data)
            },
            "message": "Project mapping retrieved successfully"
        }

    except Exception as e:
        logger.error(f"Error getting project mapping: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get project mapping: {str(e)}")

@router.post("/normalize")
async def normalize_dld_data(
    dld_area: str | None = Query(None, description="DLD area name to normalize"),
    dld_property_type: str | None = Query(None, description="DLD property type to normalize"),
    dld_developer: str | None = Query(None, description="DLD developer name to normalize"),
    dld_project: str | None = Query(None, description="DLD project name to normalize"),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Normalize DLD data to user-friendly format

    Args:
        dld_area: Optional DLD area name
        dld_property_type: Optional DLD property type
        dld_developer: Optional DLD developer name
        dld_project: Optional DLD project name
        current_user: Authenticated user

    Returns:
        Dictionary with normalized data
    """
    try:
        result = {}

        if dld_area:
            result["area"] = {
                "dld_value": dld_area,
                "normalized_value": normalization_lookup.normalize_area(dld_area)
            }

        if dld_property_type:
            result["property_type"] = {
                "dld_value": dld_property_type,
                "normalized_value": normalization_lookup.normalize_property_type(dld_property_type)
            }

        if dld_developer:
            result["developer"] = {
                "dld_value": dld_developer,
                "normalized_value": normalization_lookup.normalize_developer(dld_developer)
            }

        if dld_project:
            result["project"] = {
                "dld_value": dld_project,
                "normalized_value": normalization_lookup.normalize_project(dld_project)
            }

        return {
            "status": "success",
            "data": result,
            "message": "Data normalized successfully"
        }

    except Exception as e:
        logger.error(f"Error normalizing data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to normalize data: {str(e)}")

@router.get("/export")
async def export_normalization_mapping(
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Export complete normalization mapping to JSON format

    Args:
        current_user: Authenticated user

    Returns:
        Dictionary with complete normalization mapping
    """
    try:
        mapping_data = normalization_lookup.export_mapping_to_json()

        return {
            "status": "success",
            "data": mapping_data,
            "message": "Normalization mapping exported successfully"
        }

    except Exception as e:
        logger.error(f"Error exporting normalization mapping: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export normalization mapping: {str(e)}")

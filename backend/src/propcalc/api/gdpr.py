import logging

from fastapi import APIRouter, HTTPException

from ..domain.security.gdpr import get_gdpr_manager

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/api/v1/gdpr/user-data/{user_id}")
async def get_user_data(user_id: str):
    """Get user data for GDPR compliance (Right of Access)"""
    try:
        gdpr_manager = get_gdpr_manager()
        user_data = gdpr_manager.get_user_data(user_id)

        if user_data:
            return {
                "status": "success",
                "user_data": user_data
            }
        else:
            raise HTTPException(status_code=404, detail="User data not found")

    except Exception as e:
        logger.error(f"Error getting user data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user data")

@router.delete("/api/v1/gdpr/user-data/{user_id}")
async def delete_user_data(user_id: str):
    """Delete user data for GDPR compliance (Right to Erasure)"""
    try:
        gdpr_manager = get_gdpr_manager()
        success = gdpr_manager.delete_user_data(user_id)

        if success:
            return {
                "status": "success",
                "message": "User data deleted successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to delete user data")

    except Exception as e:
        logger.error(f"Error deleting user data: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user data")

@router.get("/api/v1/gdpr/report")
async def get_gdpr_report():
    """Get GDPR compliance report"""
    try:
        gdpr_manager = get_gdpr_manager()
        report = gdpr_manager.get_gdpr_report()

        return {
            "status": "success",
            "gdpr_report": report
        }

    except Exception as e:
        logger.error(f"Error generating GDPR report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate GDPR report")

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import logging
import traceback

from utils.cleanup import (
    cleanup_old_documents,
    cleanup_old_slides,
    cleanup_orphaned_uploads,
    vacuum_database
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

# Simple admin dependency for now - in production you'd have proper auth
def get_admin_user():
    # This should be replaced with proper authentication and authorization
    return {"id": "admin", "is_admin": True}

@router.post("/vacuum-database")
async def run_vacuum_database(
    admin_user: Dict = Depends(get_admin_user)
) -> Dict[str, Any]:
    """
    Manually trigger a database vacuum operation to optimize database and reclaim space.
    
    Returns:
        Status of the operation
    """
    try:
        # Verify admin permissions
        if not admin_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin permissions required")
        
        success = vacuum_database()
        
        if success:
            return {"success": True, "message": "Database vacuum completed successfully"}
        else:
            return {"success": False, "message": "Database vacuum failed"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during database vacuum: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error during database vacuum: {str(e)}")

@router.post("/cleanup-documents")
async def run_cleanup_documents(
    retention_days: int = 30,
    admin_user: Dict = Depends(get_admin_user)
) -> Dict[str, Any]:
    """
    Manually trigger cleanup of old documents.
    
    Parameters:
        retention_days: Number of days to keep documents for (default: 30)
        
    Returns:
        Number of documents removed
    """
    try:
        # Verify admin permissions
        if not admin_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin permissions required")
        
        removed_count = cleanup_old_documents(retention_days)
        
        return {
            "success": True,
            "documents_removed": removed_count,
            "message": f"Removed {removed_count} old documents and associated chat history"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during document cleanup: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error during document cleanup: {str(e)}")

@router.post("/cleanup-slides")
async def run_cleanup_slides(
    retention_days: int = 30,
    admin_user: Dict = Depends(get_admin_user)
) -> Dict[str, Any]:
    """
    Manually trigger cleanup of old slide files.
    
    Parameters:
        retention_days: Number of days to keep slide files for (default: 30)
        
    Returns:
        Number of slide files removed
    """
    try:
        # Verify admin permissions
        if not admin_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin permissions required")
        
        removed_count = cleanup_old_slides(retention_days)
        
        return {
            "success": True,
            "files_removed": removed_count,
            "message": f"Removed {removed_count} old slide files"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during slide cleanup: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error during slide cleanup: {str(e)}")

@router.post("/cleanup-uploads")
async def run_cleanup_uploads(
    retention_hours: int = 24,
    admin_user: Dict = Depends(get_admin_user)
) -> Dict[str, Any]:
    """
    Manually trigger cleanup of orphaned upload files.
    
    Parameters:
        retention_hours: Number of hours to keep unused uploaded files for (default: 24)
        
    Returns:
        Number of orphaned files removed
    """
    try:
        # Verify admin permissions
        if not admin_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin permissions required")
        
        removed_count = cleanup_orphaned_uploads(retention_hours)
        
        return {
            "success": True,
            "files_removed": removed_count,
            "message": f"Removed {removed_count} orphaned upload files"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during uploads cleanup: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error during uploads cleanup: {str(e)}")

@router.post("/cleanup-all")
async def run_cleanup_all(
    document_retention_days: int = 30,
    slide_retention_days: int = 30,
    upload_retention_hours: int = 24,
    admin_user: Dict = Depends(get_admin_user)
) -> Dict[str, Any]:
    """
    Run all cleanup operations in sequence.
    
    Parameters:
        document_retention_days: Number of days to keep documents for (default: 30)
        slide_retention_days: Number of days to keep slide files for (default: 30)
        upload_retention_hours: Number of hours to keep unused uploaded files for (default: 24)
        
    Returns:
        Results of all cleanup operations
    """
    try:
        # Verify admin permissions
        if not admin_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin permissions required")
        
        # Run all cleanup operations
        docs_removed = cleanup_old_documents(document_retention_days)
        slides_removed = cleanup_old_slides(slide_retention_days)
        uploads_removed = cleanup_orphaned_uploads(upload_retention_hours)
        vacuum_success = vacuum_database()
        
        return {
            "success": True,
            "documents_removed": docs_removed,
            "slides_removed": slides_removed,
            "uploads_removed": uploads_removed,
            "vacuum_completed": vacuum_success,
            "message": "All cleanup operations completed"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")

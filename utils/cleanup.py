from datetime import datetime, timedelta
import os
import time
import logging
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from utils.database import Storage

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Storage paths from configuration
UPLOAD_DIR = "storage/uploads"
SLIDES_DIR = "output/slides"
DB_PATH = "storage/database.sqlite"

# Import repositories safely
try:
    from utils.repository import DocumentRepository, ChatHistoryRepository
    document_repo = DocumentRepository()
    chat_history_repo = ChatHistoryRepository()
    USE_REPO = True
except ImportError:
    logger.warning("Could not import repository classes, using direct database access")
    USE_REPO = False

# Scheduler singleton
scheduler = None

def get_scheduler():
    """Get or create the scheduler singleton"""
    global scheduler
    if scheduler is None:
        scheduler = BackgroundScheduler()
        scheduler.start()
    return scheduler

def cleanup_old_documents(retention_days=30):
    """Delete document records and files older than retention period"""
    try:
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        cutoff_timestamp = int(cutoff_date.timestamp())
        
        removed_count = 0
        
        if USE_REPO:
            # Use repository method
            old_documents = document_repo.get_old_documents(cutoff_date)
            
            for document in old_documents:
                # Delete associated chat history
                chat_history_repo.delete_chat_history_by_document(document["id"])
                
                # Delete document file if it exists
                if document.get("path") and os.path.exists(document["path"]):
                    try:
                        os.remove(document["path"])
                    except Exception as e:
                        logger.error(f"Error removing document file {document['path']}: {e}")
                
                # Delete document record
                document_repo.delete_document(document["id"])
                removed_count += 1
        else:
            # Direct database access
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get old documents
            cursor.execute("SELECT * FROM documents WHERE created_at < ?", (cutoff_timestamp,))
            old_documents = cursor.fetchall()
            
            for document in old_documents:
                # Delete associated chat history
                cursor.execute("DELETE FROM chat_history WHERE document_id = ?", (document["id"],))
                
                # Delete document file if it exists
                if document.get("path") and os.path.exists(document["path"]):
                    try:
                        os.remove(document["path"])
                    except Exception as e:
                        logger.error(f"Error removing document file {document['path']}: {e}")
                
                # Delete document record
                cursor.execute("DELETE FROM documents WHERE id = ?", (document["id"],))
                removed_count += 1
                
            conn.commit()
            conn.close()
            
        logger.info(f"Cleaned up {removed_count} old documents and associated chat history")
        return removed_count
    except Exception as e:
        logger.error(f"Error during document cleanup: {e}")
        return 0

def cleanup_old_slides(retention_days=30):
    """Delete slide files older than retention period"""
    try:
        cutoff_time = time.time() - (retention_days * 24 * 3600)
        
        file_count = 0
        if os.path.exists(SLIDES_DIR):
            for filename in os.listdir(SLIDES_DIR):
                file_path = os.path.join(SLIDES_DIR, filename)
                if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                    os.remove(file_path)
                    file_count += 1
                    
        logger.info(f"Cleaned up {file_count} old slide files")
        return file_count
    except Exception as e:
        logger.error(f"Error cleaning old slides: {e}")
        return 0

def cleanup_orphaned_uploads(retention_hours=24):
    """Clean uploaded files that aren't linked to any document record"""
    try:
        if not os.path.exists(UPLOAD_DIR):
            return 0
            
        document_paths = set()
        
        if USE_REPO:
            # Get all document paths from database using repository
            all_documents = document_repo.get_all_documents()
            document_paths = {doc.get("path", "") for doc in all_documents}
        else:
            # Direct database access
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM documents")
            document_paths = {row["path"] for row in cursor.fetchall() if row["path"]}
            conn.close()
        
        cutoff_time = time.time() - (retention_hours * 3600)
        
        file_count = 0
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            # Skip directories
            if not os.path.isfile(file_path):
                continue
                
            # Check if file is older than retention period and not linked to any document
            if (os.path.getmtime(file_path) < cutoff_time and 
                file_path not in document_paths and
                os.path.join(UPLOAD_DIR, filename) not in document_paths):
                os.remove(file_path)
                file_count += 1
                
        logger.info(f"Cleaned up {file_count} orphaned upload files")
        return file_count
    except Exception as e:
        logger.error(f"Error cleaning orphaned uploads: {e}")
        return 0

def vacuum_database():
    """Perform database vacuum to reclaim space (SQLite only)"""
    try:
        if hasattr(Storage, 'vacuum_database'):
            # Use the Storage class method if available
            success = Storage.vacuum_database()
        else:
            # Direct database access
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("VACUUM")
            conn.close()
            success = True
            
        logger.info("Database vacuum completed successfully")
        return success
    except Exception as e:
        logger.error(f"Database vacuum failed: {e}")
        return False

def setup_cleaning_tasks(
    document_retention_days=30,
    slide_retention_days=30,
    upload_retention_hours=24
):
    """Initialize all cleaning tasks with configurable retention periods"""
    scheduler = get_scheduler()
    
    # Clean old documents daily at 2 AM
    scheduler.add_job(
        cleanup_old_documents,
        trigger="cron",
        hour=2,
        minute=0,
        id="cleanup_old_documents",
        kwargs={"retention_days": document_retention_days},
        replace_existing=True
    )
    
    # Clean old slides daily at 3 AM
    scheduler.add_job(
        cleanup_old_slides,
        trigger="cron",
        hour=3,
        minute=0,
        id="cleanup_old_slides",
        kwargs={"retention_days": slide_retention_days},
        replace_existing=True
    )
    
    # Clean orphaned uploads every 6 hours
    scheduler.add_job(
        cleanup_orphaned_uploads,
        trigger="interval",
        hours=6,
        id="cleanup_orphaned_uploads",
        kwargs={"retention_hours": upload_retention_hours},
        replace_existing=True
    )
    
    # Weekly database vacuum on Sunday at 4 AM
    scheduler.add_job(
        vacuum_database,
        trigger="cron",
        day_of_week="sun",
        hour=4,
        minute=0,
        id="vacuum_database",
        replace_existing=True
    )
    
    logger.info("Cleaning tasks scheduled successfully")
    return scheduler

"""
Database Migration Scripts for AI NVCB

This module provides database migration functionality for the AI NVCB application.
"""

import sqlite3
import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """Handle database migrations for AI NVCB."""
    
    def __init__(self, db_path: str = "documents.db"):
        """Initialize the migrator with database path."""
        self.db_path = db_path
        self.migrations_dir = Path(__file__).parent / "scripts"
        self.migrations_dir.mkdir(exist_ok=True)
        
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def create_migrations_table(self):
        """Create migrations tracking table if it doesn't exist."""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    checksum TEXT
                )
            """)
            conn.commit()
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT version FROM migrations ORDER BY version")
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Migrations table doesn't exist
            return []
    
    def apply_migration(self, version: str, name: str, sql: str):
        """Apply a single migration."""
        logger.info(f"Applying migration {version}: {name}")
        
        with self.get_connection() as conn:
            try:
                # Execute migration SQL
                conn.executescript(sql)
                
                # Record migration
                conn.execute("""
                    INSERT INTO migrations (version, name, checksum)
                    VALUES (?, ?, ?)
                """, (version, name, hash(sql)))
                
                conn.commit()
                logger.info(f"Successfully applied migration {version}")
                
            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to apply migration {version}: {e}")
                raise
    
    def run_migrations(self):
        """Run all pending migrations."""
        self.create_migrations_table()
        applied = set(self.get_applied_migrations())
        
        migrations = self.get_available_migrations()
        
        for version, name, sql in migrations:
            if version not in applied:
                self.apply_migration(version, name, sql)
    
    def get_available_migrations(self) -> List[tuple]:
        """Get list of available migrations."""
        migrations = []
        
        # Built-in migrations
        migrations.extend([
            ("001", "Create initial tables", self._migration_001_initial_tables()),
            ("002", "Add indexes for performance", self._migration_002_add_indexes()),
            ("003", "Add document metadata", self._migration_003_document_metadata()),
            ("004", "Add user tracking", self._migration_004_user_tracking()),
            ("005", "Add cleanup tracking", self._migration_005_cleanup_tracking()),
        ])
        
        return migrations
    
    def _migration_001_initial_tables(self) -> str:
        """Initial database schema."""
        return """
        -- Documents table
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            file_name TEXT NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT,
            file_size INTEGER,
            file_type TEXT,
            content_hash TEXT,
            analysis_count INTEGER DEFAULT 0,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Chat history table
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            user_query TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            query_type TEXT DEFAULT 'qa',
            model_used TEXT,
            response_time REAL,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        );
        
        -- Slides table
        CREATE TABLE IF NOT EXISTS slides (
            id TEXT PRIMARY KEY,
            document_id TEXT,
            title TEXT,
            content TEXT,
            template TEXT DEFAULT 'default',
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_size INTEGER,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        );
        
        -- System configuration table
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    
    def _migration_002_add_indexes(self) -> str:
        """Add database indexes for performance."""
        return """
        -- Performance indexes
        CREATE INDEX IF NOT EXISTS idx_documents_upload_time ON documents(upload_time);
        CREATE INDEX IF NOT EXISTS idx_documents_file_type ON documents(file_type);
        CREATE INDEX IF NOT EXISTS idx_documents_last_accessed ON documents(last_accessed);
        
        CREATE INDEX IF NOT EXISTS idx_chat_history_document_id ON chat_history(document_id);
        CREATE INDEX IF NOT EXISTS idx_chat_history_timestamp ON chat_history(timestamp);
        CREATE INDEX IF NOT EXISTS idx_chat_history_query_type ON chat_history(query_type);
        
        CREATE INDEX IF NOT EXISTS idx_slides_document_id ON slides(document_id);
        CREATE INDEX IF NOT EXISTS idx_slides_created_at ON slides(created_at);
        
        CREATE INDEX IF NOT EXISTS idx_system_config_key ON system_config(key);
        """
    
    def _migration_003_document_metadata(self) -> str:
        """Add document metadata columns."""
        return """
        -- Add metadata columns to documents table
        ALTER TABLE documents ADD COLUMN metadata TEXT;
        ALTER TABLE documents ADD COLUMN tags TEXT;
        ALTER TABLE documents ADD COLUMN category TEXT;
        ALTER TABLE documents ADD COLUMN language TEXT DEFAULT 'vi';
        ALTER TABLE documents ADD COLUMN processing_status TEXT DEFAULT 'completed';
        """
    
    def _migration_004_user_tracking(self) -> str:
        """Add user tracking capabilities."""
        return """
        -- Add user tracking columns
        ALTER TABLE documents ADD COLUMN user_id TEXT;
        ALTER TABLE documents ADD COLUMN user_session TEXT;
        
        ALTER TABLE chat_history ADD COLUMN user_id TEXT;
        ALTER TABLE chat_history ADD COLUMN user_session TEXT;
        ALTER TABLE chat_history ADD COLUMN feedback_rating INTEGER;
        ALTER TABLE chat_history ADD COLUMN feedback_comment TEXT;
        
        ALTER TABLE slides ADD COLUMN user_id TEXT;
        ALTER TABLE slides ADD COLUMN user_session TEXT;
        
        -- User tracking indexes
        CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
        CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
        CREATE INDEX IF NOT EXISTS idx_slides_user_id ON slides(user_id);
        """
    
    def _migration_005_cleanup_tracking(self) -> str:
        """Add cleanup tracking table."""
        return """
        -- Cleanup tracking table
        CREATE TABLE IF NOT EXISTS cleanup_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cleanup_type TEXT NOT NULL,
            items_processed INTEGER DEFAULT 0,
            items_deleted INTEGER DEFAULT 0,
            space_freed INTEGER DEFAULT 0,
            started_at TIMESTAMP,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'completed',
            error_message TEXT
        );
        
        CREATE INDEX IF NOT EXISTS idx_cleanup_logs_type ON cleanup_logs(cleanup_type);
        CREATE INDEX IF NOT EXISTS idx_cleanup_logs_completed_at ON cleanup_logs(completed_at);
        """
    
    def backup_database(self, backup_path: str = None):
        """Create a backup of the database."""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_{timestamp}.db"
        
        logger.info(f"Creating database backup: {backup_path}")
        
        with self.get_connection() as source:
            backup = sqlite3.connect(backup_path)
            source.backup(backup)
            backup.close()
        
        logger.info(f"Database backup created: {backup_path}")
        return backup_path
    
    def validate_database(self) -> bool:
        """Validate database integrity."""
        try:
            with self.get_connection() as conn:
                # Check database integrity
                cursor = conn.execute("PRAGMA integrity_check")
                result = cursor.fetchone()[0]
                
                if result != "ok":
                    logger.error(f"Database integrity check failed: {result}")
                    return False
                
                # Check that required tables exist
                required_tables = [
                    "documents", "chat_history", "slides", 
                    "system_config", "migrations"
                ]
                
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                existing_tables = [row[0] for row in cursor.fetchall()]
                
                missing_tables = set(required_tables) - set(existing_tables)
                if missing_tables:
                    logger.error(f"Missing required tables: {missing_tables}")
                    return False
                
                logger.info("Database validation passed")
                return True
                
        except Exception as e:
            logger.error(f"Database validation failed: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {}
        
        try:
            with self.get_connection() as conn:
                # Table row counts
                tables = ["documents", "chat_history", "slides", "cleanup_logs"]
                for table in tables:
                    try:
                        cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                        stats[f"{table}_count"] = cursor.fetchone()[0]
                    except sqlite3.OperationalError:
                        stats[f"{table}_count"] = 0
                
                # Database size
                cursor = conn.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                cursor = conn.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                stats["database_size_bytes"] = page_count * page_size
                
                # Applied migrations
                stats["applied_migrations"] = len(self.get_applied_migrations())
                
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            stats["error"] = str(e)
        
        return stats


def main():
    """Main migration runner."""
    logging.basicConfig(level=logging.INFO)
    
    migrator = DatabaseMigrator()
    
    print("🔄 Running database migrations...")
    migrator.run_migrations()
    
    print("✅ Validating database...")
    if migrator.validate_database():
        print("✅ Database validation passed")
    else:
        print("❌ Database validation failed")
        return 1
    
    print("📊 Database statistics:")
    stats = migrator.get_database_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("✅ Migration completed successfully")
    return 0


if __name__ == "__main__":
    exit(main())

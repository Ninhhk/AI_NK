"""
Database seeding utilities for AI NVCB.

This module provides functionality to seed the database with initial data,
test data, and configuration settings.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)


class DatabaseSeeder:
    """Handle database seeding for AI NVCB."""
    
    def __init__(self, db_path: str = "documents.db"):
        """Initialize the seeder with database path."""
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def seed_system_config(self):
        """Seed system configuration with default values."""
        logger.info("Seeding system configuration...")
        
        default_config = {
            "system_prompt": "Phải trả lời bằng tiếng Việt. Hãy trả lời một cách chính xác và hữu ích.",
            "default_model": "llama3.1:8b",
            "max_upload_size": "10485760",  # 10MB
            "allowed_file_types": ".txt,.pdf,.docx,.doc,.md,.rtf",
            "document_retention_days": "30",
            "slide_retention_days": "30",
            "upload_retention_hours": "24",
            "enable_cleanup": "true",
            "enable_background_cleanup": "true",
            "cleanup_interval_hours": "24",
            "app_version": "2.0.0",
            "app_name": "AI NVCB",
            "app_description": "AI-powered document analysis and slide generation system",
            "last_backup": "",
            "maintenance_mode": "false"
        }
        
        with self.get_connection() as conn:
            for key, value in default_config.items():
                conn.execute("""
                    INSERT OR REPLACE INTO system_config (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (key, value))
            conn.commit()
        
        logger.info(f"Seeded {len(default_config)} system configuration entries")
    
    def seed_test_data(self, num_documents: int = 5, num_chats_per_doc: int = 3):
        """Seed database with test data for development."""
        logger.info(f"Seeding test data: {num_documents} documents, {num_chats_per_doc} chats each...")
        
        with self.get_connection() as conn:
            # Create test documents
            document_ids = []
            for i in range(num_documents):
                doc_id = str(uuid.uuid4())
                document_ids.append(doc_id)
                
                upload_time = datetime.now() - timedelta(days=i, hours=i)
                
                conn.execute("""
                    INSERT INTO documents (
                        id, file_name, upload_time, file_path, file_size, file_type,
                        content_hash, analysis_count, last_accessed, language,
                        processing_status, category, user_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    doc_id,
                    f"test_document_{i+1}.pdf",
                    upload_time,
                    f"/uploads/test_document_{i+1}.pdf",
                    1024 * (i + 1),  # Varying file sizes
                    "application/pdf",
                    f"hash_{i+1}",
                    num_chats_per_doc,
                    upload_time,
                    "vi",
                    "completed",
                    "test",
                    "test_user"
                ))
            
            # Create test chat history
            for doc_id in document_ids:
                for j in range(num_chats_per_doc):
                    chat_time = datetime.now() - timedelta(hours=j)
                    
                    conn.execute("""
                        INSERT INTO chat_history (
                            document_id, user_query, ai_response, timestamp,
                            query_type, model_used, response_time, user_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        doc_id,
                        f"Test question {j+1} for document",
                        f"Test response {j+1} with detailed analysis",
                        chat_time,
                        "qa" if j % 2 == 0 else "summary",
                        "llama3.1:8b",
                        2.5 + j * 0.5,
                        "test_user"
                    ))
            
            # Create test slides
            for i, doc_id in enumerate(document_ids[:3]):  # Only for first 3 documents
                slide_id = str(uuid.uuid4())
                created_time = datetime.now() - timedelta(hours=i)
                
                conn.execute("""
                    INSERT INTO slides (
                        id, document_id, title, content, template, file_path,
                        created_at, file_size, user_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    slide_id,
                    doc_id,
                    f"Test Presentation {i+1}",
                    f"Test slide content for document {i+1}",
                    "default",
                    f"/output/slides/test_slides_{i+1}.pptx",
                    created_time,
                    2048 * (i + 1),
                    "test_user"
                ))
            
            conn.commit()
        
        logger.info("Test data seeded successfully")
    
    def seed_cleanup_logs(self, num_logs: int = 10):
        """Seed cleanup logs with sample data."""
        logger.info(f"Seeding {num_logs} cleanup log entries...")
        
        cleanup_types = ["documents", "slides", "uploads", "database_vacuum"]
        
        with self.get_connection() as conn:
            for i in range(num_logs):
                cleanup_type = cleanup_types[i % len(cleanup_types)]
                started_time = datetime.now() - timedelta(days=i, hours=i)
                completed_time = started_time + timedelta(minutes=5 + i)
                
                conn.execute("""
                    INSERT INTO cleanup_logs (
                        cleanup_type, items_processed, items_deleted, space_freed,
                        started_at, completed_at, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    cleanup_type,
                    10 + i * 2,
                    i + 1,
                    1024 * (i + 1),
                    started_time,
                    completed_time,
                    "completed"
                ))
            
            conn.commit()
        
        logger.info("Cleanup logs seeded successfully")
    
    def clear_test_data(self):
        """Clear all test data from the database."""
        logger.info("Clearing test data...")
        
        with self.get_connection() as conn:
            # Clear test data (identified by user_id = 'test_user')
            conn.execute("DELETE FROM chat_history WHERE user_id = 'test_user'")
            conn.execute("DELETE FROM slides WHERE user_id = 'test_user'")
            conn.execute("DELETE FROM documents WHERE user_id = 'test_user'")
            
            # Clear old cleanup logs (keep recent ones)
            cutoff_date = datetime.now() - timedelta(days=7)
            conn.execute("DELETE FROM cleanup_logs WHERE completed_at < ?", (cutoff_date,))
            
            conn.commit()
        
        logger.info("Test data cleared successfully")
    
    def export_config(self, output_file: str):
        """Export system configuration to JSON file."""
        logger.info(f"Exporting configuration to {output_file}...")
        
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT key, value FROM system_config")
            config = dict(cursor.fetchall())
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info("Configuration exported successfully")
    
    def import_config(self, input_file: str):
        """Import system configuration from JSON file."""
        logger.info(f"Importing configuration from {input_file}...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        with self.get_connection() as conn:
            for key, value in config.items():
                conn.execute("""
                    INSERT OR REPLACE INTO system_config (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (key, str(value)))
            conn.commit()
        
        logger.info(f"Imported {len(config)} configuration entries")
    
    def create_admin_user(self, username: str = "admin", password_hash: str = None):
        """Create admin user configuration."""
        logger.info("Creating admin user configuration...")
        
        if password_hash is None:
            # In production, this should be properly hashed
            password_hash = "change_this_password_in_production"
        
        admin_config = {
            "admin_username": username,
            "admin_password_hash": password_hash,
            "admin_created_at": datetime.now().isoformat(),
            "admin_last_login": "",
            "admin_permissions": json.dumps([
                "cleanup", "model_management", "system_config", "user_management"
            ])
        }
        
        with self.get_connection() as conn:
            for key, value in admin_config.items():
                conn.execute("""
                    INSERT OR REPLACE INTO system_config (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (key, value))
            conn.commit()
        
        logger.info("Admin user configuration created")
    
    def get_database_summary(self) -> Dict[str, Any]:
        """Get a summary of the current database state."""
        summary = {}
        
        with self.get_connection() as conn:
            # Table counts
            tables = ["documents", "chat_history", "slides", "cleanup_logs", "system_config"]
            for table in tables:
                try:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    summary[f"{table}_count"] = cursor.fetchone()[0]
                except sqlite3.OperationalError:
                    summary[f"{table}_count"] = 0
            
            # Recent activity
            try:
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM documents 
                    WHERE upload_time > datetime('now', '-7 days')
                """)
                summary["recent_documents"] = cursor.fetchone()[0]
                
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM chat_history 
                    WHERE timestamp > datetime('now', '-7 days')
                """)
                summary["recent_chats"] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                summary["recent_documents"] = 0
                summary["recent_chats"] = 0
            
            # Configuration entries
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM system_config")
                summary["config_entries"] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                summary["config_entries"] = 0
        
        return summary


def main():
    """Main seeding function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database seeding utility for AI NVCB")
    parser.add_argument("--action", choices=["seed", "clear", "config", "summary", "test"], 
                       default="seed", help="Action to perform")
    parser.add_argument("--config-file", help="Configuration file for import/export")
    parser.add_argument("--test-docs", type=int, default=5, help="Number of test documents")
    parser.add_argument("--test-chats", type=int, default=3, help="Number of test chats per document")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    seeder = DatabaseSeeder()
    
    if args.action == "seed":
        print("🌱 Seeding database with initial data...")
        seeder.seed_system_config()
        seeder.create_admin_user()
        print("✅ Initial seeding completed")
        
    elif args.action == "test":
        print("🧪 Seeding database with test data...")
        seeder.seed_test_data(args.test_docs, args.test_chats)
        seeder.seed_cleanup_logs()
        print("✅ Test data seeding completed")
        
    elif args.action == "clear":
        print("🧹 Clearing test data...")
        seeder.clear_test_data()
        print("✅ Test data cleared")
        
    elif args.action == "config":
        if args.config_file:
            if Path(args.config_file).exists():
                seeder.import_config(args.config_file)
            else:
                seeder.export_config(args.config_file)
        else:
            print("❌ Config file path required for config action")
            return 1
            
    elif args.action == "summary":
        print("📊 Database Summary:")
        summary = seeder.get_database_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
    
    return 0


if __name__ == "__main__":
    exit(main())

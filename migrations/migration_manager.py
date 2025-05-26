#!/usr/bin/env python3
"""
Database Migration Manager for AI NVCB

This script manages database schema migrations, versioning, and rollbacks.
Supports both SQLite (development) and PostgreSQL (production) databases.

Usage:
    python migrations/migration_manager.py init
    python migrations/migration_manager.py create add_user_preferences
    python migrations/migration_manager.py migrate
    python migrations/migration_manager.py rollback
    python migrations/migration_manager.py status
"""

import os
import sys
import sqlite3
import logging
import argparse
import importlib.util
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from utils.database import DatabaseConnection, DB_PATH
    from utils.environment import get_environment_config
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Migration paths
MIGRATIONS_DIR = Path(__file__).parent
MIGRATION_FILES_DIR = MIGRATIONS_DIR / "files"
MIGRATION_FILES_DIR.mkdir(exist_ok=True)

@dataclass
class Migration:
    """Migration metadata"""
    version: str
    name: str
    description: str
    applied_at: Optional[datetime] = None
    
class MigrationManager:
    """Manages database migrations"""
    
    def __init__(self):
        """Initialize migration manager"""
        self.config = get_environment_config()
        self.migrations_table = "schema_migrations"
        
    def init_migrations_table(self):
        """Create migrations tracking table"""
        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.migrations_table} (
                    version TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    applied_at INTEGER NOT NULL,
                    checksum TEXT
                )
                """)
                conn.commit()
                logger.info("Migrations table initialized")
        except Exception as e:
            logger.error(f"Failed to initialize migrations table: {e}")
            raise
            
    def get_applied_migrations(self) -> List[Migration]:
        """Get list of applied migrations"""
        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                SELECT version, name, description, applied_at 
                FROM {self.migrations_table} 
                ORDER BY version
                """)
                
                migrations = []
                for row in cursor.fetchall():
                    migrations.append(Migration(
                        version=row['version'],
                        name=row['name'],
                        description=row['description'],
                        applied_at=datetime.fromtimestamp(row['applied_at'])
                    ))
                return migrations
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []
            
    def get_pending_migrations(self) -> List[str]:
        """Get list of pending migration files"""
        applied = {m.version for m in self.get_applied_migrations()}
        
        pending = []
        for migration_file in sorted(MIGRATION_FILES_DIR.glob("*.py")):
            if migration_file.name.startswith("_"):
                continue
            version = migration_file.stem
            if version not in applied:
                pending.append(version)
                
        return pending
        
    def create_migration(self, name: str, description: str = "") -> str:
        """Create a new migration file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = f"{timestamp}_{name}"
        
        migration_content = f'''"""
Migration: {version}
Description: {description or name.replace('_', ' ').title()}
Created: {datetime.now().isoformat()}
"""

def up(cursor):
    """Apply migration"""
    # Add your migration SQL here
    # Example:
    # cursor.execute("""
    # ALTER TABLE documents ADD COLUMN new_field TEXT DEFAULT '';
    # """)
    pass

def down(cursor):
    """Rollback migration"""
    # Add your rollback SQL here
    # Example:
    # cursor.execute("ALTER TABLE documents DROP COLUMN new_field;")
    pass

# Migration metadata
DESCRIPTION = "{description or name.replace('_', ' ').title()}"
'''
        
        migration_path = MIGRATION_FILES_DIR / f"{version}.py"
        with open(migration_path, 'w', encoding='utf-8') as f:
            f.write(migration_content)
            
        logger.info(f"Created migration: {migration_path}")
        return version
        
    def apply_migration(self, version: str) -> bool:
        """Apply a specific migration"""
        migration_path = MIGRATION_FILES_DIR / f"{version}.py"
        
        if not migration_path.exists():
            logger.error(f"Migration file not found: {migration_path}")
            return False
            
        try:
            # Load migration module
            spec = importlib.util.spec_from_file_location(version, migration_path)
            migration_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration_module)
            
            # Apply migration
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                
                # Execute migration
                migration_module.up(cursor)
                
                # Record migration
                cursor.execute(f"""
                INSERT INTO {self.migrations_table} 
                (version, name, description, applied_at, checksum)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    version,
                    version.split('_', 2)[-1] if '_' in version else version,
                    getattr(migration_module, 'DESCRIPTION', ''),
                    int(datetime.now().timestamp()),
                    self._calculate_checksum(migration_path)
                ))
                
                conn.commit()
                logger.info(f"Applied migration: {version}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to apply migration {version}: {e}")
            return False
            
    def rollback_migration(self, version: str) -> bool:
        """Rollback a specific migration"""
        migration_path = MIGRATION_FILES_DIR / f"{version}.py"
        
        if not migration_path.exists():
            logger.error(f"Migration file not found: {migration_path}")
            return False
            
        try:
            # Load migration module
            spec = importlib.util.spec_from_file_location(version, migration_path)
            migration_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration_module)
            
            # Rollback migration
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                
                # Execute rollback
                migration_module.down(cursor)
                
                # Remove migration record
                cursor.execute(f"""
                DELETE FROM {self.migrations_table} WHERE version = ?
                """, (version,))
                
                conn.commit()
                logger.info(f"Rolled back migration: {version}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to rollback migration {version}: {e}")
            return False
            
    def migrate_all(self) -> bool:
        """Apply all pending migrations"""
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("No pending migrations")
            return True
            
        success_count = 0
        for version in pending:
            if self.apply_migration(version):
                success_count += 1
            else:
                logger.error(f"Migration failed, stopping at: {version}")
                break
                
        logger.info(f"Applied {success_count} migrations")
        return success_count == len(pending)
        
    def status(self) -> Dict[str, Any]:
        """Get migration status"""
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()
        
        return {
            'applied_count': len(applied),
            'pending_count': len(pending),
            'applied_migrations': [
                {
                    'version': m.version,
                    'name': m.name,
                    'applied_at': m.applied_at.isoformat() if m.applied_at else None
                }
                for m in applied
            ],
            'pending_migrations': pending,
            'database_path': str(DB_PATH)
        }
        
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate checksum for migration file"""
        import hashlib
        
        with open(file_path, 'rb') as f:
            content = f.read()
            return hashlib.md5(content).hexdigest()

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Database Migration Manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    subparsers.add_parser('init', help='Initialize migration system')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create new migration')
    create_parser.add_argument('name', help='Migration name')
    create_parser.add_argument('--description', help='Migration description')
    
    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Apply migrations')
    migrate_parser.add_argument('--version', help='Specific version to migrate to')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback migration')
    rollback_parser.add_argument('version', help='Version to rollback')
    
    # Status command
    subparsers.add_parser('status', help='Show migration status')
    
    # Seed command
    subparsers.add_parser('seed', help='Seed database with sample data')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    manager = MigrationManager()
    
    try:
        if args.command == 'init':
            manager.init_migrations_table()
            print("Migration system initialized")
            
        elif args.command == 'create':
            version = manager.create_migration(args.name, args.description or "")
            print(f"Created migration: {version}")
            
        elif args.command == 'migrate':
            if args.version:
                success = manager.apply_migration(args.version)
                print(f"Migration {'applied' if success else 'failed'}")
            else:
                success = manager.migrate_all()
                print(f"Migrations {'completed' if success else 'failed'}")
                
        elif args.command == 'rollback':
            success = manager.rollback_migration(args.version)
            print(f"Rollback {'completed' if success else 'failed'}")
            
        elif args.command == 'status':
            status = manager.status()
            print(f"Applied migrations: {status['applied_count']}")
            print(f"Pending migrations: {status['pending_count']}")
            print(f"Database: {status['database_path']}")
            
            if status['applied_migrations']:
                print("\nApplied:")
                for migration in status['applied_migrations']:
                    print(f"  - {migration['version']} ({migration['applied_at']})")
                    
            if status['pending_migrations']:
                print("\nPending:")
                for migration in status['pending_migrations']:
                    print(f"  - {migration}")
                    
        elif args.command == 'seed':
            from migrations.seed_data import seed_database
            seed_database()
            print("Database seeded with sample data")
            
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

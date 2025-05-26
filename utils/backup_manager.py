"""
Automated backup and recovery system for AI NVCB application.

This module provides comprehensive backup and recovery capabilities including
database backups, file system backups, configuration backups, and automated
recovery procedures.
"""

import os
import shutil
import subprocess
import asyncio
import gzip
import tarfile
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import tempfile
import sqlite3
from dataclasses import dataclass, asdict

try:
    import boto3
    HAS_S3 = True
except ImportError:
    HAS_S3 = False

try:
    import paramiko
    HAS_SFTP = True
except ImportError:
    HAS_SFTP = False

from utils.production_logging import get_production_logger

logger = get_production_logger('backup')


@dataclass
class BackupManifest:
    """Backup manifest containing backup metadata."""
    backup_id: str
    backup_type: str
    created_at: str
    size_bytes: int
    source_path: str
    backup_path: str
    compression: str
    checksum: str
    metadata: Dict[str, Any]
    retention_days: int


class BackupStorage:
    """Abstract base class for backup storage backends."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def upload(self, local_path: str, remote_path: str) -> bool:
        """Upload backup to storage."""
        raise NotImplementedError
    
    async def download(self, remote_path: str, local_path: str) -> bool:
        """Download backup from storage."""
        raise NotImplementedError
    
    async def delete(self, remote_path: str) -> bool:
        """Delete backup from storage."""
        raise NotImplementedError
    
    async def list_backups(self, prefix: str = '') -> List[Dict[str, Any]]:
        """List available backups."""
        raise NotImplementedError


class LocalBackupStorage(BackupStorage):
    """Local filesystem backup storage."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.backup_directory = Path(config.get('backup_directory', './backups'))
        self.backup_directory.mkdir(parents=True, exist_ok=True)
    
    async def upload(self, local_path: str, remote_path: str) -> bool:
        """Copy backup to local backup directory."""
        try:
            destination = self.backup_directory / remote_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            if Path(local_path).is_file():
                shutil.copy2(local_path, destination)
            else:
                shutil.copytree(local_path, destination, dirs_exist_ok=True)
            
            logger.info(f"Backup uploaded to local storage: {destination}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload backup to local storage: {e}")
            return False
    
    async def download(self, remote_path: str, local_path: str) -> bool:
        """Copy backup from local backup directory."""
        try:
            source = self.backup_directory / remote_path
            
            if not source.exists():
                logger.error(f"Backup not found: {source}")
                return False
            
            if source.is_file():
                shutil.copy2(source, local_path)
            else:
                shutil.copytree(source, local_path, dirs_exist_ok=True)
            
            logger.info(f"Backup downloaded from local storage: {source}")
            return True
        except Exception as e:
            logger.error(f"Failed to download backup from local storage: {e}")
            return False
    
    async def delete(self, remote_path: str) -> bool:
        """Delete backup from local backup directory."""
        try:
            backup_path = self.backup_directory / remote_path
            
            if backup_path.is_file():
                backup_path.unlink()
            elif backup_path.is_dir():
                shutil.rmtree(backup_path)
            else:
                logger.warning(f"Backup not found for deletion: {backup_path}")
                return False
            
            logger.info(f"Backup deleted from local storage: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete backup from local storage: {e}")
            return False
    
    async def list_backups(self, prefix: str = '') -> List[Dict[str, Any]]:
        """List available backups in local storage."""
        backups = []
        
        try:
            pattern = f"{prefix}*" if prefix else "*"
            for backup_path in self.backup_directory.glob(pattern):
                if backup_path.is_file():
                    stat = backup_path.stat()
                    backups.append({
                        'path': str(backup_path.relative_to(self.backup_directory)),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
        except Exception as e:
            logger.error(f"Failed to list local backups: {e}")
        
        return backups


class S3BackupStorage(BackupStorage):
    """Amazon S3 backup storage."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        if not HAS_S3:
            raise RuntimeError("boto3 library not available for S3 storage")
        
        self.bucket_name = config.get('s3_bucket_name')
        self.prefix = config.get('s3_prefix', 'ai-nvcb-backups/')
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.get('aws_access_key_id'),
            aws_secret_access_key=config.get('aws_secret_access_key'),
            region_name=config.get('aws_region', 'us-east-1')
        )
    
    async def upload(self, local_path: str, remote_path: str) -> bool:
        """Upload backup to S3."""
        try:
            s3_key = f"{self.prefix}{remote_path}"
            
            # Upload file
            self.s3_client.upload_file(local_path, self.bucket_name, s3_key)
            
            logger.info(f"Backup uploaded to S3: s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload backup to S3: {e}")
            return False
    
    async def download(self, remote_path: str, local_path: str) -> bool:
        """Download backup from S3."""
        try:
            s3_key = f"{self.prefix}{remote_path}"
            
            # Download file
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            
            logger.info(f"Backup downloaded from S3: s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to download backup from S3: {e}")
            return False
    
    async def delete(self, remote_path: str) -> bool:
        """Delete backup from S3."""
        try:
            s3_key = f"{self.prefix}{remote_path}"
            
            # Delete object
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            
            logger.info(f"Backup deleted from S3: s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete backup from S3: {e}")
            return False
    
    async def list_backups(self, prefix: str = '') -> List[Dict[str, Any]]:
        """List available backups in S3."""
        backups = []
        
        try:
            full_prefix = f"{self.prefix}{prefix}"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=full_prefix
            )
            
            for obj in response.get('Contents', []):
                key = obj['Key']
                # Remove the prefix to get relative path
                relative_path = key[len(self.prefix):]
                
                backups.append({
                    'path': relative_path,
                    'size': obj['Size'],
                    'modified': obj['LastModified'].isoformat()
                })
        except Exception as e:
            logger.error(f"Failed to list S3 backups: {e}")
        
        return backups


class BackupManager:
    """Main backup management system."""
    
    def __init__(self):
        self.config = self._load_config()
        self.storage_backend = self._setup_storage_backend()
        self.backup_directory = Path(self.config['local_backup_directory'])
        self.backup_directory.mkdir(parents=True, exist_ok=True)
        self.manifests = {}
    
    def _load_config(self) -> Dict[str, Any]:
        """Load backup configuration."""
        return {
            'enabled': os.getenv('BACKUP_ENABLED', 'true').lower() == 'true',
            'storage_backend': os.getenv('BACKUP_STORAGE_BACKEND', 'local'),
            'local_backup_directory': os.getenv('LOCAL_BACKUP_DIRECTORY', './backups'),
            'backup_schedule': os.getenv('BACKUP_SCHEDULE', '0 2 * * *'),  # Daily at 2 AM
            'retention_days': int(os.getenv('BACKUP_RETENTION_DAYS', '30')),
            'compression_enabled': os.getenv('BACKUP_COMPRESSION', 'true').lower() == 'true',
            'encryption_enabled': os.getenv('BACKUP_ENCRYPTION', 'false').lower() == 'true',
            'encryption_password': os.getenv('BACKUP_ENCRYPTION_PASSWORD', ''),
            'include_uploads': os.getenv('BACKUP_INCLUDE_UPLOADS', 'true').lower() == 'true',
            'include_logs': os.getenv('BACKUP_INCLUDE_LOGS', 'false').lower() == 'true',
            'include_cache': os.getenv('BACKUP_INCLUDE_CACHE', 'false').lower() == 'true',
            'max_backup_size_gb': int(os.getenv('MAX_BACKUP_SIZE_GB', '10')),
            'backup_verification': os.getenv('BACKUP_VERIFICATION', 'true').lower() == 'true',
            # S3 configuration
            's3_bucket_name': os.getenv('S3_BACKUP_BUCKET'),
            's3_prefix': os.getenv('S3_BACKUP_PREFIX', 'ai-nvcb-backups/'),
            'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
            'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
            'aws_region': os.getenv('AWS_REGION', 'us-east-1'),
            # SFTP configuration
            'sftp_host': os.getenv('SFTP_BACKUP_HOST'),
            'sftp_port': int(os.getenv('SFTP_BACKUP_PORT', '22')),
            'sftp_username': os.getenv('SFTP_BACKUP_USERNAME'),
            'sftp_password': os.getenv('SFTP_BACKUP_PASSWORD'),
            'sftp_key_file': os.getenv('SFTP_BACKUP_KEY_FILE'),
            'sftp_remote_path': os.getenv('SFTP_BACKUP_REMOTE_PATH', '/backups/')
        }
    
    def _setup_storage_backend(self) -> BackupStorage:
        """Setup storage backend based on configuration."""
        backend_type = self.config['storage_backend'].lower()
        
        if backend_type == 's3':
            return S3BackupStorage(self.config)
        elif backend_type == 'sftp':
            # Implement SFTP storage if needed
            raise NotImplementedError("SFTP storage backend not implemented")
        else:
            return LocalBackupStorage(self.config)
    
    def _generate_backup_id(self) -> str:
        """Generate unique backup ID."""
        return f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum."""
        import hashlib
        
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def backup_database(self, backup_id: str = None) -> Optional[str]:
        """
        Backup application database.
        
        Args:
            backup_id: Optional backup ID
            
        Returns:
            Path to backup file if successful
        """
        backup_id = backup_id or self._generate_backup_id()
        
        try:
            database_url = os.getenv('DATABASE_URL', 'sqlite:///./ai_nvcb.db')
            
            if database_url.startswith('sqlite'):
                # SQLite backup
                db_path = database_url.replace('sqlite:///', '').replace('sqlite://', '')
                
                if not Path(db_path).exists():
                    logger.error(f"Database file not found: {db_path}")
                    return None
                
                # Create backup filename
                backup_filename = f"{backup_id}_database.db"
                backup_path = self.backup_directory / backup_filename
                
                # Copy database file
                shutil.copy2(db_path, backup_path)
                
                # Compress if enabled
                if self.config['compression_enabled']:
                    compressed_path = f"{backup_path}.gz"
                    with open(backup_path, 'rb') as f_in:
                        with gzip.open(compressed_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    # Remove uncompressed file
                    backup_path.unlink()
                    backup_path = Path(compressed_path)
                
                # Create manifest
                manifest = BackupManifest(
                    backup_id=backup_id,
                    backup_type='database',
                    created_at=datetime.utcnow().isoformat(),
                    size_bytes=backup_path.stat().st_size,
                    source_path=db_path,
                    backup_path=str(backup_path),
                    compression='gzip' if self.config['compression_enabled'] else 'none',
                    checksum=self._calculate_checksum(str(backup_path)),
                    metadata={'database_type': 'sqlite', 'database_path': db_path},
                    retention_days=self.config['retention_days']
                )
                
                # Save manifest
                self.manifests[backup_id] = manifest
                await self._save_manifest(manifest)
                
                logger.info(f"Database backup completed: {backup_path}")
                return str(backup_path)
                
            else:
                # PostgreSQL or other database backup
                logger.warning("Non-SQLite database backup not implemented")
                return None
                
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return None
    
    async def backup_files(self, backup_id: str = None, include_patterns: List[str] = None) -> Optional[str]:
        """
        Backup application files.
        
        Args:
            backup_id: Optional backup ID
            include_patterns: List of file patterns to include
            
        Returns:
            Path to backup archive if successful
        """
        backup_id = backup_id or self._generate_backup_id()
        
        try:
            # Default patterns to include
            if include_patterns is None:
                include_patterns = [
                    'backend/**/*.py',
                    'frontend/**/*',
                    'utils/**/*.py',
                    'migrations/**/*.py',
                    'templates/**/*',
                    'static/**/*',
                    '*.py',
                    '*.json',
                    '*.yaml',
                    '*.yml',
                    '.env*',
                    'requirements.txt',
                    'Dockerfile*',
                    'docker-compose*.yml'
                ]
                
                if self.config['include_uploads']:
                    include_patterns.append('uploads/**/*')
                
                if self.config['include_logs']:
                    include_patterns.append('logs/**/*')
                
                if self.config['include_cache']:
                    include_patterns.append('cache/**/*')
            
            # Create backup archive
            backup_filename = f"{backup_id}_files.tar"
            if self.config['compression_enabled']:
                backup_filename += ".gz"
            
            backup_path = self.backup_directory / backup_filename
            
            # Create tar archive
            mode = 'w:gz' if self.config['compression_enabled'] else 'w'
            
            with tarfile.open(backup_path, mode) as tar:
                for pattern in include_patterns:
                    for file_path in Path('.').glob(pattern):
                        if file_path.is_file():
                            tar.add(file_path, arcname=str(file_path))
            
            # Check backup size
            backup_size_gb = backup_path.stat().st_size / (1024**3)
            if backup_size_gb > self.config['max_backup_size_gb']:
                logger.warning(f"Backup size ({backup_size_gb:.2f}GB) exceeds maximum ({self.config['max_backup_size_gb']}GB)")
            
            # Create manifest
            manifest = BackupManifest(
                backup_id=backup_id,
                backup_type='files',
                created_at=datetime.utcnow().isoformat(),
                size_bytes=backup_path.stat().st_size,
                source_path='.',
                backup_path=str(backup_path),
                compression='gzip' if self.config['compression_enabled'] else 'none',
                checksum=self._calculate_checksum(str(backup_path)),
                metadata={'include_patterns': include_patterns, 'file_count': len(list(Path('.').glob('**/*')))},
                retention_days=self.config['retention_days']
            )
            
            # Save manifest
            self.manifests[backup_id] = manifest
            await self._save_manifest(manifest)
            
            logger.info(f"File backup completed: {backup_path} ({backup_size_gb:.2f}GB)")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"File backup failed: {e}")
            return None
    
    async def backup_configuration(self, backup_id: str = None) -> Optional[str]:
        """
        Backup application configuration.
        
        Args:
            backup_id: Optional backup ID
            
        Returns:
            Path to backup file if successful
        """
        backup_id = backup_id or self._generate_backup_id()
        
        try:
            # Collect configuration
            config_data = {
                'environment_variables': dict(os.environ),
                'backup_timestamp': datetime.utcnow().isoformat(),
                'backup_id': backup_id,
                'application_version': os.getenv('APP_VERSION', 'unknown'),
                'configuration_files': {}
            }
            
            # Include configuration files
            config_files = [
                '.env',
                '.env.example',
                '.env.production',
                '.env.development',
                'docker-compose.yml',
                'docker-compose.prod.yml',
                'requirements.txt',
                'package.json'
            ]
            
            for config_file in config_files:
                config_path = Path(config_file)
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data['configuration_files'][config_file] = f.read()
            
            # Create backup file
            backup_filename = f"{backup_id}_config.json"
            backup_path = self.backup_directory / backup_filename
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            # Compress if enabled
            if self.config['compression_enabled']:
                compressed_path = f"{backup_path}.gz"
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove uncompressed file
                backup_path.unlink()
                backup_path = Path(compressed_path)
            
            # Create manifest
            manifest = BackupManifest(
                backup_id=backup_id,
                backup_type='configuration',
                created_at=datetime.utcnow().isoformat(),
                size_bytes=backup_path.stat().st_size,
                source_path='configuration',
                backup_path=str(backup_path),
                compression='gzip' if self.config['compression_enabled'] else 'none',
                checksum=self._calculate_checksum(str(backup_path)),
                metadata={'config_files': list(config_data['configuration_files'].keys())},
                retention_days=self.config['retention_days']
            )
            
            # Save manifest
            self.manifests[backup_id] = manifest
            await self._save_manifest(manifest)
            
            logger.info(f"Configuration backup completed: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Configuration backup failed: {e}")
            return None
    
    async def create_full_backup(self) -> Optional[Dict[str, str]]:
        """
        Create a complete backup of the application.
        
        Returns:
            Dictionary of backup paths if successful
        """
        backup_id = self._generate_backup_id()
        backup_paths = {}
        
        logger.info(f"Starting full backup: {backup_id}")
        
        try:
            # Backup database
            db_backup = await self.backup_database(backup_id)
            if db_backup:
                backup_paths['database'] = db_backup
            
            # Backup files
            files_backup = await self.backup_files(backup_id)
            if files_backup:
                backup_paths['files'] = files_backup
            
            # Backup configuration
            config_backup = await self.backup_configuration(backup_id)
            if config_backup:
                backup_paths['configuration'] = config_backup
            
            # Upload to remote storage
            if self.storage_backend and not isinstance(self.storage_backend, LocalBackupStorage):
                for backup_type, backup_path in backup_paths.items():
                    remote_path = f"{backup_id}/{Path(backup_path).name}"
                    success = await self.storage_backend.upload(backup_path, remote_path)
                    
                    if success:
                        logger.info(f"Uploaded {backup_type} backup to remote storage")
                    else:
                        logger.error(f"Failed to upload {backup_type} backup to remote storage")
            
            # Verify backups
            if self.config['backup_verification']:
                await self._verify_backups(backup_paths)
            
            logger.info(f"Full backup completed: {backup_id}")
            return backup_paths
            
        except Exception as e:
            logger.error(f"Full backup failed: {e}")
            return None
    
    async def restore_from_backup(self, backup_id: str, backup_type: str = 'full') -> bool:
        """
        Restore application from backup.
        
        Args:
            backup_id: Backup ID to restore from
            backup_type: Type of backup to restore ('database', 'files', 'configuration', 'full')
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Starting restore from backup: {backup_id} (type: {backup_type})")
            
            # Load manifest
            manifest = await self._load_manifest(backup_id)
            if not manifest:
                logger.error(f"Backup manifest not found: {backup_id}")
                return False
            
            # Restore based on type
            if backup_type in ['database', 'full']:
                success = await self._restore_database(backup_id)
                if not success:
                    logger.error("Database restore failed")
                    return False
            
            if backup_type in ['files', 'full']:
                success = await self._restore_files(backup_id)
                if not success:
                    logger.error("Files restore failed")
                    return False
            
            if backup_type in ['configuration', 'full']:
                success = await self._restore_configuration(backup_id)
                if not success:
                    logger.error("Configuration restore failed")
                    return False
            
            logger.info(f"Restore completed successfully: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    async def cleanup_old_backups(self) -> int:
        """
        Clean up old backups based on retention policy.
        
        Returns:
            Number of backups cleaned up
        """
        cleaned_count = 0
        cutoff_date = datetime.utcnow() - timedelta(days=self.config['retention_days'])
        
        try:
            # Get list of all backups
            backups = await self.storage_backend.list_backups()
            
            for backup in backups:
                backup_date = datetime.fromisoformat(backup['modified'].replace('Z', '+00:00'))
                
                if backup_date < cutoff_date:
                    # Delete old backup
                    success = await self.storage_backend.delete(backup['path'])
                    if success:
                        cleaned_count += 1
                        logger.info(f"Deleted old backup: {backup['path']}")
                    else:
                        logger.error(f"Failed to delete old backup: {backup['path']}")
            
            logger.info(f"Cleanup completed: {cleaned_count} old backups removed")
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
        
        return cleaned_count
    
    async def _save_manifest(self, manifest: BackupManifest):
        """Save backup manifest."""
        manifest_path = self.backup_directory / f"{manifest.backup_id}_manifest.json"
        
        with open(manifest_path, 'w') as f:
            json.dump(asdict(manifest), f, indent=2)
    
    async def _load_manifest(self, backup_id: str) -> Optional[BackupManifest]:
        """Load backup manifest."""
        manifest_path = self.backup_directory / f"{backup_id}_manifest.json"
        
        if not manifest_path.exists():
            return None
        
        with open(manifest_path, 'r') as f:
            data = json.load(f)
            return BackupManifest(**data)
    
    async def _verify_backups(self, backup_paths: Dict[str, str]) -> bool:
        """Verify backup integrity."""
        for backup_type, backup_path in backup_paths.items():
            if not Path(backup_path).exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Verify file is not corrupted (basic check)
            try:
                if backup_path.endswith('.gz'):
                    with gzip.open(backup_path, 'rb') as f:
                        f.read(1024)  # Read first chunk
                elif backup_path.endswith('.tar.gz'):
                    with tarfile.open(backup_path, 'r:gz') as tar:
                        tar.getnames()[:10]  # Get first 10 names
                
                logger.info(f"Backup verification passed: {backup_type}")
            except Exception as e:
                logger.error(f"Backup verification failed for {backup_type}: {e}")
                return False
        
        return True
    
    async def _restore_database(self, backup_id: str) -> bool:
        """Restore database from backup."""
        # Implementation depends on database type
        # This is a basic SQLite restore implementation
        try:
            backup_filename = f"{backup_id}_database.db"
            if self.config['compression_enabled']:
                backup_filename += ".gz"
            
            backup_path = self.backup_directory / backup_filename
            
            if not backup_path.exists():
                logger.error(f"Database backup not found: {backup_path}")
                return False
            
            # Determine restore path
            database_url = os.getenv('DATABASE_URL', 'sqlite:///./ai_nvcb.db')
            db_path = database_url.replace('sqlite:///', '').replace('sqlite://', '')
            
            # Create backup of current database
            current_backup = f"{db_path}.backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            if Path(db_path).exists():
                shutil.copy2(db_path, current_backup)
                logger.info(f"Created backup of current database: {current_backup}")
            
            # Restore database
            if self.config['compression_enabled']:
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(db_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_path, db_path)
            
            logger.info(f"Database restored from backup: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            return False
    
    async def _restore_files(self, backup_id: str) -> bool:
        """Restore files from backup."""
        try:
            backup_filename = f"{backup_id}_files.tar"
            if self.config['compression_enabled']:
                backup_filename += ".gz"
            
            backup_path = self.backup_directory / backup_filename
            
            if not backup_path.exists():
                logger.error(f"Files backup not found: {backup_path}")
                return False
            
            # Extract files
            mode = 'r:gz' if self.config['compression_enabled'] else 'r'
            
            with tarfile.open(backup_path, mode) as tar:
                tar.extractall(path='.')
            
            logger.info(f"Files restored from backup: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Files restore failed: {e}")
            return False
    
    async def _restore_configuration(self, backup_id: str) -> bool:
        """Restore configuration from backup."""
        try:
            backup_filename = f"{backup_id}_config.json"
            if self.config['compression_enabled']:
                backup_filename += ".gz"
            
            backup_path = self.backup_directory / backup_filename
            
            if not backup_path.exists():
                logger.error(f"Configuration backup not found: {backup_path}")
                return False
            
            # Load configuration
            if self.config['compression_enabled']:
                with gzip.open(backup_path, 'rt') as f:
                    config_data = json.load(f)
            else:
                with open(backup_path, 'r') as f:
                    config_data = json.load(f)
            
            # Restore configuration files
            for config_file, content in config_data.get('configuration_files', {}).items():
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Restored configuration file: {config_file}")
            
            logger.info(f"Configuration restored from backup: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Configuration restore failed: {e}")
            return False


# Global backup manager
backup_manager = BackupManager()


async def create_backup(backup_type: str = 'full') -> Optional[Union[str, Dict[str, str]]]:
    """Create a backup of the specified type."""
    if not backup_manager.config['enabled']:
        logger.warning("Backup is disabled")
        return None
    
    if backup_type == 'database':
        return await backup_manager.backup_database()
    elif backup_type == 'files':
        return await backup_manager.backup_files()
    elif backup_type == 'configuration':
        return await backup_manager.backup_configuration()
    elif backup_type == 'full':
        return await backup_manager.create_full_backup()
    else:
        logger.error(f"Unknown backup type: {backup_type}")
        return None


async def restore_backup(backup_id: str, backup_type: str = 'full') -> bool:
    """Restore from a backup."""
    return await backup_manager.restore_from_backup(backup_id, backup_type)


async def cleanup_backups() -> int:
    """Clean up old backups."""
    return await backup_manager.cleanup_old_backups()


def get_backup_manager() -> BackupManager:
    """Get the global backup manager."""
    return backup_manager

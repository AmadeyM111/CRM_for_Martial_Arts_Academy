#!/usr/bin/env python3
"""
Backup Service for BJJ CRM System
Handles database and file backups
"""

import os
import shutil
import sqlite3
import subprocess
import tarfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import json


class BackupService:
    """Service for handling backups and restores"""
    
    def __init__(self, app_dir: str = None):
        self.app_dir = app_dir or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.backup_dir = os.path.join(self.app_dir, "backups")
        self.db_path = os.path.join(self.app_dir, "bjj_crm.db")
        
        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, include_files: bool = True) -> Dict[str, str]:
        """
        Create a backup of database and optionally files
        
        Args:
            include_files: Whether to include application files
            
        Returns:
            Dict with backup info: {'db_file': path, 'files_file': path, 'timestamp': str}
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_info = {
            'timestamp': timestamp,
            'created_at': datetime.now().isoformat(),
            'db_file': None,
            'files_file': None,
            'include_files': include_files,
            'app_version': '1.0.0',
            'backup_type': 'manual',
            'description': 'Резервная копия BJJ CRM',
            'file_sizes': {},
            'checksums': {}
        }
        
        try:
            # Backup database
            db_backup_path = os.path.join(self.backup_dir, f"bjj_crm_{timestamp}.db")
            shutil.copy2(self.db_path, db_backup_path)
            backup_info['db_file'] = db_backup_path
            
            # Get database file size
            if os.path.exists(db_backup_path):
                backup_info['file_sizes']['database'] = os.path.getsize(db_backup_path)
            
            # Backup application files if requested
            if include_files:
                files_backup_path = os.path.join(self.backup_dir, f"bjj_crm_files_{timestamp}.tar.gz")
                self._create_files_backup(files_backup_path)
                backup_info['files_file'] = files_backup_path
                
                # Get files archive size
                if os.path.exists(files_backup_path):
                    backup_info['file_sizes']['files'] = os.path.getsize(files_backup_path)
            
            # Create backup metadata
            metadata_path = os.path.join(self.backup_dir, f"backup_metadata_{timestamp}.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, ensure_ascii=False, indent=2)
            
            return backup_info
            
        except Exception as e:
            raise Exception(f"Ошибка создания бэкапа: {str(e)}")
    
    def _create_files_backup(self, backup_path: str):
        """Create tar.gz backup of application files"""
        with tarfile.open(backup_path, "w:gz") as tar:
            # Add main application files
            files_to_backup = [
                "main.py",
                "requirements.txt",
                ".env",
                "app/",
                "database/",
                "scripts/",
                "docs/"
            ]
            
            for file_path in files_to_backup:
                full_path = os.path.join(self.app_dir, file_path)
                if os.path.exists(full_path):
                    tar.add(full_path, arcname=file_path)
    
    def list_backups(self) -> List[Dict[str, str]]:
        """
        List all available backups
        
        Returns:
            List of backup info dictionaries
        """
        backups = []
        
        try:
            for file_name in os.listdir(self.backup_dir):
                if file_name.startswith("backup_metadata_") and file_name.endswith(".json"):
                    metadata_path = os.path.join(self.backup_dir, file_name)
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            backup_info = json.load(f)
                            backup_info['metadata_file'] = metadata_path
                            backups.append(backup_info)
                    except (json.JSONDecodeError, FileNotFoundError):
                        continue
            
            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x['timestamp'], reverse=True)
            return backups
            
        except Exception as e:
            raise Exception(f"Ошибка получения списка бэкапов: {str(e)}")
    
    def restore_backup(self, backup_info: Dict[str, str], restore_files: bool = False) -> bool:
        """
        Restore from backup
        
        Args:
            backup_info: Backup info dictionary
            restore_files: Whether to restore application files
            
        Returns:
            True if successful
        """
        try:
            # Restore database
            if backup_info.get('db_file') and os.path.exists(backup_info['db_file']):
                # Create backup of current database
                current_backup = f"{self.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(self.db_path, current_backup)
                
                # Restore database
                shutil.copy2(backup_info['db_file'], self.db_path)
            
            # Restore files if requested
            if restore_files and backup_info.get('files_file') and os.path.exists(backup_info['files_file']):
                self._restore_files_backup(backup_info['files_file'])
            
            return True
            
        except Exception as e:
            raise Exception(f"Ошибка восстановления: {str(e)}")
    
    def _restore_files_backup(self, backup_path: str):
        """Restore files from tar.gz backup"""
        with tarfile.open(backup_path, "r:gz") as tar:
            tar.extractall(path=self.app_dir)
    
    def delete_backup(self, backup_info: Dict[str, str]) -> bool:
        """
        Delete backup files
        
        Args:
            backup_info: Backup info dictionary
            
        Returns:
            True if successful
        """
        try:
            files_to_delete = [
                backup_info.get('db_file'),
                backup_info.get('files_file'),
                backup_info.get('metadata_file')
            ]
            
            for file_path in files_to_delete:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            
            return True
            
        except Exception as e:
            raise Exception(f"Ошибка удаления бэкапа: {str(e)}")
    
    def get_backup_size(self, backup_info: Dict[str, str]) -> int:
        """
        Get total size of backup files in bytes
        
        Args:
            backup_info: Backup info dictionary
            
        Returns:
            Total size in bytes
        """
        total_size = 0
        
        files_to_check = [
            backup_info.get('db_file'),
            backup_info.get('files_file'),
            backup_info.get('metadata_file')
        ]
        
        for file_path in files_to_check:
            if file_path and os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
        
        return total_size
    
    def cleanup_old_backups(self, keep_days: int = 7) -> int:
        """
        Clean up old backups
        
        Args:
            keep_days: Number of days to keep backups
            
        Returns:
            Number of backups deleted
        """
        deleted_count = 0
        cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 3600)
        
        try:
            for file_name in os.listdir(self.backup_dir):
                file_path = os.path.join(self.backup_dir, file_name)
                if os.path.getmtime(file_path) < cutoff_time:
                    os.remove(file_path)
                    deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            raise Exception(f"Ошибка очистки старых бэкапов: {str(e)}")
    
    def format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"


# Example usage
if __name__ == "__main__":
    backup_service = BackupService()
    
    # Create backup
    backup_info = backup_service.create_backup()
    print(f"Backup created: {backup_info}")
    
    # List backups
    backups = backup_service.list_backups()
    print(f"Available backups: {len(backups)}")
    
    for backup in backups:
        size = backup_service.get_backup_size(backup)
        print(f"  - {backup['timestamp']}: {backup_service.format_size(size)}")

"""
Utility functions for the RBAC-Project application.

This module contains common utility functions used across the application.
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_file_hash(file_path: Path) -> str:
    """
    Calculate SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        SHA-256 hash string
    """
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return file_hash
    except Exception as e:
        logger.error(f"Failed to calculate file hash for {file_path}: {e}")
        return ""

def get_file_info(file_path: Path) -> Dict[str, Any]:
    """
    Get comprehensive file information.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary containing file information
    """
    try:
        stat = file_path.stat()
        return {
            "name": file_path.name,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime),
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "extension": file_path.suffix.lower(),
            "hash": get_file_hash(file_path)
        }
    except Exception as e:
        logger.error(f"Failed to get file info for {file_path}: {e}")
        return {}

def ensure_directory(path: Path) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False

def clean_filename(filename: str) -> str:
    """
    Clean a filename by removing or replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename
    """
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    
    return filename

def get_safe_table_name(filename: str) -> str:
    """
    Convert a filename to a safe database table name.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe table name
    """
    # Remove extension and clean
    name = Path(filename).stem
    
    # Replace hyphens and spaces with underscores
    name = name.replace('-', '_').replace(' ', '_')
    
    # Remove any remaining invalid characters
    name = ''.join(c for c in name if c.isalnum() or c == '_')
    
    # Ensure it starts with a letter
    if name and not name[0].isalpha():
        name = 'table_' + name
    
    # Ensure it's not empty
    if not name:
        name = 'unnamed_table'
    
    return name.lower()

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def validate_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate if a file has an allowed extension.
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed file extensions
        
    Returns:
        True if file type is allowed, False otherwise
    """
    file_extension = Path(filename).suffix.lower()
    return file_extension in allowed_extensions

def get_relative_path(file_path: Path, base_path: Path) -> str:
    """
    Get relative path from base path.
    
    Args:
        file_path: Full file path
        base_path: Base directory path
        
    Returns:
        Relative path string
    """
    try:
        return str(file_path.relative_to(base_path))
    except ValueError:
        return str(file_path)

def create_backup_path(original_path: Path) -> Path:
    """
    Create a backup path for a file.
    
    Args:
        original_path: Original file path
        
    Returns:
        Backup file path
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{original_path.stem}_{timestamp}{original_path.suffix}"
    return original_path.parent / backup_name

def is_text_file(file_path: Path) -> bool:
    """
    Check if a file is a text file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if it's a text file, False otherwise
    """
    text_extensions = {'.txt', '.md', '.csv', '.json', '.xml', '.html', '.css', '.js', '.py', '.java', '.cpp', '.c'}
    return file_path.suffix.lower() in text_extensions

def get_mime_type(file_path: Path) -> str:
    """
    Get MIME type based on file extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MIME type string
    """
    mime_types = {
        '.txt': 'text/plain',
        '.md': 'text/markdown',
        '.csv': 'text/csv',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.py': 'text/x-python',
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif'
    }
    
    return mime_types.get(file_path.suffix.lower(), 'application/octet-stream')

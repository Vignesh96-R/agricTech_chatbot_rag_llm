import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_file_hash(file_path: Path) -> str:
    # Calculate SHA-256 hash of a file.
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return file_hash
    except Exception as e:
        logger.error(f"Failed to calculate file hash for {file_path}: {e}")
        return ""

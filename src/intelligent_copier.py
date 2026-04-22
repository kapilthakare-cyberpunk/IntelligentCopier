#!/usr/bin/env python3
"""
IntelligentCopier - AI-powered file copying with intelligent filtering

This module provides intelligent file copying capabilities using Magika AI
for file type detection and smart filtering.
"""

import os
import shutil
import hashlib
import json
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Magika integration
def check_file_type(file_path: str) -> Dict[str, Any]:
    """Check file type using Magika"""
    try:
        result = subprocess.run(
            ['magika', '-r', '--json', file_path],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {'label': 'unknown', 'score': 0.0}
    except Exception as e:
        logger.debug(f"Magika check failed: {e}")
        return {'label': 'unknown', 'score': 0.0}

class FileFilter:
    """Smart file filtering based on various criteria"""
    
    def __init__(self):
        self.include_extensions: set = set()
        self.exclude_extensions: set = set()
        self.include_patterns: List[str] = []
        self.exclude_patterns: List[str] = []
        self.min_size: Optional[int] = None
        self.max_size: Optional[int] = None
        self.use_magika: bool = True
    
    def set_extensions(self, include: Optional[List[str]] = None, 
                       exclude: Optional[List[str]] = None):
        if include:
            self.include_extensions = {ext.lower().lstrip('.') for ext in include}
        if exclude:
            self.exclude_extensions = {ext.lower().lstrip('.') for ext in exclude}
    
    def should_copy(self, file_path: str) -> bool:
        """Determine if a file should be copied based on filter criteria"""
        path = Path(file_path)
        
        # Extension filters
        ext = path.suffix.lower().lstrip('.')
        if self.include_extensions and ext not in self.include_extensions:
            return False
        if ext in self.exclude_extensions:
            return False
        
        # Size filters
        try:
            size = path.stat().st_size
            if self.min_size and size < self.min_size:
                return False
            if self.max_size and size > self.max_size:
                return False
        except OSError:
            pass
        
        return True


class CopySession:
    """Manages a file copying session with progress tracking"""
    
    def __init__(self, source: str, destination: str, filter: Optional[FileFilter] = None):
        self.source = Path(source)
        self.destination = Path(destination)
        self.filter = filter or FileFilter()
        self.total_files: int = 0
        self.copied_files: int = 0
        self.skipped_files: int = 0
        self.failed_files: int = 0
        self.file_list: List[Path] = []
        self.status = "pending"  # pending, running, paused, completed, failed
    
    def scan(self, recursive: bool = True) -> int:
        """Scan source directory and build file list"""
        self.file_list = []
        
        if recursive:
            for root, _, files in os.walk(self.source):
                for file in files:
                    file_path = Path(root) / file
                    if self.filter.should_copy(str(file_path)):
                        self.file_list.append(file_path)
        else:
            for item in self.source.iterdir():
                if item.is_file() and self.filter.should_copy(str(item)):
                    self.file_list.append(item)
        
        self.total_files = len(self.file_list)
        return self.total_files
    
    def copy_file(self, src: Path, dest_dir: Path) -> bool:
        """Copy a single file with error handling"""
        try:
            rel_path = src.relative_to(self.source)
            dest_path = dest_dir / rel_path
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest_path)
            return True
        except Exception as e:
            logger.error(f"Failed to copy {src}: {e}")
            return False
    
    def run(self) -> None:
        """Execute the copy operation"""
        self.status = "running"
        
        for file_path in self.file_list:
            if self.copy_file(file_path, self.destination):
                self.copied_files += 1
            else:
                self.failed_files += 1
            
            progress = (self.copied_files + self.failed_files) / self.total_files * 100
            logger.info(f"Progress: {progress:.1f}% - Copied {self.copied_files}/{self.total_files}")
        
        self.status = "completed"


def verify_copy(source: str, destination: str) -> Dict[str, Any]:
    """Verify that copy was successful by comparing file hashes"""
    source_files = {}
    dest_files = {}
    
    # Get all source file hashes
    for root, _, files in os.walk(source):
        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(source)
            with open(file_path, 'rb') as f:
                source_files[str(rel_path)] = hashlib.md5(f.read()).hexdigest()
    
    # Get all dest file hashes
    for root, _, files in os.walk(destination):
        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(destination)
            with open(file_path, 'rb') as f:
                dest_files[str(rel_path)] = hashlib.md5(f.read()).hexdigest()
    
    # Compare
    missing = set(source_files.keys()) - set(dest_files.keys())
    mismatch = []
    
    for rel_path in source_files:
        if rel_path in dest_files:
            if source_files[rel_path] != dest_files[rel_path]:
                mismatch.append(rel_path)
    
    return {
        'success': len(missing) == 0 and len(mismatch) == 0,
        'total_files': len(source_files),
        'missing': list(missing),
        'mismatch': mismatch
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: intelligent_copier.py <source> <destination>")
        sys.exit(1)
    
    session = CopySession(sys.argv[1], sys.argv[2])
    session.scan()
    session.run()
    
    print(f"\nCopy completed: {session.copied_files} files copied, {session.failed_files} failed")

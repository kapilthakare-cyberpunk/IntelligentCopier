#!/usr/bin/env python3
"""
Magika Integration Module for Intelligent File Copier

Provides fast, content-based file type detection using Google's Magika.
https://github.com/google/magika

Features:
- File type detection from content (not just extension)
- Content-based duplicate detection
- File type distribution analysis
- Suspicious file detection
- Auto-categorization
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import hashlib
import threading

# Optional import - app works without Magika
try:
    from magika import Magika
    MAGIKA_AVAILABLE = True
except ImportError:
    MAGIKA_AVAILABLE = False


@dataclass
class FileInfo:
    """Represents file information with Magika detection."""
    path: str
    size: int
    extension: str
    magika_type: Optional[str] = None
    mime_type: Optional[str] = None
    confidence: Optional[float] = None
    content_hash: Optional[str] = None
    is_suspicious: bool = False


class MagikaAnalyzer:
    """Analyzer class using Magika for file type detection."""

    def __init__(self):
        self.magika = None
        self.available = MAGIKA_AVAILABLE
        self.initialized = False
        self._init_magika()

    def _init_magika(self):
        """Initialize Magika if available."""
        if self.available:
            try:
                self.magika = Magika()
                self.initialized = True
            except Exception as e:
                print(f"Warning: Could not initialize Magika: {e}")
                self.available = False

    def is_available(self) -> bool:
        """Check if Magika is available and initialized."""
        return self.available and self.initialized

    def detect_file_type(self, file_path: str) -> Optional[Tuple[str, str, float]]:
        """
        Detect file type using Magika.

        Returns:
            Tuple of (magika_type, mime_type, confidence) or None if failed
        """
        if not self.is_available():
            return None

        try:
            result = self.magika.identify_path(Path(file_path))
            return (
                result.output.ct_label,
                result.output.mime_type,
                result.output.score
            )
        except Exception as e:
            print(f"Magika detection failed for {file_path}: {e}")
            return None

    def analyze_directory(self, directory: str,
                         progress_callback=None,
                         stop_event=None) -> Dict:
        """
        Analyze entire directory with Magika.

        Args:
            directory: Path to analyze
            progress_callback: Optional callback function(current, total)
            stop_event: Optional threading.Event to stop early

        Returns:
            Dictionary with analysis results
        """
        results = {
            'total_files': 0,
            'analyzed_files': 0,
            'type_distribution': defaultdict(int),
            'mime_distribution': defaultdict(int),
            'suspicious_files': [],
            'large_files': [],
            'file_list': []
        }

        # Collect all files
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                files.append(os.path.join(root, filename))

        results['total_files'] = len(files)

        # Analyze each file
        for i, file_path in enumerate(files):
            if stop_event and stop_event.is_set():
                break

            try:
                stat = os.stat(file_path)
                size = stat.st_size

                file_info = FileInfo(
                    path=file_path,
                    size=size,
                    extension=Path(file_path).suffix.lower()
                )

                # Magika detection
                if self.is_available():
                    detection = self.detect_file_type(file_path)
                    if detection:
                        file_info.magika_type, file_info.mime_type, file_info.confidence = detection
                        results['type_distribution'][file_info.magika_type] += 1
                        results['mime_distribution'][file_info.mime_type] += 1

                        # Check for suspicious files (extension mismatch)
                        if self._is_suspicious(file_path, file_info.magika_type):
                            file_info.is_suspicious = True
                            results['suspicious_files'].append(file_info)

                # Detect large files (>1GB)
                if size > 1_000_000_000:
                    results['large_files'].append(file_info)

                results['file_list'].append(file_info)
                results['analyzed_files'] += 1

                if progress_callback:
                    progress_callback(i + 1, len(files))

            except (OSError, PermissionError):
                continue

        return results

    def _is_suspicious(self, file_path: str, magika_type: str) -> bool:
        """
        Check if file extension matches its content type.

        Returns True if extension doesn't match detected type.
        """
        ext = Path(file_path).suffix.lower()

        # Common mismatches
        suspicious_pairs = {
            '.jpg': ['executable', 'shellscript', 'javascript'],
            '.png': ['executable', 'shellscript'],
            '.pdf': ['executable'],
            '.txt': ['executable'],
            '.doc': ['executable'],
            '.docx': ['executable'],
        }

        if ext in suspicious_pairs:
            if magika_type.lower() in suspicious_pairs[ext]:
                return True

        # Check if executable disguised as document
        executable_types = ['executable', 'shellscript', 'python', 'javascript']
        document_extensions = ['.doc', '.docx', '.pdf', '.txt', '.rtf']

        if ext in document_extensions and magika_type.lower() in executable_types:
            return True

        return False

    def find_duplicates_by_content(self, file_list: List[FileInfo],
                                   progress_callback=None) -> List[List[FileInfo]]:
        """
        Find duplicate files by content hash.

        More reliable than name/size matching.

        Returns:
            List of duplicate groups (each group is a list of FileInfo)
        """
        # Group by size first (optimization)
        size_groups = defaultdict(list)
        for f in file_list:
            size_groups[f.size].append(f)

        # Only hash files with same size
        hash_groups = defaultdict(list)

        processed = 0
        total = sum(len(g) for g in size_groups.values() if len(g) > 1)

        for size, files in size_groups.items():
            if len(files) < 2:
                continue

            for f in files:
                try:
                    f.content_hash = self._calculate_hash(f.path)
                    hash_groups[f.content_hash].append(f)

                    processed += 1
                    if progress_callback:
                        progress_callback(processed, total)
                except Exception:
                    continue

        # Return only actual duplicates (groups with 2+ files)
        return [group for group in hash_groups.values() if len(group) > 1]

    def _calculate_hash(self, file_path: str, sample_size: int = 8192) -> str:
        """
        Calculate MD5 hash of file.

        For large files, uses first and last sample_size bytes.
        """
        hasher = hashlib.md5()

        with open(file_path, 'rb') as f:
            # Read first chunk
            data = f.read(sample_size)
            hasher.update(data)

            # For large files, also hash end
            if len(data) == sample_size:
                f.seek(-sample_size, 2)
                data = f.read(sample_size)
                hasher.update(data)

        return hasher.hexdigest()

    def get_category_for_type(self, magika_type: str) -> str:
        """Map Magika type to high-level category."""
        categories = {
            'images': ['jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'ico'],
            'documents': ['pdf', 'doc', 'docx', 'odt', 'rtf', 'txt'],
            'spreadsheets': ['xls', 'xlsx', 'ods', 'csv'],
            'presentations': ['ppt', 'pptx', 'odp'],
            'archives': ['zip', 'tar', 'gz', 'bz2', '7z', 'rar'],
            'executables': ['elf', 'pebin', 'macho'],
            'code': ['python', 'javascript', 'shellscript', 'html', 'css'],
            'audio': ['mp3', 'wav', 'ogg', 'flac', 'aac'],
            'video': ['mp4', 'avi', 'mkv', 'mov', 'wmv'],
        }

        type_lower = magika_type.lower()
        for category, types in categories.items():
            if type_lower in types:
                return category

        return 'other'


class ContentBasedOrganizer:
    """Organizes files by detected content type."""

    def __init__(self, magika_analyzer: MagikaAnalyzer):
        self.analyzer = magika_analyzer

    def suggest_organization(self, source_dir: str) -> Dict[str, List[str]]:
        """
        Suggest folder organization based on content types.

        Returns:
            Dictionary mapping category names to file paths
        """
        if not self.analyzer.is_available():
            return {}

        analysis = self.analyzer.analyze_directory(source_dir)
        organization = defaultdict(list)

        for file_info in analysis['file_list']:
            if file_info.magika_type:
                category = self.analyzer.get_category_for_type(file_info.magika_type)
                organization[category].append(file_info.path)

        return dict(organization)


# Standalone CLI for testing
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Magika File Analyzer')
    parser.add_argument('path', help='File or directory to analyze')
    parser.add_argument('--duplicates', action='store_true',
                       help='Find duplicates')
    parser.add_argument('--organize', action='store_true',
                       help='Suggest organization')

    args = parser.parse_args()

    analyzer = MagikaAnalyzer()

    if not analyzer.is_available():
        print("Error: Magika not available. Install with: pip install magika")
        exit(1)

    if os.path.isfile(args.path):
        result = analyzer.detect_file_type(args.path)
        if result:
            print(f"File: {args.path}")
            print(f"  Type: {result[0]}")
            print(f"  MIME: {result[1]}")
            print(f"  Confidence: {result[2]:.2%}")
    else:
        print(f"Analyzing directory: {args.path}")
        results = analyzer.analyze_directory(args.path)

        print(f"\nTotal files: {results['total_files']}")
        print(f"Analyzed: {results['analyzed_files']}")

        print("\nFile type distribution:")
        for ftype, count in sorted(results['type_distribution'].items(),
                                    key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {ftype}: {count}")

        if results['suspicious_files']:
            print(f"\n⚠ Found {len(results['suspicious_files'])} suspicious files")

        if args.duplicates:
            print("\nFinding duplicates by content...")
            duplicates = analyzer.find_duplicates_by_content(results['file_list'])
            if duplicates:
                print(f"Found {len(duplicates)} duplicate groups")
                for group in duplicates[:5]:
                    print(f"\n  Group ({len(group)} files):")
                    for f in group:
                        print(f"    - {f.path}")
            else:
                print("No duplicates found")

        if args.organize:
            print("\nSuggested organization:")
            organizer = ContentBasedOrganizer(analyzer)
            suggestion = organizer.suggest_organization(args.path)
            for category, files in sorted(suggestion.items()):
                print(f"\n  {category}/ ({len(files)} files)")

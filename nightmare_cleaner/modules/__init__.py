"""
Base module for all cleaning modules
"""
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple


class CleaningModule(ABC):
    """Abstract base class for all cleaning modules"""

    def __init__(self):
        self.name = self.__class__.__name__
        self.description = ""
        self.files_to_clean = []
        self.total_size = 0
        self.total_count = 0

    @abstractmethod
    def scan(self) -> Tuple[int, int]:
        """
        Scan for files to clean
        Returns: (count, size_in_bytes)
        """
        pass

    @abstractmethod
    def clean(self, dry_run=False) -> Tuple[int, int]:
        """
        Clean the files
        Args:
            dry_run: If True, only simulate cleaning without actual deletion
        Returns: (count_cleaned, size_cleaned)
        """
        pass

    def get_stats(self) -> Dict:
        """Get statistics about this module"""
        return {
            'name': self.name,
            'description': self.description,
            'count': self.total_count,
            'size': self.total_size
        }

    def safe_delete(self, filepath, dry_run=False):
        """Safely delete a file with error handling"""
        if dry_run:
            return True

        try:
            if os.path.isfile(filepath):
                os.remove(filepath)
                return True
            elif os.path.isdir(filepath):
                import shutil
                shutil.rmtree(filepath)
                return True
        except (PermissionError, OSError) as e:
            return False
        return False

    def get_file_size(self, filepath):
        """Get file size safely"""
        try:
            if os.path.isfile(filepath):
                return os.path.getsize(filepath)
            elif os.path.isdir(filepath):
                total = 0
                for dirpath, dirnames, filenames in os.walk(filepath):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        try:
                            total += os.path.getsize(fp)
                        except (OSError, FileNotFoundError):
                            continue
                return total
        except (OSError, FileNotFoundError):
            return 0
        return 0

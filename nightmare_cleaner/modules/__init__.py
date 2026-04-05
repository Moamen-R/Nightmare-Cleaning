"""
Base module for all cleaning modules
"""

import os
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple

from ..security import is_safe_path, is_safe_extension


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
    def clean(self, dry_run=False, secure=False) -> Tuple[int, int]:
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
            "name": self.name,
            "description": self.description,
            "count": self.total_count,
            "size": self.total_size,
        }

    def safe_delete(self, filepath, dry_run=False, secure=False):
        """Safely delete a file with error handling"""
        if not is_safe_path(filepath) or not is_safe_extension(filepath):
            return False

        if dry_run:
            return True

        try:
            if os.path.isfile(filepath):
                if secure:
                    # Implement secure file deletion (3 passes)
                    try:
                        size = os.path.getsize(filepath)
                        with open(filepath, "r+b", buffering=0) as f:
                            for _ in range(3):
                                f.seek(0)
                                f.write(os.urandom(size))
                    except Exception:
                        pass
                os.remove(filepath)
                return True
            elif os.path.isdir(filepath):
                import shutil

                if secure:
                    # Secure delete files inside directory first
                    for dirpath, _, filenames in os.walk(filepath):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            try:
                                size = os.path.getsize(fp)
                                with open(fp, "r+b", buffering=0) as fh:
                                    for _ in range(3):
                                        fh.seek(0)
                                        fh.write(os.urandom(size))
                            except Exception:
                                pass
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

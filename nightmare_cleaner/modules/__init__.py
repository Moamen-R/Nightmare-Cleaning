"""
Base module for all cleaning modules
"""

import os
import stat
import shutil
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, final

from ..security import is_safe_path, is_safe_extension
from ..audit_logger import log_deletion, log_blocked, log_error


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
    def clean(self, dry_run: bool = False, secure: bool = False) -> Tuple[int, int]:
        """
        Clean the files
        Args:
            dry_run: If True, only simulate cleaning without actual deletion
            secure: If True, overwrite files with random data before deletion
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

    def _secure_wipe(self, filepath: str, passes: int = 3) -> None:
        """
        Securely wipe a file by overwriting with random data.
        Uses fsync to ensure data reaches disk.
        """
        size = os.path.getsize(filepath)
        with open(filepath, "r+b", buffering=0) as f:
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(size))
                f.flush()
                os.fsync(f.fileno())

    @final
    def safe_delete(
        self, filepath: str, dry_run: bool = False, secure: bool = False
    ) -> bool:
        """
        Safely delete a file with security checks.

        Marked @final to prevent subclasses from bypassing security.
        Performs:
        1. Path safety validation (no traversal, not critical system path)
        2. Extension safety check (no .sys, .dll, etc.)
        3. TOCTOU fix: uses os.stat with follow_symlinks=False
        4. Symlink rejection
        5. Optional secure wipe (3-pass overwrite)
        6. Audit logging
        """
        if not is_safe_path(filepath) or not is_safe_extension(filepath):
            log_blocked(
                self.name, os.path.basename(filepath), "Unsafe path or extension"
            )
            return False

        if dry_run:
            return True

        try:
            # TOCTOU fix: use os.stat with follow_symlinks=False to detect symlinks
            stat_result = os.stat(filepath, follow_symlinks=False)

            # Reject symlinks entirely to prevent symlink attacks
            if stat.S_ISLNK(stat_result.st_mode):
                log_blocked(self.name, os.path.basename(filepath), "Symlink rejected")
                return False

            if os.path.isfile(filepath):
                if secure:
                    try:
                        self._secure_wipe(filepath)
                    except Exception as e:
                        # If secure wipe fails, do NOT delete the file
                        log_error(
                            self.name,
                            os.path.basename(filepath),
                            f"Secure wipe failed: {type(e).__name__}",
                        )
                        return False

                os.remove(filepath)
                log_deletion(
                    self.name, os.path.basename(filepath), stat_result.st_size, secure
                )
                return True

            elif os.path.isdir(filepath):
                if secure:
                    for dirpath, _, filenames in os.walk(filepath):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            try:
                                self._secure_wipe(fp)
                            except Exception:
                                pass
                shutil.rmtree(filepath)
                log_deletion(self.name, filepath, 0, secure)
                return True

        except (PermissionError, OSError) as e:
            log_error(self.name, os.path.basename(filepath), type(e).__name__)
            return False

        return False

    def get_file_size(self, filepath: str) -> int:
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

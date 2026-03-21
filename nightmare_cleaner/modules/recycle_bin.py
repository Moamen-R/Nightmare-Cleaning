"""
Recycle bin cleaning module
"""
import os
import subprocess
from typing import Tuple
from . import CleaningModule


class RecycleBinCleaner(CleaningModule):
    """Clean the Windows Recycle Bin"""

    def __init__(self):
        super().__init__()
        self.description = "Recycle Bin"

    def scan(self) -> Tuple[int, int]:
        """Scan recycle bin"""
        self.total_size = 0
        self.total_count = 0

        if os.name == 'nt':
            # Try to get recycle bin size on Windows
            try:
                # Check all drives
                import string
                from pathlib import Path

                for drive in string.ascii_uppercase:
                    recycle_path = f"{drive}:\\$Recycle.Bin"
                    if os.path.exists(recycle_path):
                        try:
                            for root, dirs, files in os.walk(recycle_path):
                                for file in files:
                                    try:
                                        filepath = os.path.join(root, file)
                                        size = os.path.getsize(filepath)
                                        self.total_size += size
                                        self.total_count += 1
                                    except (PermissionError, OSError):
                                        continue
                        except (PermissionError, OSError):
                            continue
            except Exception:
                pass

        return self.total_count, self.total_size

    def clean(self, dry_run=False) -> Tuple[int, int]:
        """Empty the recycle bin"""
        if dry_run:
            return self.total_count, self.total_size

        cleaned_count = 0
        cleaned_size = self.total_size

        if os.name == 'nt':
            try:
                # Use PowerShell to empty recycle bin on Windows
                subprocess.run(
                    ['powershell', '-Command', 'Clear-RecycleBin', '-Force'],
                    capture_output=True,
                    check=False
                )
                cleaned_count = self.total_count
            except Exception:
                pass

        return cleaned_count, cleaned_size

"""
Windows Store cache cleaning module
"""
import os
import subprocess
from typing import Tuple
from . import CleaningModule


class WindowsStoreCacheCleaner(CleaningModule):
    """Clear Windows Store cache"""

    def __init__(self):
        super().__init__()
        self.description = "Windows Store cache"
        self.can_run = os.name == 'nt'

    def scan(self) -> Tuple[int, int]:
        """Scan Windows Store cache - returns placeholder values"""
        # Windows Store cache doesn't have easily measurable size
        self.total_size = 0
        self.total_count = 0

        if self.can_run:
            # Indicate that Windows Store cache can be cleared
            self.total_count = 1

        return self.total_count, self.total_size

    def clean(self, dry_run=False, secure=False) -> Tuple[int, int]:
        """Clear Windows Store cache"""
        if dry_run or not self.can_run:
            return self.total_count, self.total_size

        cleaned_count = 0
        cleaned_size = 0

        try:
            # Clear Windows Store cache using wsreset
            subprocess.run(
                ['wsreset.exe'],
                capture_output=True,
                check=False,
                timeout=30
            )
            cleaned_count = 1
        except (subprocess.TimeoutExpired, Exception):
            pass

        return cleaned_count, cleaned_size

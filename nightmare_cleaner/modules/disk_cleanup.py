"""
Disk Cleanup utility runner module
"""
import os
import subprocess
from typing import Tuple
from . import CleaningModule


class DiskCleanupCleaner(CleaningModule):
    """Run Windows Disk Cleanup utility"""

    def __init__(self):
        super().__init__()
        self.description = "Disk Cleanup utility"
        self.can_run = os.name == 'nt'

    def scan(self) -> Tuple[int, int]:
        """Scan for Disk Cleanup - returns estimated values"""
        # Disk Cleanup doesn't provide a scan mode, so we return placeholder values
        self.total_size = 0
        self.total_count = 0

        if self.can_run:
            # Indicate that the utility is available
            self.total_count = 1

        return self.total_count, self.total_size

    def clean(self, dry_run=False, secure=False) -> Tuple[int, int]:
        """Run Disk Cleanup utility"""
        if dry_run or not self.can_run:
            return self.total_count, self.total_size

        cleaned_count = 0
        cleaned_size = 0

        try:
            # Run cleanmgr with /sagerun to execute preset cleanup tasks
            # /sagerun:1 runs cleanup tasks preset 1
            subprocess.run(
                ['cleanmgr', '/sagerun:1'],
                capture_output=True,
                check=False,
                timeout=300  # 5 minute timeout
            )
            cleaned_count = 1
        except (subprocess.TimeoutExpired, Exception):
            pass

        return cleaned_count, cleaned_size

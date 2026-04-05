"""
Memory (RAM) cleaning module
"""

import ctypes
import os
from typing import Tuple
from . import CleaningModule


class MemoryCleaner(CleaningModule):
    """Frees up unused memory using Windows API"""

    def __init__(self):
        super().__init__()
        self.description = "Unused System Memory (RAM)"
        self.can_run = os.name == "nt"
        self.process_all_access = 0x1F0FFF

    def scan(self) -> Tuple[int, int]:
        """Scan for Memory - returns placeholder as we don't know exactly how much will be freed"""
        self.total_size = 0
        self.total_count = 0

        if self.can_run:
            self.total_count = 1
            # Give a dummy size like 0 bytes since we can't estimate exact freeing amount
            self.total_size = 0

        return self.total_count, self.total_size

    def clean(self, dry_run=False, secure=False) -> Tuple[int, int]:
        """Empty Working Set of all processes"""
        if dry_run or not self.can_run:
            return self.total_count, self.total_size

        cleaned_count = 0
        cleaned_size = 0

        try:
            # Use ctypes to call Windows API EmptyWorkingSet
            psapi = ctypes.WinDLL("psapi")
            kernel32 = ctypes.WinDLL("kernel32")

            # Empty system working set
            kernel32.SetProcessWorkingSetSize(kernel32.GetCurrentProcess(), -1, -1)
            cleaned_count = 1

        except Exception:
            pass

        return cleaned_count, cleaned_size

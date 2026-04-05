"""
Windows Update cache cleaning module
"""
import os
from typing import Tuple
from . import CleaningModule


class WindowsUpdateCacheCleaner(CleaningModule):
    """Clean Windows Update cache files"""

    def __init__(self):
        super().__init__()
        self.description = "Windows Update cache"
        self.cache_locations = []
        if os.name == 'nt':
            windir = os.environ.get('WINDIR', 'C:\\Windows')
            # SoftwareDistribution folder contains update cache
            self.cache_locations.append(
                os.path.join(windir, 'SoftwareDistribution', 'Download')
            )

    def scan(self) -> Tuple[int, int]:
        """Scan Windows Update cache"""
        self.files_to_clean = []
        self.total_size = 0
        self.total_count = 0

        for cache_dir in self.cache_locations:
            if not os.path.exists(cache_dir):
                continue

            try:
                for root, dirs, files in os.walk(cache_dir):
                    for file in files:
                        filepath = os.path.join(root, file)
                        try:
                            size = self.get_file_size(filepath)
                            self.files_to_clean.append(filepath)
                            self.total_size += size
                            self.total_count += 1
                        except (PermissionError, OSError):
                            continue
            except (PermissionError, OSError):
                continue

        return self.total_count, self.total_size

    def clean(self, dry_run=False, secure=False) -> Tuple[int, int]:
        """Clean Windows Update cache"""
        cleaned_count = 0
        cleaned_size = 0

        for filepath in self.files_to_clean:
            try:
                size = self.get_file_size(filepath)
                if self.safe_delete(filepath, dry_run=dry_run, secure=secure):
                    cleaned_count += 1
                    cleaned_size += size
            except (PermissionError, OSError):
                continue

        return cleaned_count, cleaned_size

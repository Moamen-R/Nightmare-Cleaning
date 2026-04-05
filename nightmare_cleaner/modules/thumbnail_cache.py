"""
Windows thumbnail cache cleaning module
"""
import os
from typing import Tuple
from . import CleaningModule


class ThumbnailCacheCleaner(CleaningModule):
    """Clean Windows thumbnail cache"""

    def __init__(self):
        super().__init__()
        self.description = "Windows thumbnail cache"
        self.cache_locations = []
        if os.name == 'nt':
            local_appdata = os.environ.get('LOCALAPPDATA', '')
            if local_appdata:
                self.cache_locations.append(
                    os.path.join(local_appdata, 'Microsoft', 'Windows', 'Explorer')
                )

    def scan(self) -> Tuple[int, int]:
        """Scan thumbnail cache"""
        self.files_to_clean = []
        self.total_size = 0
        self.total_count = 0

        for cache_dir in self.cache_locations:
            if not os.path.exists(cache_dir):
                continue

            try:
                for file in os.listdir(cache_dir):
                    if file.startswith('thumbcache_') and file.endswith('.db'):
                        filepath = os.path.join(cache_dir, file)
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
        """Clean thumbnail cache"""
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

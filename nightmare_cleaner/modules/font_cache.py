"""
Windows Font Cache cleaning module
"""

import os
import glob
from typing import Tuple
from . import CleaningModule


class FontCacheCleaner(CleaningModule):
    """Clean Windows Font Cache files"""

    def __init__(self):
        super().__init__()
        self.description = "Windows Font Cache"
        self.cache_locations = []
        if os.name == "nt":
            localappdata = os.environ.get("LOCALAPPDATA", "")
            if localappdata:
                # Windows 10/11 Font Cache
                # Don't try to delete the folder, just the dat files inside
                self.cache_locations.append(
                    os.path.join(localappdata, "Microsoft", "Windows", "FontCache")
                )

            windir = os.environ.get("WINDIR", "")
            if windir:
                self.cache_locations.append(
                    os.path.join(
                        windir,
                        "ServiceProfiles",
                        "LocalService",
                        "AppData",
                        "Local",
                        "FontCache",
                    )
                )

    def scan(self) -> Tuple[int, int]:
        """Scan Windows Font Cache"""
        self.files_to_clean = []
        self.total_size = 0
        self.total_count = 0

        for cache_dir in self.cache_locations:
            if not os.path.exists(cache_dir):
                continue

            try:
                # Get only known font cache .dat files (not all .dat files)
                search_pattern = os.path.join(cache_dir, "**", "FntCache_*.dat")
                for filepath in glob.glob(search_pattern, recursive=True):
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
        """Clean Windows Font Cache"""
        # Note: Font Cache files are often locked by the 'Windows Font Cache Service' (FontCache)
        # So we just delete what we can
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

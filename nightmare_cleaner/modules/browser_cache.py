"""
Browser cache cleaning module
"""

import os
from pathlib import Path
from typing import Tuple
from . import CleaningModule


class BrowserCacheCleaner(CleaningModule):
    """Clean browser caches"""

    def __init__(self):
        super().__init__()
        self.description = "Browser cache and temporary internet files"
        self.cache_locations = self._get_cache_locations()

    def _get_cache_locations(self):
        """Get browser cache locations"""
        locations = []
        if os.name == "nt":
            local_appdata = os.environ.get("LOCALAPPDATA", "")
            if local_appdata:
                # Chrome
                locations.append(
                    os.path.join(
                        local_appdata,
                        "Google",
                        "Chrome",
                        "User Data",
                        "Default",
                        "Cache",
                    )
                )
                # Firefox
                locations.append(
                    os.path.join(local_appdata, "Mozilla", "Firefox", "Profiles")
                )
                # Edge
                locations.append(
                    os.path.join(
                        local_appdata,
                        "Microsoft",
                        "Edge",
                        "User Data",
                        "Default",
                        "Cache",
                    )
                )
                # Opera
                locations.append(
                    os.path.join(
                        local_appdata, "Opera Software", "Opera Stable", "Cache"
                    )
                )
                # Brave
                locations.append(
                    os.path.join(
                        local_appdata,
                        "BraveSoftware",
                        "Brave-Browser",
                        "User Data",
                        "Default",
                        "Cache",
                    )
                )
                # Vivaldi
                locations.append(
                    os.path.join(
                        local_appdata, "Vivaldi", "User Data", "Default", "Cache"
                    )
                )
        return [loc for loc in locations if os.path.exists(loc)]

    def scan(self) -> Tuple[int, int]:
        """Scan browser caches"""
        self.files_to_clean = []
        self.total_size = 0
        self.total_count = 0

        for cache_dir in self.cache_locations:
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
        """Clean browser caches"""
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

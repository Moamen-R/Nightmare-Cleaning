"""
Temporary files cleaning module
"""
import os
import tempfile
from pathlib import Path
from typing import Tuple
from . import CleaningModule


class TempFilesCleaner(CleaningModule):
    """Clean temporary files from various locations"""

    def __init__(self):
        super().__init__()
        self.description = "Temporary files and folders"
        self.temp_locations = [
            tempfile.gettempdir(),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp') if os.name == 'nt' else None,
            os.path.join(os.environ.get('WINDIR', ''), 'Temp') if os.name == 'nt' else None,
        ]
        # Remove None values
        self.temp_locations = [loc for loc in self.temp_locations if loc]

    def scan(self) -> Tuple[int, int]:
        """Scan for temporary files"""
        self.files_to_clean = []
        self.total_size = 0
        self.total_count = 0

        for temp_dir in self.temp_locations:
            if not os.path.exists(temp_dir):
                continue

            try:
                for item in os.listdir(temp_dir):
                    item_path = os.path.join(temp_dir, item)
                    try:
                        size = self.get_file_size(item_path)
                        self.files_to_clean.append(item_path)
                        self.total_size += size
                        self.total_count += 1
                    except (PermissionError, OSError):
                        continue
            except (PermissionError, OSError):
                continue

        return self.total_count, self.total_size

    def clean(self, dry_run=False) -> Tuple[int, int]:
        """Clean temporary files"""
        cleaned_count = 0
        cleaned_size = 0

        for filepath in self.files_to_clean:
            try:
                size = self.get_file_size(filepath)
                if self.safe_delete(filepath, dry_run):
                    cleaned_count += 1
                    cleaned_size += size
            except (PermissionError, OSError):
                continue

        return cleaned_count, cleaned_size

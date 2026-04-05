"""
User Temp files cleaning module
"""
import os
import tempfile
from typing import Tuple
from . import CleaningModule


class UserTempCleaner(CleaningModule):
    """Clean user temporary files"""

    def __init__(self):
        super().__init__()
        self.description = "User Temp files"
        self.temp_locations = []
        # User temp directory
        self.temp_locations.append(tempfile.gettempdir())
        if os.name == 'nt':
            localappdata = os.environ.get('LOCALAPPDATA', '')
            if localappdata:
                user_temp = os.path.join(localappdata, 'Temp')
                if user_temp not in self.temp_locations:
                    self.temp_locations.append(user_temp)
        # Remove None values and duplicates
        self.temp_locations = list(set([loc for loc in self.temp_locations if loc]))

    def scan(self) -> Tuple[int, int]:
        """Scan for user temporary files"""
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

    def clean(self, dry_run=False, secure=False) -> Tuple[int, int]:
        """Clean user temporary files"""
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

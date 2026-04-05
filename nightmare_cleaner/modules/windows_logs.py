"""
Windows Logs cleaning module
"""
import os
from typing import Tuple
from . import CleaningModule


class WindowsLogsCleaner(CleaningModule):
    """Clean Windows Log files"""

    def __init__(self):
        super().__init__()
        self.description = "Windows Log files"
        self.log_locations = []
        if os.name == 'nt':
            windir = os.environ.get('WINDIR', 'C:\\Windows')
            # Windows Log file locations
            self.log_locations.append(os.path.join(windir, 'Logs'))
            self.log_locations.append(os.path.join(windir, 'Temp'))
            self.log_locations.append(os.path.join(windir, 'Panther'))

    def scan(self) -> Tuple[int, int]:
        """Scan Windows Log files"""
        self.files_to_clean = []
        self.total_size = 0
        self.total_count = 0

        for log_dir in self.log_locations:
            if not os.path.exists(log_dir):
                continue

            try:
                for root, dirs, files in os.walk(log_dir):
                    for file in files:
                        # Only target log files
                        if file.endswith(('.log', '.etl', '.txt')):
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
        """Clean Windows Log files"""
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

"""
Windows Error Reports cleaning module
"""
import os
from typing import Tuple
from . import CleaningModule


class WindowsErrorReportsCleaner(CleaningModule):
    """Clean Windows Error Reports"""

    def __init__(self):
        super().__init__()
        self.description = "Windows Error Reports"
        self.error_locations = []
        if os.name == 'nt':
            programdata = os.environ.get('PROGRAMDATA', 'C:\\ProgramData')
            localappdata = os.environ.get('LOCALAPPDATA', '')
            # Windows Error Reporting locations
            self.error_locations.append(
                os.path.join(programdata, 'Microsoft', 'Windows', 'WER')
            )
            if localappdata:
                self.error_locations.append(
                    os.path.join(localappdata, 'Microsoft', 'Windows', 'WER')
                )

    def scan(self) -> Tuple[int, int]:
        """Scan Windows Error Reports"""
        self.files_to_clean = []
        self.total_size = 0
        self.total_count = 0

        for error_dir in self.error_locations:
            if not os.path.exists(error_dir):
                continue

            try:
                for root, dirs, files in os.walk(error_dir):
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
        """Clean Windows Error Reports"""
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

"""
Windows prefetch cleaning module
"""
import os
from typing import Tuple
from . import CleaningModule


class PrefetchCleaner(CleaningModule):
    """Clean Windows Prefetch files"""

    def __init__(self):
        super().__init__()
        self.description = "Windows Prefetch files"
        self.prefetch_dir = None
        if os.name == 'nt':
            windir = os.environ.get('WINDIR', 'C:\\Windows')
            self.prefetch_dir = os.path.join(windir, 'Prefetch')

    def scan(self) -> Tuple[int, int]:
        """Scan prefetch files"""
        self.files_to_clean = []
        self.total_size = 0
        self.total_count = 0

        if not self.prefetch_dir or not os.path.exists(self.prefetch_dir):
            return 0, 0

        try:
            for file in os.listdir(self.prefetch_dir):
                if file.endswith('.pf'):
                    filepath = os.path.join(self.prefetch_dir, file)
                    try:
                        size = self.get_file_size(filepath)
                        self.files_to_clean.append(filepath)
                        self.total_size += size
                        self.total_count += 1
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            pass

        return self.total_count, self.total_size

    def clean(self, dry_run=False) -> Tuple[int, int]:
        """Clean prefetch files"""
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

"""
Delivery Optimization cache cleaning module
"""
import os
from typing import Tuple
from . import CleaningModule


class DeliveryOptimizationCleaner(CleaningModule):
    """Clean Windows Delivery Optimization cache"""

    def __init__(self):
        super().__init__()
        self.description = "Delivery Optimization cache"
        self.cache_locations = []
        if os.name == 'nt':
            windir = os.environ.get('WINDIR', 'C:\\Windows')
            # Delivery Optimization cache location
            self.cache_locations.append(
                os.path.join(windir, 'SoftwareDistribution', 'DeliveryOptimization')
            )
            # Alternative location
            programdata = os.environ.get('PROGRAMDATA', 'C:\\ProgramData')
            self.cache_locations.append(
                os.path.join(programdata, 'Microsoft', 'Windows', 'DeliveryOptimization')
            )

    def scan(self) -> Tuple[int, int]:
        """Scan Delivery Optimization cache"""
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

    def clean(self, dry_run=False) -> Tuple[int, int]:
        """Clean Delivery Optimization cache"""
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

"""
C Drive root cleaning module – removes common Windows junk from C:\\
"""

import os
from pathlib import Path
from typing import Tuple, List
from . import CleaningModule


# Directories commonly left behind on C:\ that are safe to remove
# Paths are relative to the drive root (e.g. C:\\)
_JUNK_DIRS: List[str] = [
    "Windows.old",          # Previous Windows installation
    "Windows.old.000",      # Multiple old installations
    "Windows.old.001",
    "$Windows.~BT",         # Windows upgrade staging files
    "$Windows.~WS",         # Windows upgrade workspace
    "$WINDOWS.~Q",          # Windows upgrade temp
    "MSOCache",             # Microsoft Office local cache
    "AMD",                  # AMD driver install leftovers
    "NVIDIA",               # NVIDIA driver install leftovers
    "Intel",                # Intel driver install leftovers
    "OneDriveTemp",         # OneDrive temp staging
    "PerfLogs",             # Performance logs (safe to clear)
    "ESD",                  # Enterprise Software Deployment temp
    "$SysReset",            # System reset residue
    "Recovery",             # Sometimes safe orphaned recovery folders
]

# Files on C:\ root commonly left by installers
_JUNK_FILES: List[str] = [
    "bootmgr.efi.bak",
    "setup.log",
    "install.log",
    "setup.exe.log",
]


def _get_drive_root() -> str:
    """Return the system drive root (e.g. C:\\)."""
    return os.environ.get("SystemDrive", "C:") + "\\"


class CDriveCleaner(CleaningModule):
    """Clean common Windows junk and leftover installer files from the C: drive root"""

    def __init__(self):
        super().__init__()
        self.description = "C Drive root junk (Windows.old, installer leftovers, driver dumps)"
        self._drive_root = _get_drive_root()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _collect_targets(self) -> List[str]:
        """Return a list of absolute paths that exist and are safe to remove."""
        targets: List[str] = []

        # Known junk directories
        for name in _JUNK_DIRS:
            path = os.path.join(self._drive_root, name)
            if os.path.exists(path):
                targets.append(path)

        # Known junk files
        for name in _JUNK_FILES:
            path = os.path.join(self._drive_root, name)
            if os.path.isfile(path):
                targets.append(path)

        return targets

    # ------------------------------------------------------------------
    # CleaningModule interface
    # ------------------------------------------------------------------

    def scan(self) -> Tuple[int, int]:
        """Scan C:\\ for known junk directories and files."""
        self.files_to_clean = []
        self.total_size = 0
        self.total_count = 0

        for target in self._collect_targets():
            try:
                size = self.get_file_size(target)
                self.files_to_clean.append(target)
                self.total_size += size
                self.total_count += 1
            except (PermissionError, OSError):
                continue

        return self.total_count, self.total_size

    def clean(self, dry_run: bool = False, secure: bool = False) -> Tuple[int, int]:
        """Remove junk from C:\\ root."""
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

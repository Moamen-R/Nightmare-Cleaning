"""
Security and path validation module
"""

import os
import re
from pathlib import Path
from typing import Union

# System-critical directories that should NEVER be cleaned or modified
CRITICAL_SYSTEM_PATHS = [
    os.environ.get("WINDIR", "C:\\Windows"),
    os.environ.get("PROGRAMFILES", "C:\\Program Files"),
    os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
    os.environ.get("SYSTEMDRIVE", "C:") + "\\",
    os.environ.get("USERPROFILE", "C:\\Users\\Default"),
]

# Sensitive file extensions that should be preserved unless explicitly targeted
SENSITIVE_EXTENSIONS = {
    ".sys",
    ".dll",
    ".exe",
    ".bat",
    ".cmd",
    ".ps1",
    ".ini",
    ".cfg",
    ".conf",
    ".json",
    ".yaml",
    ".xml",
}


class SecurityError(Exception):
    """Raised when a security violation is detected"""

    pass


def normalize_path(path: Union[str, Path]) -> str:
    """Normalize a path to its absolute, resolved form"""
    try:
        return str(Path(path).resolve())
    except Exception:
        return str(path)


def is_safe_path(path: Union[str, Path], allowed_bases: list[str] = None) -> bool:
    """
    Check if a path is safe to operate on.

    Args:
        path: The path to check
        allowed_bases: Optional list of allowed base directories

    Returns:
        bool: True if safe, False otherwise
    """
    if not path:
        return False

    norm_path = normalize_path(path)

    # 1. Prevent directory traversal attacks
    if ".." in str(path) or norm_path != os.path.abspath(path):
        return False

    # 2. Check against critical system paths
    for critical_path in CRITICAL_SYSTEM_PATHS:
        if not critical_path:
            continue

        norm_critical = normalize_path(critical_path)
        # Cannot delete the critical directory itself or its immediate root files
        if norm_path == norm_critical or os.path.dirname(norm_path) == norm_critical:
            # Allow targeted cleaning inside specific subdirectories of Windows (like Temp or SoftwareDistribution)
            # but not arbitrary files
            if norm_path.lower().startswith(
                os.path.join(norm_critical.lower(), "temp")
            ) or norm_path.lower().startswith(
                os.path.join(norm_critical.lower(), "softwaredistribution")
            ):
                pass
            else:
                return False

    # 3. Restrict to allowed base directories if specified
    if allowed_bases:
        is_allowed = False
        for base in allowed_bases:
            if not base:
                continue
            norm_base = normalize_path(base)
            if norm_path.lower().startswith(norm_base.lower()):
                is_allowed = True
                break

        if not is_allowed:
            return False

    return True


def is_safe_extension(path: Union[str, Path]) -> bool:
    """Check if the file extension is safe to delete"""
    ext = os.path.splitext(str(path))[1].lower()
    return ext not in SENSITIVE_EXTENSIONS


def sanitize_input(user_input: str) -> str:
    """Normalize user confirmation input to lowercase stripped string.

    Only used for yes/no confirmation prompts — no regex needed.
    """
    return str(user_input).strip().lower()

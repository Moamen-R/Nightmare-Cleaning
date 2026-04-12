"""
Program uninstaller module for Nightmare Cleaner.

Scans the Windows registry for installed programs and provides
normal and force uninstall capabilities with leftover cleanup.
"""

import os
import sys
import subprocess
import shutil
from typing import List, Dict, Tuple, Optional

from ..security import is_safe_path, sanitize_input
from ..audit_logger import log_deletion, log_blocked, log_error, get_logger

# Protected programs that should NEVER be uninstalled (case-insensitive match)
PROTECTED_PROGRAMS = [
    "python",
    "pip",
    "nightmare",
    "windows",
    "microsoft",
    ".net",
    "visual c++",
    "directx",
    "nvidia driver",
    "amd driver",
    "intel driver",
]

# Registry paths to scan for installed programs
REGISTRY_UNINSTALL_PATHS = [
    (r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", "HKLM"),
    (r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall", "HKLM"),
    (r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", "HKCU"),
]


class ProgramUninstaller:
    """Scan, uninstall, and clean up installed Windows programs."""

    def __init__(self):
        self.name = "ProgramUninstaller"
        self.description = "Program Uninstaller"
        self.logger = get_logger()

    def _is_protected(self, program_name: str) -> bool:
        """Check if a program is in the protected list."""
        name_lower = program_name.lower()
        return any(protected in name_lower for protected in PROTECTED_PROGRAMS)

    def get_installed_programs(self) -> List[Dict]:
        """
        Scan the Windows registry for installed programs.

        Scans three registry hives:
          - HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall
          - HKLM\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall
          - HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall

        Returns:
            Sorted list of dicts, each containing:
              name, publisher, size_bytes, install_date,
              uninstall_string, install_location, registry_key
        """
        try:
            import winreg
        except ImportError:
            return []

        programs = []
        seen_names = set()  # For deduplication (case-insensitive)

        for reg_path, hive_name in REGISTRY_UNINSTALL_PATHS:
            hive = winreg.HKEY_LOCAL_MACHINE if hive_name == "HKLM" else winreg.HKEY_CURRENT_USER

            try:
                with winreg.OpenKey(hive, reg_path) as key:
                    subkey_count = winreg.QueryInfoKey(key)[0]

                    for i in range(subkey_count):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            subkey_path = f"{reg_path}\\{subkey_name}"

                            with winreg.OpenKey(hive, subkey_path) as subkey:
                                program = self._read_program_info(
                                    subkey, hive_name, subkey_path
                                )

                                if program is None:
                                    continue

                                # Deduplicate by name (case-insensitive)
                                name_key = program["name"].lower().strip()
                                if name_key in seen_names:
                                    continue

                                seen_names.add(name_key)
                                programs.append(program)

                        except (OSError, WindowsError):
                            continue

            except (OSError, WindowsError):
                # Hive or path not accessible — skip silently
                continue

        # Sort alphabetically by name
        programs.sort(key=lambda p: p["name"].lower())
        return programs

    def _read_program_info(self, subkey, hive_name: str, subkey_path: str) -> Optional[Dict]:
        """
        Read program metadata from a single registry subkey.

        Returns None if the entry has no DisplayName or no UninstallString.
        """
        try:
            import winreg
        except ImportError:
            return None

        def _get_value(key, value_name, default=None):
            """Safely read a registry value, returning default on failure."""
            try:
                return winreg.QueryValueEx(key, value_name)[0]
            except (OSError, FileNotFoundError):
                return default

        # DisplayName is required — skip entries without it
        display_name = _get_value(subkey, "DisplayName")
        if not display_name or not display_name.strip():
            return None

        # UninstallString is required — skip entries without it
        uninstall_string = _get_value(subkey, "UninstallString")
        if not uninstall_string or not uninstall_string.strip():
            return None

        # EstimatedSize is in KB → convert to bytes
        estimated_size_kb = _get_value(subkey, "EstimatedSize", 0)
        try:
            size_bytes = int(estimated_size_kb) * 1024
        except (ValueError, TypeError):
            size_bytes = 0

        # Install date: prefer DisplayVersion, fall back to InstallDate
        install_date = _get_value(subkey, "DisplayVersion")
        if not install_date:
            install_date = _get_value(subkey, "InstallDate", "N/A")

        publisher = _get_value(subkey, "Publisher", "Unknown")
        install_location = _get_value(subkey, "InstallLocation", "")

        # Fallback: if registry has no size, calculate from install directory
        if size_bytes == 0 and install_location and os.path.isdir(install_location):
            try:
                size_bytes = self._get_dir_size(install_location)
            except Exception:
                size_bytes = 0

        # Build full registry key path for later deletion
        registry_key = f"{hive_name}\\{subkey_path}"

        return {
            "name": display_name.strip(),
            "publisher": publisher if publisher else "Unknown",
            "size_bytes": size_bytes,
            "install_date": install_date if install_date else "N/A",
            "uninstall_string": uninstall_string.strip(),
            "install_location": install_location if install_location else "",
            "registry_key": registry_key,
        }

    def normal_uninstall(self, program: Dict) -> bool:
        """
        Run the program's official uninstaller via subprocess.

        - If the uninstall string contains 'msiexec', run silently with /qn.
        - Otherwise, run the command as-is and wait for completion.

        Args:
            program: Program dict from get_installed_programs()

        Returns:
            True on success, False on failure. Never raises.
        """
        uninstall_cmd = program.get("uninstall_string", "")
        if not uninstall_cmd:
            return False

        try:
            if "msiexec" in uninstall_cmd.lower():
                # MSI-based installer — run silently
                # Replace /I with /X for uninstall if present
                cmd = uninstall_cmd.replace("/I", "/X").replace("/i", "/X")
                # Add silent flag if not already present
                if "/qn" not in cmd.lower():
                    cmd += " /qn"
                self.logger.info(
                    f"{self.name} | NORMAL_UNINSTALL | {program['name']} | MSI silent mode"
                )
                result = subprocess.run(
                    cmd, shell=True, timeout=300,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            else:
                # Standard uninstaller — run and wait
                self.logger.info(
                    f"{self.name} | NORMAL_UNINSTALL | {program['name']} | Standard mode"
                )
                result = subprocess.run(
                    uninstall_cmd, shell=True, timeout=300,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )

            success = result.returncode == 0
            if success:
                self.logger.info(
                    f"{self.name} | UNINSTALL_SUCCESS | {program['name']}"
                )
            else:
                self.logger.warning(
                    f"{self.name} | UNINSTALL_FAILED | {program['name']} | "
                    f"exit_code={result.returncode}"
                )
            return success

        except subprocess.TimeoutExpired:
            self.logger.error(
                f"{self.name} | UNINSTALL_TIMEOUT | {program['name']} | 300s limit"
            )
            return False
        except Exception as e:
            self.logger.error(
                f"{self.name} | UNINSTALL_ERROR | {program['name']} | {type(e).__name__}"
            )
            return False

    def force_uninstall(self, program: Dict) -> Dict:
        """
        Aggressively remove a program by killing processes, deleting files,
        and cleaning all leftovers.

        Steps:
            1. Kill all running processes matching the program.
            2. Delete the install directory (if safe).
            3. Run clean_leftovers() for full cleanup.

        Args:
            program: Program dict from get_installed_programs()

        Returns:
            Dict with keys: processes_killed, files_deleted, registry_removed
        """
        results = {
            "processes_killed": 0,
            "files_deleted": 0,
            "registry_removed": 0,
            "space_freed": 0,
        }

        program_name = program.get("name", "")
        install_location = program.get("install_location", "")

        # --- Step 1: Kill related processes ---
        results["processes_killed"] = self._kill_related_processes(
            program_name, install_location
        )

        # --- Step 2: Delete install directory ---
        if install_location and os.path.isdir(install_location):
            if is_safe_path(install_location):
                try:
                    # Calculate size before deletion
                    dir_size = self._get_dir_size(install_location)
                    shutil.rmtree(install_location, ignore_errors=True)

                    if not os.path.exists(install_location):
                        results["files_deleted"] += 1
                        results["space_freed"] += dir_size
                        self.logger.info(
                            f"{self.name} | FORCE_DELETE_DIR | {program_name} | "
                            f"{install_location} | {dir_size} bytes"
                        )
                    else:
                        self.logger.warning(
                            f"{self.name} | FORCE_DELETE_PARTIAL | {program_name} | "
                            f"{install_location}"
                        )
                except Exception as e:
                    log_error(
                        self.name, install_location, f"rmtree failed: {type(e).__name__}"
                    )
            else:
                log_blocked(
                    self.name, install_location, "Unsafe path — skipped force delete"
                )

        # --- Step 3: Clean all leftovers ---
        leftover_results = self.clean_leftovers(program)
        results["files_deleted"] += leftover_results.get("files_deleted", 0)
        results["registry_removed"] += leftover_results.get("registry_removed", 0)
        results["space_freed"] += leftover_results.get("space_freed", 0)

        return results

    def _kill_related_processes(self, program_name: str, install_location: str) -> int:
        """
        Kill all running processes related to a program.

        Matches by:
          - Executable path containing the install_location
          - Process name loosely matching the program name

        Returns:
            Number of processes killed.
        """
        try:
            import psutil
        except ImportError:
            self.logger.warning(
                f"{self.name} | PSUTIL_MISSING | Cannot kill processes"
            )
            return 0

        killed = 0
        # Build simple match tokens from program name (e.g., "Visual Studio Code" → ["visual", "studio", "code"])
        name_tokens = [t.lower() for t in program_name.split() if len(t) > 2]

        for proc in psutil.process_iter(["pid", "name", "exe"]):
            try:
                proc_name = (proc.info.get("name") or "").lower()
                proc_exe = (proc.info.get("exe") or "").lower()

                matched = False

                # Match by install location
                if install_location and install_location.lower() in proc_exe:
                    matched = True

                # Match by process name containing significant tokens of the program name
                if not matched and name_tokens:
                    # Require at least the first significant token to match
                    if any(token in proc_name for token in name_tokens):
                        matched = True

                if matched:
                    proc.kill()
                    killed += 1
                    self.logger.info(
                        f"{self.name} | KILL_PROCESS | {proc.info['name']} | "
                        f"PID={proc.info['pid']}"
                    )

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception:
                continue

        return killed

    def _get_dir_size(self, path: str) -> int:
        """Calculate total size of a directory in bytes."""
        total = 0
        try:
            for dirpath, _, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        total += os.path.getsize(fp)
                    except (OSError, FileNotFoundError):
                        continue
        except (OSError, FileNotFoundError):
            pass
        return total

    def clean_leftovers(self, program: Dict) -> Dict:
        """
        Scan and remove ALL leftover files and registry entries for a program.

        File system locations cleaned:
          - %APPDATA%\\{program_name}
          - %LOCALAPPDATA%\\{program_name}
          - %PROGRAMDATA%\\{program_name}
          - Remaining items in install_location (if exists and safe)

        Registry locations cleaned:
          - The program's own registry_key
          - HKCU\\SOFTWARE\\{publisher}\\{name}
          - HKLM\\SOFTWARE\\{publisher}\\{name}
          - Startup entries in HKLM and HKCU Run keys

        Args:
            program: Program dict from get_installed_programs()

        Returns:
            Dict with keys: files_deleted, registry_removed, space_freed
        """
        results = {
            "files_deleted": 0,
            "registry_removed": 0,
            "space_freed": 0,
        }

        program_name = program.get("name", "")
        publisher = program.get("publisher", "")
        install_location = program.get("install_location", "")
        registry_key = program.get("registry_key", "")

        # --- File system cleanup ---
        appdata = os.environ.get("APPDATA", "")
        localappdata = os.environ.get("LOCALAPPDATA", "")
        programdata = os.environ.get("PROGRAMDATA", "")

        leftover_dirs = []
        if appdata:
            leftover_dirs.append(os.path.join(appdata, program_name))
        if localappdata:
            leftover_dirs.append(os.path.join(localappdata, program_name))
        if programdata:
            leftover_dirs.append(os.path.join(programdata, program_name))
        if install_location and os.path.isdir(install_location):
            leftover_dirs.append(install_location)

        for dir_path in leftover_dirs:
            if not os.path.isdir(dir_path):
                continue

            if not is_safe_path(dir_path):
                log_blocked(self.name, dir_path, "Unsafe path — skipped leftover cleanup")
                continue

            try:
                dir_size = self._get_dir_size(dir_path)
                shutil.rmtree(dir_path, ignore_errors=True)

                if not os.path.exists(dir_path):
                    results["files_deleted"] += 1
                    results["space_freed"] += dir_size
                    log_deletion(self.name, dir_path, dir_size)
                    self.logger.info(
                        f"{self.name} | LEFTOVER_DIR_REMOVED | {program_name} | "
                        f"{dir_path} | {dir_size} bytes"
                    )
            except Exception as e:
                log_error(self.name, dir_path, f"Leftover cleanup failed: {type(e).__name__}")

        # --- Registry cleanup ---
        results["registry_removed"] = self._clean_registry_leftovers(
            program_name, publisher, registry_key
        )

        return results

    def _clean_registry_leftovers(
        self, program_name: str, publisher: str, registry_key: str
    ) -> int:
        """
        Remove leftover registry entries for a program.

        Cleans:
          1. The program's own uninstall registry key
          2. HKCU\\SOFTWARE\\{publisher}\\{name}
          3. HKLM\\SOFTWARE\\{publisher}\\{name}
          4. Startup entries matching the program name

        Returns:
            Number of registry keys/values removed.
        """
        try:
            import winreg
        except ImportError:
            return 0

        removed = 0

        # 1. Delete the program's own registry key
        if registry_key:
            if self._delete_registry_key(registry_key):
                removed += 1

        # 2. Delete publisher\name keys in HKCU and HKLM
        if publisher and publisher != "Unknown":
            for hive_name in ("HKCU", "HKLM"):
                key_path = f"{hive_name}\\SOFTWARE\\{publisher}\\{program_name}"
                if self._delete_registry_key(key_path):
                    removed += 1

        # 3. Clean startup entries
        startup_paths = [
            ("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            ("HKCU", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        ]

        for hive_name, run_path in startup_paths:
            hive = (
                winreg.HKEY_LOCAL_MACHINE
                if hive_name == "HKLM"
                else winreg.HKEY_CURRENT_USER
            )

            try:
                with winreg.OpenKey(hive, run_path, 0, winreg.KEY_ALL_ACCESS) as key:
                    i = 0
                    while True:
                        try:
                            value_name, value_data, _ = winreg.EnumValue(key, i)
                            # Check if this startup entry matches the program name
                            if program_name.lower() in value_name.lower():
                                try:
                                    winreg.DeleteValue(key, value_name)
                                    removed += 1
                                    self.logger.info(
                                        f"{self.name} | STARTUP_REMOVED | "
                                        f"{value_name} | {hive_name}\\{run_path}"
                                    )
                                except OSError:
                                    pass
                            else:
                                i += 1
                        except OSError:
                            # No more values
                            break
            except OSError:
                # Can't open Run key — skip
                continue

        return removed

    def _delete_registry_key(self, full_key_path: str) -> bool:
        """
        Delete a registry key given its full path (e.g., 'HKLM\\SOFTWARE\\...').

        Handles recursive deletion of subkeys.
        Never raises — returns False on any failure.
        """
        try:
            import winreg
        except ImportError:
            return False

        try:
            # Parse hive and subkey path
            parts = full_key_path.split("\\", 1)
            if len(parts) != 2:
                return False

            hive_name, subkey_path = parts

            hive_map = {
                "HKLM": winreg.HKEY_LOCAL_MACHINE,
                "HKCU": winreg.HKEY_CURRENT_USER,
            }
            hive = hive_map.get(hive_name)
            if hive is None:
                return False

            # Try to delete the key (must delete subkeys first on Windows)
            self._delete_registry_tree(hive, subkey_path)
            self.logger.info(
                f"{self.name} | REGISTRY_REMOVED | {full_key_path}"
            )
            return True

        except OSError:
            return False
        except Exception:
            return False

    def _delete_registry_tree(self, hive, key_path: str) -> None:
        """
        Recursively delete a registry key and all its subkeys.
        Raises OSError if the key cannot be deleted.
        """
        try:
            import winreg
        except ImportError:
            return

        try:
            with winreg.OpenKey(hive, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
                # First, recursively delete all subkeys
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, 0)
                        self._delete_registry_tree(
                            hive, f"{key_path}\\{subkey_name}"
                        )
                    except OSError:
                        break

            # Now delete the key itself
            winreg.DeleteKey(hive, key_path)
        except OSError:
            raise

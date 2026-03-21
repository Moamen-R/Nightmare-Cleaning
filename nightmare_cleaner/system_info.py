"""
System information utilities
"""
import os
import platform
import psutil
from typing import Dict


def get_system_info() -> Dict:
    """Get system information"""
    info = {
        'os': platform.system(),
        'os_version': platform.version(),
        'os_release': platform.release(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'hostname': platform.node(),
        'python_version': platform.python_version(),
    }
    return info


def get_disk_info() -> Dict:
    """Get disk usage information"""
    disk_info = {}
    try:
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info[partition.device] = {
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                }
            except (PermissionError, OSError):
                continue
    except Exception:
        pass
    return disk_info


def get_memory_info() -> Dict:
    """Get memory information"""
    try:
        mem = psutil.virtual_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent
        }
    except Exception:
        return {}


def is_admin() -> bool:
    """Check if running with administrator privileges"""
    try:
        if os.name == 'nt':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False

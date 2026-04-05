"""
Audit logging module for Nightmare Cleaner
Records all cleaning operations with timestamps, file names, and sizes
for accountability and forensic analysis.
"""

import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler


def get_log_dir() -> str:
    """Get the platform-specific log directory"""
    if os.name == "nt":
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            return os.path.join(appdata, "NightmareCleaner", "logs")
    return os.path.join(os.path.expanduser("~"), ".nightmare_cleaner", "logs")


def setup_audit_logger() -> logging.Logger:
    """
    Set up and return the audit logger with rotation.
    
    Log files are written to:
      - Windows: %APPDATA%\\NightmareCleaner\\logs\\
      - Other:   ~/.nightmare_cleaner/logs/
    
    Logs are rotated at 5MB with 10 backup files retained.
    """
    log_dir = get_log_dir()
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(
        log_dir, f"clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    logger = logging.getLogger("nightmare_audit")

    # Prevent duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=10,
        encoding="utf-8",
    )

    # Log format: timestamp | level | module | action | filename | size
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

    logger.addHandler(handler)

    return logger


# Global audit logger instance (lazy-initialized)
_audit_logger = None


def get_logger() -> logging.Logger:
    """Get or create the global audit logger"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = setup_audit_logger()
    return _audit_logger


def log_deletion(module: str, filename: str, size: int, secure: bool = False) -> None:
    """Log a file deletion event"""
    mode = "SECURE_DELETE" if secure else "DELETE"
    get_logger().info(f"{module} | {mode} | {filename} | {size} bytes")


def log_blocked(module: str, filename: str, reason: str) -> None:
    """Log a blocked deletion attempt"""
    get_logger().warning(f"{module} | BLOCKED | {filename} | {reason}")


def log_error(module: str, filename: str, error: str) -> None:
    """Log a deletion error"""
    get_logger().error(f"{module} | ERROR | {filename} | {error}")


def log_session_start(modules: list, dry_run: bool, secure: bool) -> None:
    """Log the start of a cleaning session"""
    mode = []
    if dry_run:
        mode.append("DRY_RUN")
    if secure:
        mode.append("SECURE")
    mode_str = " | ".join(mode) if mode else "NORMAL"
    get_logger().info(f"SESSION_START | modules={','.join(modules)} | mode={mode_str}")


def log_session_end(total_cleaned: int, total_size: int, duration: float) -> None:
    """Log the end of a cleaning session"""
    get_logger().info(
        f"SESSION_END | cleaned={total_cleaned} | "
        f"size={total_size} bytes | duration={duration:.1f}s"
    )

"""
Main CLI interface for Nightmare Cleaner
"""

import click
import sys
import subprocess
from .ui import (
    print_banner,
    print_section_header,
    print_info,
    print_success,
    print_warning,
    print_error,
    create_progress_bar,
    print_stats_table,
    create_table,
    console,
    confirm_action,
    format_size,
)
from .system_info import get_system_info, get_disk_info, get_memory_info, is_admin
from .modules.temp_cleaner import TempFilesCleaner
from .modules.browser_cache import BrowserCacheCleaner
from .modules.recycle_bin import RecycleBinCleaner
from .modules.prefetch import PrefetchCleaner
from .modules.thumbnail_cache import ThumbnailCacheCleaner
from .modules.windows_update import WindowsUpdateCacheCleaner
from .modules.error_reports import WindowsErrorReportsCleaner
from .modules.windows_logs import WindowsLogsCleaner
from .modules.delivery_optimization import DeliveryOptimizationCleaner
from .modules.disk_cleanup import DiskCleanupCleaner
from .modules.dns_cache import DNSCacheCleaner
from .modules.store_cache import WindowsStoreCacheCleaner
from .modules.windows_temp import WindowsTempCleaner
from .modules.user_temp import UserTempCleaner
from .modules.memory_cleaner import MemoryCleaner
from .modules.font_cache import FontCacheCleaner
from .security import sanitize_input
from .audit_logger import log_session_start, log_session_end
import time


PACKAGE_NAME = "nightmare-cleaner"


def check_for_update():
    """Check PyPI for the latest version and upgrade if available."""
    from . import __version__

    console.print(f"\n[bold magenta]Current version:[/bold magenta] v{__version__}")
    console.print("[info]Checking PyPI for the latest version...[/info]")

    try:
        import json
        from urllib.request import urlopen, Request
        from urllib.error import URLError

        url = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            latest_version = data["info"]["version"]
    except Exception:
        print_error("Could not reach PyPI. Check your internet connection.")
        return

    # Compare versions using packaging if available, else simple string compare
    try:
        from packaging.version import Version

        is_newer = Version(latest_version) > Version(__version__)
    except ImportError:
        is_newer = latest_version != __version__

    if not is_newer:
        print_success(
            f"You are already on the latest version (v{__version__}). No update needed."
        )
        return

    console.print(
        f"[bold green]New version available:[/bold green] v{latest_version} "
        f"(installed: v{__version__})"
    )

    # Ask for confirmation
    user_input = input("\nDo you want to update now? [y/N]: ").strip().lower()
    if user_input not in ("y", "yes"):
        print_warning("Update cancelled.")
        return

    # Perform the upgrade
    console.print("[info]Upgrading...[/info]")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", PACKAGE_NAME]
        )
        print_success(f"Successfully updated to v{latest_version}!")
    except subprocess.CalledProcessError:
        print_error(
            "Update failed. Try running manually:\n"
            f"  pip install --upgrade {PACKAGE_NAME}"
        )


# Available cleaning modules
CLEANING_MODULES = {
    "windows-temp": WindowsTempCleaner,
    "user-temp": UserTempCleaner,
    "browser": BrowserCacheCleaner,
    "windows-update": WindowsUpdateCacheCleaner,
    "prefetch": PrefetchCleaner,
    "recycle": RecycleBinCleaner,
    "error-reports": WindowsErrorReportsCleaner,
    "thumbnails": ThumbnailCacheCleaner,
    "logs": WindowsLogsCleaner,
    "delivery-optimization": DeliveryOptimizationCleaner,
    "disk-cleanup": DiskCleanupCleaner,
    "dns-cache": DNSCacheCleaner,
    "store-cache": WindowsStoreCacheCleaner,
    "memory": MemoryCleaner,
    "font-cache": FontCacheCleaner,
}

# Modules that require administrator privileges
PRIVILEGED_MODULES = {
    "prefetch",
    "windows-temp",
    "windows-update",
    "logs",
    "dns-cache",
    "disk-cleanup",
    "recycle",
}


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version information")
@click.option("--update", "-u", is_flag=True, help="Check for updates and upgrade to the latest version")
@click.pass_context
def main(ctx, version, update):
    """
    Nightmare Cleaner - A modular, high-performance Windows Cleaner and Optimizer

    A beautiful purple/magenta themed CLI tool for cleaning and optimizing Windows systems.
    """
    if version:
        from . import __version__

        console.print(f"[title]Nightmare Cleaner v{__version__}[/title]")
        return

    if update:
        print_banner()
        check_for_update()
        return

    if ctx.invoked_subcommand is None:
        print_banner()
        console.print("[info]Use --help to see available commands[/info]\n")


@main.command()
def info():
    """Display system information"""
    print_banner()
    print_section_header("SYSTEM INFORMATION")

    # System info
    sys_info = get_system_info()
    table = create_table("System Details", ["Property", "Value"])
    table.add_row("Operating System", f"{sys_info['os']} {sys_info['os_release']}")
    table.add_row("Version", sys_info["os_version"])
    table.add_row("Architecture", sys_info["architecture"])
    table.add_row("Processor", sys_info["processor"])
    table.add_row("Hostname", sys_info["hostname"])
    table.add_row("Python Version", sys_info["python_version"])
    table.add_row("Administrator", "Yes" if is_admin() else "No")
    console.print(table)

    # Memory info
    print_section_header("MEMORY INFORMATION")
    mem_info = get_memory_info()
    if mem_info:
        table = create_table("Memory Usage", ["Property", "Value"])
        table.add_row("Total", format_size(mem_info["total"]))
        table.add_row("Used", format_size(mem_info["used"]))
        table.add_row("Available", format_size(mem_info["available"]))
        table.add_row("Usage", f"{mem_info['percent']}%")
        console.print(table)

    # Disk info
    print_section_header("DISK INFORMATION")
    disk_info = get_disk_info()
    if disk_info:
        table = create_table(
            "Disk Usage", ["Drive", "Type", "Total", "Used", "Free", "Usage"]
        )
        for device, info in disk_info.items():
            table.add_row(
                info["mountpoint"],
                info["fstype"],
                format_size(info["total"]),
                format_size(info["used"]),
                format_size(info["free"]),
                f"{info['percent']}%",
            )
        console.print(table)


@main.command()
@click.option(
    "--module",
    "-m",
    multiple=True,
    type=click.Choice(list(CLEANING_MODULES.keys())),
    help="Specific module(s) to scan",
)
@click.option("--all", "scan_all", is_flag=True, help="Scan all modules")
def scan(module, scan_all):
    """Scan system for cleanable items"""
    print_banner()

    # Check admin rights
    if not is_admin():
        print_warning("Not running as administrator. Some features may be limited.")

    print_section_header("SCANNING SYSTEM")

    # Determine which modules to scan
    modules_to_scan = []
    if scan_all or not module:
        modules_to_scan = list(CLEANING_MODULES.keys())
    else:
        modules_to_scan = list(module)

    stats = {}

    with create_progress_bar("Scanning") as progress:
        task = progress.add_task(
            "[progress]Analyzing system...", total=len(modules_to_scan)
        )

        for mod_name in modules_to_scan:
            progress.update(task, description=f"[progress]Scanning {mod_name}...")

            try:
                cleaner = CLEANING_MODULES[mod_name]()
                count, size = cleaner.scan()
                stats[cleaner.description] = {"count": count, "size": size}
            except Exception as e:
                # Sanitize exception message to avoid leaking system paths
                error_msg = str(e).split(":")[0] if ":" in str(e) else str(e)
                print_error(f"Error scanning {mod_name}: {error_msg}")

            progress.advance(task)

    print_section_header("SCAN RESULTS")
    print_stats_table(stats)

    print_info("\nUse 'nightmare clean' to remove these items")


@main.command()
@click.option(
    "--module",
    "-m",
    multiple=True,
    type=click.Choice(list(CLEANING_MODULES.keys())),
    help="Specific module(s) to clean",
)
@click.option("--all", "clean_all", is_flag=True, help="Clean all modules")
@click.option(
    "--dry-run", is_flag=True, help="Simulate cleaning without actually deleting files"
)
@click.option("--secure", is_flag=True, help="Securely delete files (3 passes)")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def clean(module, clean_all, dry_run, secure, yes):
    """Clean system by removing temporary and unnecessary files"""
    print_banner()

    # Check admin rights
    if not is_admin():
        print_warning("Not running as administrator. Some operations may fail.")

    if secure:
        print_warning(
            "SECURE CLEANING ENABLED: Deletions will take longer to overwrite files."
        )

    if dry_run:
        print_info("DRY RUN MODE: No files will be deleted\n")

    # Determine which modules to clean
    modules_to_clean = []
    if clean_all or not module:
        modules_to_clean = list(CLEANING_MODULES.keys())
    else:
        modules_to_clean = list(module)

    # Block privileged modules when not running as admin
    if not is_admin():
        skipped = []
        filtered = []
        for mod_name in modules_to_clean:
            if mod_name in PRIVILEGED_MODULES:
                skipped.append(mod_name)
            else:
                filtered.append(mod_name)
        if skipped:
            print_warning(
                f"Skipping {len(skipped)} module(s) requiring admin: "
                + ", ".join(skipped)
            )
        modules_to_clean = filtered

    # First scan to show what will be cleaned
    print_section_header("ANALYZING SYSTEM")
    stats = {}
    cleaners = {}

    with create_progress_bar("Scanning") as progress:
        task = progress.add_task("[progress]Analyzing...", total=len(modules_to_clean))

        for mod_name in modules_to_clean:
            progress.update(task, description=f"[progress]Scanning {mod_name}...")

            try:
                cleaner = CLEANING_MODULES[mod_name]()
                count, size = cleaner.scan()
                stats[cleaner.description] = {"count": count, "size": size}
                cleaners[mod_name] = cleaner
            except Exception as e:
                # Sanitize exception message to avoid leaking system paths
                error_msg = str(e).split(":")[0] if ":" in str(e) else str(e)
                print_error(f"Error scanning {mod_name}: {error_msg}")

            progress.advance(task)

    print_section_header("ITEMS TO CLEAN")
    print_stats_table(stats)

    # Ask for confirmation
    if not yes and not dry_run:
        # Ask for confirmation and sanitize input
        user_input = input("\nProceed with cleaning? [y/N]: ")
        safe_input = sanitize_input(user_input).lower()
        if safe_input not in ["y", "yes"]:
            print_warning("Cleaning cancelled")
            return

    # Perform cleaning
    print_section_header("CLEANING SYSTEM")
    cleaned_stats = {}
    session_start = time.time()

    # Log session start
    log_session_start(modules_to_clean, dry_run, secure)

    with create_progress_bar("Cleaning") as progress:
        task = progress.add_task("[progress]Cleaning...", total=len(cleaners))

        for mod_name, cleaner in cleaners.items():
            progress.update(task, description=f"[progress]Cleaning {mod_name}...")

            try:
                count, size = cleaner.clean(dry_run=dry_run, secure=secure)
                cleaned_stats[cleaner.description] = {"count": count, "size": size}
            except Exception as e:
                # Sanitize exception message to avoid leaking system paths
                error_msg = str(e).split(":")[0] if ":" in str(e) else str(e)
                print_error(f"Error cleaning {mod_name}: {error_msg}")

            progress.advance(task)

    # Log session end
    duration = time.time() - session_start
    total_cleaned = sum(d.get("count", 0) for d in cleaned_stats.values())
    total_size = sum(d.get("size", 0) for d in cleaned_stats.values())
    log_session_end(total_cleaned, total_size, duration)

    print_section_header("CLEANING RESULTS")
    print_stats_table(cleaned_stats)

    if dry_run:
        print_info("\nDry run completed. No files were deleted.")
    else:
        print_success("\nCleaning completed successfully!")


@main.command()
def modules():
    """List available cleaning modules"""
    print_banner()
    print_section_header("AVAILABLE CLEANING MODULES")

    table = create_table("Cleaning Modules", ["Module ID", "Description"])

    for mod_id, mod_class in CLEANING_MODULES.items():
        cleaner = mod_class()
        table.add_row(mod_id, cleaner.description)

    console.print(table)
    print_info(
        "\nUse --module or -m to specify modules: nightmare scan -m temp -m browser"
    )


if __name__ == "__main__":
    main()

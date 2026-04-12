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
from .modules.cdrive_cleaner import CDriveCleaner
from .modules.uninstaller import ProgramUninstaller
from .security import sanitize_input
from .audit_logger import log_session_start, log_session_end, get_logger
import time


PACKAGE_NAME = "nightmare-cleaner"


GITHUB_REPO = "Moamen-R/Nightmare-Cleaning"


def check_for_update():
    """Check GitHub releases for the latest version."""
    from . import __version__

    console.print(f"\n[bold magenta]Current version:[/bold magenta] v{__version__}")
    console.print("[info]Checking GitHub for the latest version...[/info]")

    try:
        import json
        from urllib.request import urlopen, Request

        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        req = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "nightmare-cleaner"})
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            latest_version = data["tag_name"].lstrip("v")
    except Exception:
        print_error("Could not reach GitHub. Check your internet connection.")
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

    # Perform the upgrade via pip from GitHub
    console.print("[info]Upgrading from GitHub...[/info]")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade",
             f"git+https://github.com/{GITHUB_REPO}.git"]
        )
        print_success(f"Successfully updated to v{latest_version}!")
    except subprocess.CalledProcessError:
        print_error(
            "Update failed. Try running manually:\n"
            f"  pip install --upgrade git+https://github.com/{GITHUB_REPO}.git"
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
    "cdrive": CDriveCleaner,
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
    "cdrive",
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


@main.command()
@click.option("--search", "-s", default=None, help="Filter program list by name keyword")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompts")
def uninstall(search, yes):
    """Interactive program uninstaller with leftover cleanup"""
    print_banner()

    # Check for Windows
    if sys.platform != "win32":
        print_error("The uninstaller is only available on Windows.")
        return

    # Check admin
    if not is_admin():
        print_warning(
            "Not running as administrator. Some uninstalls may fail."
        )

    print_section_header("NIGHTMARE UNINSTALLER")

    uninstaller = ProgramUninstaller()
    audit = get_logger()

    while True:  # Main loop for "uninstall another?"
        # --- Scan registry ---
        programs = []
        with create_progress_bar("Scanning") as progress:
            task = progress.add_task(
                "[progress]Scanning installed programs...", total=1
            )
            programs = uninstaller.get_installed_programs()
            progress.advance(task)

        # --- Apply search filter ---
        if search:
            safe_search = sanitize_input(search)
            programs = [
                p for p in programs
                if safe_search in p["name"].lower()
            ]

        # --- Display program table ---
        if not programs:
            print_warning("No programs found.")
            return

        _display_program_table(programs)

        # --- Prompt for selection ---
        selected = _prompt_program_selection(programs)
        if selected is None:
            return

        program = programs[selected]

        # --- Safety check: protected program ---
        if uninstaller._is_protected(program["name"]):
            print_error(
                f"'{program['name']}' is a protected system component and cannot be uninstalled."
            )
            continue

        # --- Show confirmation panel ---
        detail_text = (
            f"[bright_cyan]Name:[/bright_cyan]       {program['name']}\n"
            f"[bright_cyan]Publisher:[/bright_cyan]  {program['publisher']}\n"
            f"[bright_cyan]Size:[/bright_cyan]       {format_size(program['size_bytes'])}\n"
            f"[bright_cyan]Version:[/bright_cyan]    {program['install_date']}\n"
            f"[bright_cyan]Location:[/bright_cyan]   {program['install_location'] or 'N/A'}"
        )
        from .ui import create_panel
        console.print(create_panel(detail_text, title="Selected Program"))

        # --- Prompt uninstall mode ---
        mode = _prompt_uninstall_mode()
        if mode is None:
            # Cancel → re-show the table
            continue

        # --- Confirm before proceeding ---
        if not yes:
            mode_label = "Normal" if mode == "normal" else "Force"
            if not confirm_action(
                f"Proceed with {mode_label} uninstallation of '{program['name']}'?"
            ):
                print_warning("Uninstallation cancelled.")
                continue

        # --- Execute uninstall ---
        audit.info(
            f"ProgramUninstaller | SESSION_START | {program['name']} | mode={mode}"
        )
        session_start = time.time()

        results = {"processes_killed": 0, "files_deleted": 0, "registry_removed": 0, "space_freed": 0}

        if mode == "normal":
            with create_progress_bar("Uninstalling") as progress:
                task = progress.add_task(
                    f"[progress]Uninstalling {program['name']}...", total=2
                )

                success = uninstaller.normal_uninstall(program)
                progress.advance(task)

                if success:
                    print_success(f"Normal uninstall of '{program['name']}' completed.")
                else:
                    print_warning(
                        f"Normal uninstall returned a non-zero exit code. "
                        f"Cleaning leftovers anyway..."
                    )

                # Always clean leftovers after normal uninstall
                leftover = uninstaller.clean_leftovers(program)
                results["files_deleted"] = leftover.get("files_deleted", 0)
                results["registry_removed"] = leftover.get("registry_removed", 0)
                results["space_freed"] = leftover.get("space_freed", 0)
                progress.advance(task)

        elif mode == "force":
            with create_progress_bar("Force Uninstalling") as progress:
                task = progress.add_task(
                    f"[progress]Force removing {program['name']}...", total=1
                )
                results = uninstaller.force_uninstall(program)
                progress.advance(task)

            print_success(f"Force uninstall of '{program['name']}' completed.")

        # --- Show summary panel ---
        duration = time.time() - session_start
        mode_label = "Normal" if mode == "normal" else "Force"
        summary_text = (
            f"[bright_cyan]Program:[/bright_cyan]          {program['name']}\n"
            f"[bright_cyan]Mode:[/bright_cyan]             {mode_label}\n"
            f"[bright_cyan]Processes Killed:[/bright_cyan] {results['processes_killed']}\n"
            f"[bright_cyan]Files Deleted:[/bright_cyan]    {results['files_deleted']}\n"
            f"[bright_cyan]Registry Removed:[/bright_cyan] {results['registry_removed']}\n"
            f"[bright_cyan]Space Freed:[/bright_cyan]      {format_size(results['space_freed'])}\n"
            f"[bright_cyan]Duration:[/bright_cyan]         {duration:.1f}s"
        )
        console.print(create_panel(summary_text, title="Uninstall Summary"))

        # --- Log the operation ---
        audit.info(
            f"ProgramUninstaller | SESSION_END | {program['name']} | "
            f"mode={mode} | killed={results['processes_killed']} | "
            f"files={results['files_deleted']} | registry={results['registry_removed']} | "
            f"freed={results['space_freed']} | duration={duration:.1f}s"
        )

        # --- Ask to uninstall another ---
        console.print()
        try:
            again = input("Uninstall another program? [y/N]: ")
            if sanitize_input(again) not in ("y", "yes"):
                print_info("Goodbye! 💀")
                return
        except (KeyboardInterrupt, EOFError):
            console.print("\n")
            print_info("Goodbye! 💀")
            return


def _display_program_table(programs):
    """Display installed programs in a numbered Rich table."""
    table = create_table(
        "Installed Programs",
        ["#", "Program Name", "Publisher", "Size", "Version"],
    )

    for idx, prog in enumerate(programs, 1):
        table.add_row(
            str(idx),
            prog["name"],
            prog["publisher"],
            format_size(prog["size_bytes"]),
            prog["install_date"],
        )

    console.print(table)
    console.print(f"\n[info]Total: {len(programs)} programs[/info]\n")


def _prompt_program_selection(programs):
    """
    Prompt user to select a program by number.
    Returns the 0-based index, or None to quit.
    """
    while True:
        try:
            raw = input("Enter program number to select (or 'q' to quit): ")
        except (KeyboardInterrupt, EOFError):
            console.print("\n")
            return None

        choice = sanitize_input(raw)
        if choice == "q":
            print_info("Exiting uninstaller.")
            return None

        try:
            num = int(choice)
            if 1 <= num <= len(programs):
                return num - 1
            else:
                print_warning(f"Please enter a number between 1 and {len(programs)}.")
        except ValueError:
            print_warning("Invalid input. Enter a number or 'q' to quit.")


def _prompt_uninstall_mode():
    """
    Prompt user to choose uninstall mode.
    Returns 'normal', 'force', or None (cancel).
    """
    console.print("\n[title]Select uninstall mode:[/title]")
    console.print("  [bright_cyan]1.[/bright_cyan] Normal Uninstallation - Uses the official uninstaller")
    console.print("  [bright_cyan]2.[/bright_cyan] Force Uninstallation  - Terminates processes & removes all files")
    console.print("  [bright_cyan]3.[/bright_cyan] Cancel\n")

    while True:
        try:
            raw = input("Enter choice (1/2/3): ")
        except (KeyboardInterrupt, EOFError):
            console.print("\n")
            return None

        choice = sanitize_input(raw)
        if choice == "1":
            return "normal"
        elif choice == "2":
            return "force"
        elif choice == "3":
            return None
        else:
            print_warning("Invalid choice. Enter 1, 2, or 3.")


if __name__ == "__main__":
    main()

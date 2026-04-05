"""
UI utilities for Nightmare Cleaner with purple/magenta theme
"""

import sys
import io

# Fix unicode output on Windows
if sys.platform == "nt":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from rich.console import Console
from rich.theme import Theme
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.panel import Panel
from rich import box
import colorama
from colorama import Fore, Style

# Initialize colorama for Windows color support
colorama.init(autoreset=True)

# Define purple/magenta color scheme
NIGHTMARE_THEME = Theme(
    {
        "info": "magenta",
        "success": "bright_magenta",
        "warning": "yellow",
        "error": "red",
        "highlight": "bright_cyan",
        "title": "bold bright_magenta",
        "subtitle": "magenta",
        "progress": "bright_magenta",
    }
)

# Create console with custom theme
console = Console(theme=NIGHTMARE_THEME)

# Color constants for direct use
PURPLE = Fore.MAGENTA
BRIGHT_PURPLE = Fore.LIGHTMAGENTA_EX
CYAN = Fore.CYAN
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
RED = Fore.RED
RESET = Style.RESET_ALL


def print_banner():
    """Print the Nightmare Cleaner banner"""
    banner = f"""
{BRIGHT_PURPLE}=================================================================
|                                                               |
|              N    N  N  NNNNNNN  N   N  NNNNNNNN              |
|              NN   N  N  N        N   N     N                  |
|              N N  N  N  N  NNNN  NNNNN     N                  |
|              N  N N  N  N     N  N   N     N                  |
|              N   NN  N  NNNNNNN  N   N     N                  |
|                                                               |
|              NIGHTMARE CLEANER & OPTIMIZER v1.0               |
|              Windows System Cleaner and Optimizer             |
|                                                               |
================================================================={RESET}
"""
    try:
        print(banner)
    except Exception:
        pass


def print_section_header(title):
    """Print a section header with purple theme"""
    console.print(f"\n[title]{'=' * 60}[/title]")
    console.print(f"[title]{title.center(60)}[/title]")
    console.print(f"[title]{'=' * 60}[/title]\n")


def print_info(message):
    """Print an info message with purple theme"""
    console.print(f"[info]i[/info] {message}")


def print_success(message):
    """Print a success message"""
    console.print(f"[success]OK[/success] {message}")


def print_warning(message):
    """Print a warning message"""
    console.print(f"[warning]![/warning] {message}")


def print_error(message):
    """Print an error message"""
    console.print(f"[error]X[/error] {message}")


def create_progress_bar(description="Processing"):
    """Create a progress bar with purple theme"""
    return Progress(
        SpinnerColumn(style="bright_magenta"),
        TextColumn("[progress]{task.description}"),
        BarColumn(complete_style="bright_magenta", finished_style="bright_magenta"),
        TextColumn("[progress]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
    )


def create_table(title, columns):
    """Create a table with purple theme"""
    table = Table(
        title=title,
        box=box.DOUBLE_EDGE,
        title_style="title",
        header_style="bright_magenta bold",
        border_style="magenta",
    )
    for col in columns:
        table.add_column(col, style="bright_cyan")
    return table


def create_panel(content, title="", border_style="magenta"):
    """Create a panel with purple theme"""
    return Panel(content, title=title, border_style=border_style, box=box.DOUBLE)


def print_stats_table(stats):
    """Print statistics in a formatted table"""
    table = create_table("Cleaning Statistics", ["Category", "Items", "Size"])

    total_items = 0
    total_size = 0

    for category, data in stats.items():
        items = data.get("count", 0)
        size = data.get("size", 0)
        total_items += items
        total_size += size

        table.add_row(category, str(items), format_size(size))

    table.add_section()
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{total_items}[/bold]",
        f"[bold]{format_size(total_size)}[/bold]",
    )

    console.print(table)


def format_size(bytes_size):
    """Format bytes to human-readable size"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def confirm_action(message, default=False):
    """Ask for user confirmation with purple theme"""
    default_text = "Y/n" if default else "y/N"
    console.print(f"[warning]?[/warning] {message} [{default_text}]: ", end="")
    try:
        response = input().strip().lower()
        if not response:
            return default
        return response in ["y", "yes"]
    except (KeyboardInterrupt, EOFError):
        console.print("\n[error]Operation cancelled by user[/error]")
        return False

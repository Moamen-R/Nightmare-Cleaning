#!/usr/bin/env python3
"""
Example usage of Nightmare Cleaner
"""

# Example 1: Using the CLI programmatically
import subprocess
import sys

def run_nightmare_cleaner():
    """Examples of running Nightmare Cleaner commands"""

    print("=" * 60)
    print("Nightmare Cleaner - Usage Examples")
    print("=" * 60)

    # Example 1: Show version
    print("\n1. Show version:")
    print("   $ nightmare-cleaner --version")

    # Example 2: Display system information
    print("\n2. Display system information:")
    print("   $ nightmare-cleaner info")

    # Example 3: List available modules
    print("\n3. List available cleaning modules:")
    print("   $ nightmare-cleaner modules")

    # Example 4: Scan specific modules
    print("\n4. Scan specific modules (temp and browser):")
    print("   $ nightmare-cleaner scan -m temp -m browser")

    # Example 5: Scan all modules
    print("\n5. Scan all modules:")
    print("   $ nightmare-cleaner scan --all")

    # Example 6: Clean with dry-run (safe preview)
    print("\n6. Clean with dry-run (preview without deletion):")
    print("   $ nightmare-cleaner clean --all --dry-run")

    # Example 7: Clean specific modules
    print("\n7. Clean specific modules:")
    print("   $ nightmare-cleaner clean -m temp -m thumbnails")

    # Example 8: Clean all with auto-confirmation
    print("\n8. Clean all with auto-confirmation:")
    print("   $ nightmare-cleaner clean --all -y")

    print("\n" + "=" * 60)
    print("For more information, run: nightmare-cleaner --help")
    print("=" * 60)

if __name__ == "__main__":
    run_nightmare_cleaner()

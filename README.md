# Nightmare Cleaner 🌙

A modular, high-performance Windows Cleaner and Optimizer CLI tool built with Python, featuring a beautiful purple/magenta themed UI.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Version](https://img.shields.io/badge/version-1.2.0-brightgreen.svg)

##  Features

- Beautiful Purple/Magenta UI**: Eye-catching terminal interface with rich formatting
- Modular Cleaning System**: Multiple specialized cleaning modules
- High Performance**: Fast scanning and cleaning operations
- Detailed Statistics**: Comprehensive reports on cleaned items and space recovered
- Safe Operations**: Dry-run mode to preview actions before execution
- Administrator Detection**: Automatic detection of privilege levels 
- System Information**: Detailed system, memory, and disk usage information 
- Self-Update**: Check for and install the latest version directly from the CLI 

##  Cleaning Modules

Nightmare Cleaner includes the following cleaning modules:

| Module | Description | Requires Admin |
|--------|-------------|:--------------:|
| **windows-temp** | Windows system temporary files | ✅ |
| **user-temp** | User temporary files and folders | ❌ |
| **browser** | Browser cache (Chrome, Edge, Firefox) | ❌ |
| **windows-update** | Windows Update cache | ✅ |
| **prefetch** | Windows Prefetch files | ✅ |
| **recycle** | Recycle Bin contents | ✅ |
| **error-reports** | Windows Error Reports | ❌ |
| **thumbnails** | Windows thumbnail cache | ❌ |
| **logs** | Windows Log files | ✅ |
| **delivery-optimization** | Delivery Optimization cache | ❌ |
| **disk-cleanup** | Run Windows Disk Cleanup utility | ✅ |
| **dns-cache** | Clear DNS resolver cache | ✅ |
| **store-cache** | Windows Store cache | ❌ |
| **memory** | Flush working-set memory to free RAM | ❌ |
| **font-cache** | Windows font cache files | ❌ |
| **cdrive** | C:\ drive root junk (Windows.old, installer dumps, driver leftovers) | ✅ |

##  Installation

### One-Command Installation (Recommended)

To install Nightmare Cleaner with a single command, open an Administrator prompt (CMD or PowerShell) in the root directory:

```cmd
install.bat
```
*(This automatically elevates privileges, checks for Python, and installs the CLI).*

Alternatively, using PowerShell:
```powershell
.\install.ps1 -InstallPython
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/Moamen-R/Nightmare-Cleaning.git
cd Nightmare-Cleaning

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Install Dependencies Only

```bash
pip install click colorama psutil rich
```

##  Usage

### Basic Commands

#### Display Help

```bash
nightmare --help
```

#### Show Version

```bash
nightmare --version
```

#### Check for Updates

```bash
nightmare -u
# or
nightmare --update
```

Checks PyPI for the latest published version. If a newer version is available, you will be prompted to confirm the upgrade. The tool automatically downloads and installs the update via `pip`.

#### Display System Information

```bash
nightmare info
```

Shows detailed information about:
- Operating system and version
- Hardware specifications
- Memory usage
- Disk usage for all drives

#### List Available Modules

```bash
nightmare modules
```

### Scanning

#### Scan All Modules

```bash
nightmare scan --all
```

#### Scan Specific Modules

```bash
nightmare scan -m windows-temp -m browser
```

#### Scan Single Module

```bash
nightmare scan -m user-temp
```

### Cleaning

#### Clean All (with confirmation)

```bash
nightmare clean --all
```

#### Clean Specific Modules

```bash
nightmare clean -m windows-temp -m browser
```

#### Dry Run (Preview Only)

```bash
nightmare clean --all --dry-run
```

#### Clean Without Confirmation

```bash
nightmare clean --all -y
```

##  Screenshots

### Banner
```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              ███╗   ██╗██╗ ██████╗ ██╗  ██╗████████╗          ║
║              ████╗  ██║██║██╔════╝ ██║  ██║╚══██╔══╝          ║
║              ██╔██╗ ██║██║██║  ███╗███████║   ██║             ║
║              ██║╚██╗██║██║██║   ██║██╔══██║   ██║             ║
║              ██║ ╚████║██║╚██████╔╝██║  ██║   ██║             ║
║              ╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝             ║
║                                                               ║
║              NIGHTMARE CLEANER & OPTIMIZER v1.2.0             ║
║              Windows System Cleaner and Optimizer             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

##  Architecture

### Project Structure

```
nightmare-cleaner/
├── nightmare_cleaner/
│   ├── __init__.py              # Package initialization
│   ├── cli.py                   # Main CLI interface
│   ├── ui.py                    # UI utilities and theming
│   ├── system_info.py           # System information utilities
│   └── modules/
│       ├── __init__.py              # Base cleaning module
│       ├── windows_temp.py          # Windows temp files cleaner
│       ├── user_temp.py             # User temp files cleaner
│       ├── browser_cache.py         # Browser cache cleaner
│       ├── windows_update.py        # Windows Update cache cleaner
│       ├── prefetch.py              # Prefetch cleaner
│       ├── recycle_bin.py           # Recycle bin cleaner
│       ├── error_reports.py         # Error reports cleaner
│       ├── thumbnail_cache.py       # Thumbnail cache cleaner
│       ├── windows_logs.py          # Windows logs cleaner
│       ├── delivery_optimization.py # Delivery Optimization cleaner
│       ├── disk_cleanup.py          # Disk Cleanup utility runner
│       ├── dns_cache.py             # DNS cache cleaner
│       ├── store_cache.py           # Windows Store cache cleaner
│       ├── memory_cleaner.py        # RAM working-set flusher
│       ├── font_cache.py            # Font cache cleaner
│       └── cdrive_cleaner.py        # C:\ drive root junk cleaner
├── setup.py                     # Setup configuration
├── pyproject.toml              # Project metadata
├── requirements.txt            # Dependencies
├── LICENSE                     # MIT License
└── README.md                   # Documentation
```

### Modular Design

Each cleaning module inherits from the `CleaningModule` base class and implements:
- `scan()`: Analyzes the system and identifies cleanable items
- `clean()`: Removes identified items (with optional dry-run)
- `get_stats()`: Returns statistics about the cleaning operation

##  Development

### Adding a New Cleaning Module

1. Create a new file in `nightmare_cleaner/modules/`
2. Inherit from `CleaningModule`
3. Implement `scan()` and `clean()` methods
4. Register the module in `cli.py`

Example:

```python
from . import CleaningModule
from typing import Tuple

class MyCustomCleaner(CleaningModule):
    def __init__(self):
        super().__init__()
        self.description = "My custom cleaner"

    def scan(self) -> Tuple[int, int]:
        # Implement scanning logic
        return count, size

    def clean(self, dry_run=False) -> Tuple[int, int]:
        # Implement cleaning logic
        return cleaned_count, cleaned_size
```

##  Safety Features

- **Dry Run Mode**: Test cleaning operations without deleting files
- **Administrator Detection**: Warns when not running with elevated privileges
- **Error Handling**: Graceful handling of permission errors and file locks
- **Confirmation Prompts**: Asks for confirmation before destructive operations

##  Requirements

- Python 3.8+
- click >= 8.1.7
- colorama >= 0.4.6
- psutil >= 5.9.8
- rich >= 13.7.0

##  Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Disclaimer

This tool performs file deletion operations. While it includes safety features, always:
- Review what will be deleted before confirming
- Use dry-run mode first to preview operations
- Keep backups of important data
- Run with appropriate privileges

---

**Made with 💜 by [Moamen-R](https://github.com/Moamen-R) & [Mahmoud Osama](https://github.com/Mahmud-O)**

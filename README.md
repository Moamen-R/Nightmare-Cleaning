# Nightmare Cleaner 🌙✨

A modular, high-performance Windows Cleaner and Optimizer CLI tool built with Python, featuring a beautiful purple/magenta themed UI.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

## ✨ Features

- **🎨 Beautiful Purple/Magenta UI**: Eye-catching terminal interface with rich formatting
- **🧹 Modular Cleaning System**: Multiple specialized cleaning modules
- **⚡ High Performance**: Fast scanning and cleaning operations
- **📊 Detailed Statistics**: Comprehensive reports on cleaned items and space recovered
- **🔒 Safe Operations**: Dry-run mode to preview actions before execution
- **💪 Administrator Detection**: Automatic detection of privilege levels
- **📈 System Information**: Detailed system, memory, and disk usage information

## 🎯 Cleaning Modules

Nightmare Cleaner includes the following cleaning modules:

| Module | Description |
|--------|-------------|
| **temp** | Temporary files and folders |
| **browser** | Browser cache and temporary internet files |
| **recycle** | Recycle Bin contents |
| **prefetch** | Windows Prefetch files |
| **thumbnails** | Windows thumbnail cache |

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Windows operating system
- Administrator privileges (recommended)

### Install from Source

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

## 📖 Usage

### Basic Commands

#### Display Help

```bash
nightmare-cleaner --help
```

#### Show Version

```bash
nightmare-cleaner --version
```

#### Display System Information

```bash
nightmare-cleaner info
```

Shows detailed information about:
- Operating system and version
- Hardware specifications
- Memory usage
- Disk usage for all drives

#### List Available Modules

```bash
nightmare-cleaner modules
```

### Scanning

#### Scan All Modules

```bash
nightmare-cleaner scan --all
```

#### Scan Specific Modules

```bash
nightmare-cleaner scan -m temp -m browser
```

#### Scan Single Module

```bash
nightmare-cleaner scan -m temp
```

### Cleaning

#### Clean All (with confirmation)

```bash
nightmare-cleaner clean --all
```

#### Clean Specific Modules

```bash
nightmare-cleaner clean -m temp -m browser
```

#### Dry Run (Preview Only)

```bash
nightmare-cleaner clean --all --dry-run
```

#### Clean Without Confirmation

```bash
nightmare-cleaner clean --all -y
```

## 🎨 Screenshots

### Banner
```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              ███╗   ██╗██╗ ██████╗ ██╗  ██╗████████╗        ║
║              ████╗  ██║██║██╔════╝ ██║  ██║╚══██╔══╝        ║
║              ██╔██╗ ██║██║██║  ███╗███████║   ██║           ║
║              ██║╚██╗██║██║██║   ██║██╔══██║   ██║           ║
║              ██║ ╚████║██║╚██████╔╝██║  ██║   ██║           ║
║              ╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝           ║
║                                                               ║
║              NIGHTMARE CLEANER & OPTIMIZER v1.0              ║
║              Windows System Cleaner and Optimizer            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

## 🏗️ Architecture

### Project Structure

```
nightmare-cleaner/
├── nightmare_cleaner/
│   ├── __init__.py              # Package initialization
│   ├── cli.py                   # Main CLI interface
│   ├── ui.py                    # UI utilities and theming
│   ├── system_info.py           # System information utilities
│   └── modules/
│       ├── __init__.py          # Base cleaning module
│       ├── temp_cleaner.py      # Temporary files cleaner
│       ├── browser_cache.py     # Browser cache cleaner
│       ├── recycle_bin.py       # Recycle bin cleaner
│       ├── prefetch.py          # Prefetch cleaner
│       └── thumbnail_cache.py   # Thumbnail cache cleaner
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

## 🔧 Development

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

## 🛡️ Safety Features

- **Dry Run Mode**: Test cleaning operations without deleting files
- **Administrator Detection**: Warns when not running with elevated privileges
- **Error Handling**: Graceful handling of permission errors and file locks
- **Confirmation Prompts**: Asks for confirmation before destructive operations

## 📋 Requirements

- Python 3.8+
- click >= 8.1.7
- colorama >= 0.4.6
- psutil >= 5.9.8
- rich >= 13.7.0

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool performs file deletion operations. While it includes safety features, always:
- Review what will be deleted before confirming
- Use dry-run mode first to preview operations
- Keep backups of important data
- Run with appropriate privileges

## 🌟 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for the CLI framework
- Styled with [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- System monitoring via [psutil](https://github.com/giampaolo/psutil)

## 📞 Support

For issues, questions, or contributions, please visit:
- [GitHub Issues](https://github.com/Moamen-R/Nightmare-Cleaning/issues)
- [GitHub Repository](https://github.com/Moamen-R/Nightmare-Cleaning)

---

**Made with 💜 by Moamen-R**
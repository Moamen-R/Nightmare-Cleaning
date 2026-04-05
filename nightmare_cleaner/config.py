"""
Configuration management module
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List

# Default configuration
DEFAULT_CONFIG = {
    "security": {"enable_secure_delete": False, "passes": 3, "allowed_paths": []},
    "cleaning": {
        "auto_skip_locked": True,
        "timeout_seconds": 300,
        "modules_enabled": {
            "windows-temp": True,
            "user-temp": True,
            "browser": True,
            "windows-update": True,
            "prefetch": True,
            "recycle": True,
            "error-reports": True,
            "thumbnails": True,
            "logs": True,
            "delivery-optimization": True,
            "disk-cleanup": True,
            "dns-cache": True,
            "store-cache": True,
            "memory": False,
            "font-cache": False,
        },
    },
}


class ConfigManager:
    """Manages application configuration"""

    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_path = os.path.join(self.config_dir, "config.json")
        self.config = self._load_config()

    def _get_config_dir(self) -> str:
        """Get the platform-specific configuration directory"""
        if os.name == "nt":
            appdata = os.environ.get("APPDATA", "")
            if appdata:
                return os.path.join(appdata, "NightmareCleaner")

        # Fallback to user home
        return os.path.join(str(Path.home()), ".nightmare_cleaner")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from disk or create default"""
        if not os.path.exists(self.config_path):
            self._save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded_config = json.load(f)

            # Merge with defaults to ensure all keys exist
            return self._merge_configs(DEFAULT_CONFIG, loaded_config)
        except (json.JSONDecodeError, IOError):
            return DEFAULT_CONFIG

    def _merge_configs(self, default: Dict, override: Dict) -> Dict:
        """Deep merge two configuration dictionaries"""
        merged = default.copy()
        for key, value in override.items():
            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged

    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to disk"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            return True
        except IOError:
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using a dot-separated path (e.g., 'security.passes')
        """
        keys = key_path.split(".")
        value = self.config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any) -> bool:
        """
        Set a configuration value using a dot-separated path
        """
        keys = key_path.split(".")
        config_node = self.config

        for key in keys[:-1]:
            if key not in config_node or not isinstance(config_node[key], dict):
                config_node[key] = {}
            config_node = config_node[key]

        config_node[keys[-1]] = value
        return self._save_config(self.config)


# Global config instance
config = ConfigManager()

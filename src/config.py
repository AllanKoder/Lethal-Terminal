import json
import os
from typing import Optional, Any

# A class for reading from the JSON
class ConfigSingleton:
    _instance = None
    _config = None

    def __new__(cls, config_file: str = None):
        if cls._instance is None:
            cls._instance = super(ConfigSingleton, cls).__new__(cls)
            cls._instance._load_config(config_file)
        return cls._instance

    def _load_config(self, config_file: Optional[str]):
        if config_file is None:
            config_file = os.environ.get('CONFIG_FILE', 'config.json')
        
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file '{config_file}' not found")
        
        with open(config_file, 'r') as f:
            self._config = json.load(f)

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)



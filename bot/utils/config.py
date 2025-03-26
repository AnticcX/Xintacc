import json

from typing import Any

CONFIG = json.load(open("./config.json", "r"))

def get_config(config_key: str) -> Any:
    """
    Retrieves a configuration value by key from the global CONFIG dictionary.

    Args:
        config_key (str): The key to look up in the configuration.

    Returns:
        Any: The value associated with the given config key.

    Raises:
        KeyError: If the provided key does not exist in the configuration.
    """
    if config_key in CONFIG:
        return CONFIG[config_key]
    
    raise KeyError(f"{config_key} does not exist in configs")

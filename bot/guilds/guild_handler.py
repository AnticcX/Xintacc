import os

def _build_path(guild_id: int, path_category: str = None) -> str:
    base_path = f"./guild_data/{guild_id}"
    return f"{base_path}/{path_category}" if path_category else base_path

def ensure_guild_path(guild_id: int, path_category: str = None) -> str:
    if not confirm_guild_exists(guild_id):
        os.makedirs(_build_path(guild_id), exist_ok=True)
    path = _build_path(guild_id, path_category)
    os.makedirs(path, exist_ok=True)
    return path

def get_guild_path(guild_id: int, path_category: str = None) -> str:
    return ensure_guild_path(guild_id, path_category)

def confirm_guild_exists(guild_id: int) -> bool:
    return os.path.isdir(_build_path(guild_id))
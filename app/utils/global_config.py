import json
import config
from app.utils.logger import log_warning


def _read_is_old_global() -> bool:
    try:
        with open(config.SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return bool(data.get("is_old_pigeon", False))
    except Exception as e:
        log_warning(f"Nie udało się odczytać is_old_pigeon z {config.SETTINGS_FILE}: {e}")
        return False

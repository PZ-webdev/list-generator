import sys
import os

try:
    # Prefer config base directory when not frozen, for stable paths
    from config import BASE_DIR as _BASE_DIR
except Exception:
    _BASE_DIR = None


def resource_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    base = str(_BASE_DIR) if _BASE_DIR else os.path.abspath(".")
    return os.path.join(base, relative_path)

import json
import os
from config import SETTINGS_FILE


def save_paths(paths):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(paths, f)


def load_paths():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE) as f:
            return json.load(f)
    return ["" for _ in range(5)]

# Global
from pathlib import Path

WINDOW_TITLE = "Generator list PDF"
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700
WINDOW_RESIZABLE = False

# Directory settings
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
BRANCHES_FILE = DATA_DIR / 'branches.json'
SETTINGS_FILE = DATA_DIR / 'settings.json'

# Logging
LOG_LEVEL = 'INFO'
LOG_BACKUP_COUNT = 30

# About app
APP_AUTHOR = "Patryk Zaprzała"
APP_AUTHOR_EMAIL = "pzaprzala@gmail.com"

# Files
CHANGELOG_FILE = BASE_DIR / "CHANGELOG.md"

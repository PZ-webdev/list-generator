import json
import os
from typing import Dict, Any

import config
from app.utils.logger import log_warning


class UIStateStore:
    """Lightweight store for per-branch UI flags (checkboxes).

    Not part of the domain DB. Persisted to a separate cache file
    so selections survive app restarts without touching branches.json.
    """

    def __init__(self, path: str = str(config.UI_STATE_FILE)) -> None:
        self.path = path
        self.state: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        try:
            if not os.path.exists(self.path):
                self.state = {}
                return
            with open(self.path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                self.state = data
            else:
                self.state = {}
        except Exception as e:
            log_warning(f"Nie udało się wczytać UI state z {self.path}: {e}")
            self.state = {}

    def _ensure_dirs(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
        except Exception:
            pass

    def _save(self) -> None:
        try:
            self._ensure_dirs()
            tmp = f"{self.path}.tmp"
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            os.replace(tmp, self.path)
        except Exception as e:
            log_warning(f"Nie udało się zapisać UI state do {self.path}: {e}")

    def get_flags(self, branch_id: str) -> Dict[str, bool]:
        entry = self.state.get(branch_id, {})
        return {
            'additional': bool(entry.get('additional', False)),
            'rating': bool(entry.get('rating', False)),
            'league2': bool(entry.get('league2', False)),
        }

    def set_flag(self, branch_id: str, key: str, value: bool) -> None:
        entry = self.state.setdefault(branch_id, {})
        entry[key] = bool(value)
        self._save()

    def get_last_lot(self, branch_id: str) -> str:
        entry = self.state.get(branch_id, {})
        val = entry.get('last_lot', '')
        return str(val) if val is not None else ''

    def set_last_lot(self, branch_id: str, lot_value: str) -> None:
        entry = self.state.setdefault(branch_id, {})
        entry['last_lot'] = str(lot_value or '').strip()
        self._save()

    def remove_branch(self, branch_id: str) -> None:
        """Usuń stan UI powiązany z danym oddziałem (np. po usunięciu oddziału)."""
        try:
            if branch_id in self.state:
                del self.state[branch_id]
                self._save()
        except Exception:
            # Cicho ignoruj — brak stanu nie powinien zatrzymywać działania aplikacji
            pass

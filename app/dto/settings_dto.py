from dataclasses import dataclass, asdict
from typing import List

import config
from app.utils.file_utils import write_json_utf8, read_json_utf8


@dataclass
class SettingsDTO:
    filename_branch: str
    filename_branch_closed: str
    filename_section: str
    filename_section_closed: str
    attached_files: List[str]
    ring_mask: str
    default_pdf_dir: str
    is_old_pigeon: bool

    def to_json(self):
        write_json_utf8(asdict(self), config.SETTINGS_FILE)

    @classmethod
    def from_json(cls):
        data = read_json_utf8(config.SETTINGS_FILE)

        if not isinstance(data, dict):
            raise ValueError("Plik settings.json nie zawiera prawidłowej struktury (dict)")

        return cls(**data)


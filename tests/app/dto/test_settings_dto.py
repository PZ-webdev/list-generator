import json
import os
import tempfile

import config
from app.dto.settings_dto import SettingsDTO


def test_settings_dto_from_json_and_to_json(tmp_path, monkeypatch):
    # Redirect settings file into temp dir
    settings_file = os.path.join(tmp_path, 'settings.json')
    monkeypatch.setattr(config, 'SETTINGS_FILE', settings_file)

    data = {
        'filename_branch': 'OPEN_{BRANCH}_{DATE}.pdf',
        'filename_branch_closed': 'CLOSED_{BRANCH}_{DATE}.pdf',
        'filename_section': 'OPEN_{BRANCH}_{DATE}_S{SECTION}.pdf',
        'filename_section_closed': 'CLOSED_{BRANCH}_{DATE}_S{SECTION}.pdf',
        'attached_files': ['PHD_1AS.TXT'],
        'ring_mask': 'XXXXX',
        'default_pdf_dir': str(tmp_path),
        'is_old_pigeon': False,
    }
    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(data, f)

    s = SettingsDTO.from_json()
    assert s.filename_branch and isinstance(s.attached_files, list)

    # to_json writes back
    s.to_json()
    with open(settings_file, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    assert isinstance(raw, dict)


def test_settings_dto_from_json_invalid_structure_raises(tmp_path, monkeypatch):
    settings_file = os.path.join(tmp_path, 'settings.json')
    monkeypatch.setattr(config, 'SETTINGS_FILE', settings_file)
    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write('[]')  # not a dict
    try:
        SettingsDTO.from_json()
        assert False, 'Expected ValueError'
    except ValueError:
        pass

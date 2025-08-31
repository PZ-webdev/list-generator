import os
import json
from app.utils.file_utils import read_json_utf8, write_json_utf8
from app.utils.file_utils import read_file_utf8


def test_read_write_json_utf8_roundtrip(tmp_path):
    file_path = os.path.join(tmp_path, 'data.json')
    payload = {"a": 1, "b": "żółć"}
    write_json_utf8(payload, file_path)
    loaded = read_json_utf8(file_path)
    assert loaded == payload


def test_read_json_utf8_on_missing_returns_none(tmp_path):
    file_path = os.path.join(tmp_path, 'missing.json')
    assert read_json_utf8(file_path) is None


def test_read_file_utf8(tmp_path):
    p = os.path.join(tmp_path, 'file.txt')
    data = 'Linia 1\nZażółć gęślą jaźń'
    with open(p, 'w', encoding='utf-8') as f:
        f.write(data)
    assert read_file_utf8(p) == data

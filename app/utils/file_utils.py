import json

from app.utils.logger import log_error


def read_file_cp852(path: str) -> str:
    try:
        with open(path, 'r', encoding='CP852') as f:
            return f.read()
    except Exception as e:
        log_error(f'Błąd podczas odczytu pliku {path}: {e}')
        return ''


def read_file_utf8(path: str) -> str:
    try:
        with open(path, 'r', encoding='UTF-8') as f:
            return f.read()
    except Exception as e:
        log_error(f'Błąd podczas odczytu pliku {path}: {e}')
        return ''


def read_json_utf8(path: str) -> str:
    try:
        with open(path, 'r', encoding='UTF-8') as f:
            return json.load(f)
    except Exception as e:
        log_error(f'Błąd podczas odczytu pliku {path}: {e}')
        return ''


def write_json_utf8(data: list, file_path: str):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

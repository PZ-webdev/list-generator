from app.utils.logger import log_error


def read_file_cp852(path: str) -> str:
    try:
        with open(path, 'r', encoding='CP852') as f:
            return f.read()
    except Exception as e:
        log_error(f'Błąd podczas odczytu pliku {path}: {e}')
        return ''

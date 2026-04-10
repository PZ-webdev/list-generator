import os
import platform
import shutil

import pdfkit


class HtmlPdfRenderer:
    def __init__(self):
        self.config = pdfkit.configuration(wkhtmltopdf=self._get_wkhtmltopdf_path())

    def render(self, html_content: str, output_path: str) -> None:
        pdfkit.from_string(html_content, output_path, configuration=self.config)

    def _get_wkhtmltopdf_path(self) -> str:
        path = shutil.which('wkhtmltopdf')
        if path:
            return path

        if platform.system() == 'Windows':
            default_win_path = 'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
            if os.path.exists(default_win_path):
                return default_win_path

        raise FileNotFoundError('Nie znaleziono wkhtmltopdf. Dodaj go do PATH lub podaj ręczną ścieżkę.')

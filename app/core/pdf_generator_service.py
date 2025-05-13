import os
from datetime import datetime

import pdfkit
import shutil
import platform

from app.core.text_processing_service import TextProcessingService
from app.dto.branch import Branch
from app.utils.file_utils import read_file_cp852, read_file_utf8
from app.utils.resource_helper import resource_path


class PdfGeneratorService:
    def __init__(self):
        self.text_service = TextProcessingService()
        self.config = pdfkit.configuration(wkhtmltopdf=self._get_wkhtmltopdf_path())

    def _get_wkhtmltopdf_path(self) -> str:
        path = shutil.which('wkhtmltopdf')
        if path:
            return path

        if platform.system() == 'Windows':
            default_win_path = 'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
            if os.path.exists(default_win_path):
                return default_win_path

        raise FileNotFoundError('Nie znaleziono wkhtmltopdf. Dodaj go do PATH lub podaj ręczną ścieżkę.')

    def generate_single_pdf(self, file_path: str) -> str:
        raw_content = read_file_cp852(file_path)

        html_ready = self.text_service.transform_control_codes(raw_content)
        html_ready = self.text_service.center_only_first_page(html_ready)

        template_path = resource_path('app/templates/pdf_template.html')
        html_template = read_file_utf8(template_path)

        html_content = html_template.replace('{{ content }}', html_ready)
        output_path = os.path.splitext(file_path)[0] + '.pdf'

        pdfkit.from_string(html_content, output_path, configuration=self.config)
        return output_path

    def generate_pdf_to_path(
            self,
            branch: Branch,
            file_path: str,
            output_dir: str,
            additional_list: bool,
            rating_list: bool
    ):
        raw_content = read_file_cp852(file_path)

        if rating_list:
            base_dir = os.path.dirname(file_path)
            rating_files = ['PHD_1AS.TXT', 'PHDOD1A.TXT']
            raw_content = self.text_service.append_rating_files_to_content(raw_content, base_dir, rating_files)

        html_ready = self.text_service.transform_control_codes(raw_content)
        html_ready = self.text_service.center_only_first_page(html_ready)

        template_path = resource_path('app/templates/pdf_template.html')
        html_template = read_file_utf8(template_path)

        filled_html = html_template.replace('{{ content }}', html_ready)

        output_pdf_path, closed_list_path = self.get_output_filenames(branch, file_path, output_dir)
        pdfkit.from_string(filled_html, output_pdf_path, configuration=self.config)

        if additional_list:
            html_ready_masked = self.text_service.mask_pigeon_rings(html_ready)
            filled_html_masked = html_template.replace('{{ content }}', html_ready_masked)
            pdfkit.from_string(filled_html_masked, closed_list_path, configuration=self.config)

    def get_output_filenames(self, branch: Branch, file_path: str, output_dir: str) -> tuple[str, str]:
        date_format = getattr(self, 'date_format', '%Y%m%d')
        date_str = datetime.today().strftime(date_format)

        dir_name = os.path.basename(os.path.dirname(file_path))
        if dir_name.upper().startswith('SEKCJA.'):
            section_number = dir_name.split('.')[-1].zfill(2)
            base_name = f"{branch.number} {date_str} Sekcja nr. {section_number}"
        else:
            base_name = f"{branch.number} {date_str} LISTA ODDZIAŁOWA"

        open_list_path = os.path.join(output_dir, f"{base_name}.pdf")
        closed_list_path = os.path.join(output_dir, f"{base_name} - ZAMKNIĘTA.pdf")

        return open_list_path, closed_list_path



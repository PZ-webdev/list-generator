import os
import pdfkit
import shutil
import platform

from app.core.text_processing_service import TextProcessingService
from app.utils.file_utils import read_file_cp852
from app.utils.logger import log_warning
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
        with open(template_path, 'r', encoding='utf-8') as template_file:
            html_template = template_file.read()

        html_content = html_template.replace('{{ content }}', html_ready)
        output_path = os.path.splitext(file_path)[0] + '.pdf'

        pdfkit.from_string(html_content, output_path, configuration=self.config)
        return output_path

    def generate_pdf_to_path(self, file_path: str, output_pdf_path: str, additional_list: bool, rating_list: bool):
        raw_content = read_file_cp852(file_path)

        if rating_list:
            base_dir = os.path.dirname(file_path)
            rating_files = ['PHD_1AS.TXT', 'PHDOD1A.TXT', 'PHD_1AS.TXT']
            raw_content = self.text_service.append_rating_files_to_content(raw_content, base_dir, rating_files)

        html_ready = self.text_service.transform_control_codes(raw_content)
        html_ready = self.text_service.center_only_first_page(html_ready)

        template_path = resource_path('app/templates/pdf_template.html')
        with open(template_path, 'r', encoding='utf-8') as tpl_file:
            html_template = tpl_file.read()

        filled_html = html_template.replace('{{ content }}', html_ready)
        pdfkit.from_string(filled_html, output_pdf_path, configuration=self.config)

        if additional_list:
            html_ready_masked = self.text_service.mask_pigeon_rings(html_ready)
            filled_html_masked = html_template.replace('{{ content }}', html_ready_masked)
            closed_list_path = output_pdf_path.replace('.pdf', ' - LISTA ZAMKNIĘTA.pdf')
            pdfkit.from_string(filled_html_masked, closed_list_path, configuration=self.config)

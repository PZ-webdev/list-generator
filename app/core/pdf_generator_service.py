import os
from datetime import datetime
from typing import Tuple

import pdfkit
import shutil
import platform

from app.core.text_processing_service import TextProcessingService
from app.dto.branch import Branch
from app.dto.settings_dto import SettingsDTO
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

        default_output_path = os.path.splitext(file_path)[0] + '.pdf'

        try:
            settings = SettingsDTO.from_json()
            output_dir = settings.default_pdf_dir.strip()

            if output_dir and os.path.isdir(output_dir):
                file_name = os.path.basename(default_output_path)
                output_path = os.path.join(output_dir, file_name)
            else:
                output_path = default_output_path
        except Exception:
            output_path = default_output_path

        pdfkit.from_string(html_content, output_path, configuration=self.config)
        return output_path

    def generate_pdf_to_path(
            self,
            branch: Branch,
            file_path: str,
            output_dir: str,
            additional_list: bool,
            rating_list: bool,
            league2_list: bool = False
    ) -> None:
        # Determine if this is a section-level file (skip II-LIGA for sections)
        # Check any ancestor up to lot root for names like 'SEKCJA.*'
        current_dir_scan = os.path.dirname(file_path)
        is_section = False
        while True:
            base = os.path.basename(current_dir_scan)
            base_up = base.upper()
            if base_up.startswith('LOT_'):
                break
            if base_up.startswith('SEKCJA'):
                is_section = True
                break
            parent = os.path.dirname(current_dir_scan)
            if parent == current_dir_scan:
                break
            current_dir_scan = parent

        # Read base content
        raw_content = read_file_cp852(file_path)

        # Optionally append rating files to the base content only
        if rating_list:
            default_rating_files = ['PHD_1AS.TXT', 'PHDOD1A.TXT']

            rating_files = default_rating_files
            try:
                settings = SettingsDTO.from_json()
                if settings.attached_files and isinstance(settings.attached_files, list):
                    rating_files = settings.attached_files
            except Exception:
                pass

            base_dir = os.path.dirname(file_path)
            raw_content = self.text_service.append_rating_files_to_content(raw_content, base_dir, rating_files)

        # Transform and center first page for base (with optional rating appends)
        base_html = self.text_service.transform_control_codes(raw_content)
        base_html = self.text_service.center_only_first_page(base_html)

        final_html = base_html

        # If II-LIGA requested and this is NOT a section list, transform it separately and then append.
        if league2_list and not is_section:
            try:
                # Find lot root (directory named starting with 'LOT_')
                current_dir = os.path.dirname(file_path)
                lot_root = None
                while True:
                    base = os.path.basename(current_dir)
                    if base.upper().startswith('LOT_'):
                        lot_root = current_dir
                        break
                    parent = os.path.dirname(current_dir)
                    if parent == current_dir:
                        break
                    current_dir = parent

                if lot_root:
                    # Prefer 'II-LIGA' per spec; fallback to 'II liga' for compatibility
                    league_dir = os.path.join(lot_root, 'II-LIGA')
                    if not os.path.isdir(league_dir):
                        alt_dir = os.path.join(lot_root, 'II liga')
                        league_dir = alt_dir if os.path.isdir(alt_dir) else league_dir
                    if os.path.isdir(league_dir):
                        base_name_no_ext = os.path.splitext(os.path.basename(file_path))[0]
                        # search for a TXT file starting with the same prefix
                        candidate = None
                        for name in os.listdir(league_dir):
                            upper = name.upper()
                            if upper.endswith('.TXT') and upper.startswith(base_name_no_ext.upper()):
                                candidate = os.path.join(league_dir, name)
                                break
                        if candidate and os.path.exists(candidate) and os.path.abspath(candidate) != os.path.abspath(file_path):
                            league_raw = read_file_cp852(candidate)
                            league_html = self.text_service.transform_control_codes(league_raw)
                            league_html = self.text_service.center_only_first_page(league_html)
                            final_html = base_html + '<div class="page-break"></div>' + league_html
            except Exception:
                # Ignore issues with optional II-LIGA block
                pass

        template_path = resource_path('app/templates/pdf_template.html')
        html_template = read_file_utf8(template_path)

        filled_html = html_template.replace('{{ content }}', final_html)

        output_pdf_path, closed_list_path = self.get_output_filenames(branch, file_path, output_dir)
        pdfkit.from_string(filled_html, output_pdf_path, configuration=self.config)

        if additional_list:
            html_ready_masked = self.text_service.mask_pigeon_rings(final_html)
            filled_html_masked = html_template.replace('{{ content }}', html_ready_masked)
            pdfkit.from_string(filled_html_masked, closed_list_path, configuration=self.config)

    def get_output_filenames(self, branch: Branch, file_path: str, output_dir: str) -> Tuple[str, str]:
        settings = SettingsDTO.from_json()
        date_str = datetime.today().strftime('%Y%m%d')

        dir_name = os.path.basename(os.path.dirname(file_path))
        section_number = ''
        if dir_name.upper().startswith('SEKCJA.'):
            section_number = dir_name.split('.')[-1].zfill(2)

        mapping = {
            'BRANCH': branch.number,
            'DATE': date_str,
            'SECTION': section_number,
        }

        def format_template(template: str) -> str:
            for key, value in mapping.items():
                template = template.replace(f"{{{key}}}", value)
            return template

        if section_number:
            open_name = format_template(settings.filename_section)
            closed_name = format_template(settings.filename_section_closed)
        else:
            open_name = format_template(settings.filename_branch)
            closed_name = format_template(settings.filename_branch_closed)

        return (
            os.path.join(output_dir, open_name),
            os.path.join(output_dir, closed_name),
        )

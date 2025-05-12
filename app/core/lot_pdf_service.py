import os
import re
from typing import List, Tuple
from app.core.pdf_generator_service import PdfGeneratorService
from app.utils.logger import log_info, log_error, log_warning
from app.utils import notifier


class LotPdfService:
    def __init__(self, pdf_generator: PdfGeneratorService):
        self.pdf_generator = pdf_generator

    def get_matching_lot_dir(self, input_dir: str, lot_number: str) -> str | None:
        pattern = self._get_lot_pattern(lot_number)
        log_info(f'Używam wzorca regex: {pattern.pattern}')

        for folder in os.listdir(input_dir):
            log_info(f'Sprawdzam folder: {folder}')
            if pattern.match(folder):
                log_info(f'Znaleziono dopasowany folder: {folder}')
                return folder

        log_warning(f'Nie znaleziono katalogu LOT_S_{lot_number} w {input_dir}')
        return None

    def get_txt_files(self, directory: str) -> List[Tuple[str, str]]:
        matching_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.upper().startswith('LKON_S') and file.upper().endswith('.TXT'):
                    matching_files.append((root, file))
        return matching_files

    def generate_pdfs_for_lot(self, branch: dict, lot_number: str, additional_list: bool, progress_callback=None):
        input_dir = branch['input']
        output_dir = branch['output']
        os.makedirs(output_dir, exist_ok=True)

        matched_folder = self.get_matching_lot_dir(input_dir, lot_number)
        if not matched_folder:
            notifier.show_warning(f'Nie znaleziono katalogu dla lotu {lot_number}')
            return

        lot_path = os.path.join(input_dir, matched_folder)
        matching_files = self.get_txt_files(lot_path)

        if not matching_files:
            notifier.show_warning(f'Brak plików TXT do wygenerowania dla lotu {lot_number}')
            return

        for i, (root, file) in enumerate(matching_files, 1):
            relative_path = os.path.relpath(root, input_dir)
            target_folder = os.path.join(output_dir, relative_path)
            os.makedirs(target_folder, exist_ok=True)

            txt_path = os.path.join(root, file)
            output_pdf_path = os.path.join(target_folder, os.path.splitext(file)[0] + '.pdf')

            try:
                log_info(f'Generowanie PDF z pliku: {txt_path}')
                self.pdf_generator.generate_pdf_to_path(txt_path, output_pdf_path, additional_list)
                log_info(f'Zapisano PDF do: {output_pdf_path}')
            except Exception as e:
                log_error(f'Błąd generowania PDF dla {txt_path}: {e}')
                notifier.show_error(f'Błąd generowania PDF dla {txt_path}')
                return

            if progress_callback:
                progress_callback(i, len(matching_files))

        notifier.show_success(f"Poprawnie wygenerowano listy PDF\nLot numer: {lot_number}\nOddział: {branch['name']}")

    def _get_lot_pattern(self, lot_number: str):
        lot_str = f"{int(lot_number):02d}"
        return re.compile(rf'^LOT_S_{lot_str}\.\d+$')

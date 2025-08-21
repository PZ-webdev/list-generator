import os
import re
from typing import List, Tuple, Optional

from app.core.pdf_generator_service import PdfGeneratorService
from app.dto.branch import Branch
from app.utils.logger import log_info, log_error, log_warning
from app.utils import notifier
from app.utils.global_config import _read_is_old_global


class LotPdfService:
    def __init__(self, pdf_generator: PdfGeneratorService):
        self.pdf_generator = pdf_generator
        self.is_old = _read_is_old_global()
        self.suffix = "S" if self.is_old else "M"
        log_info(f"[LotPdfService] Ustawiono suffix: {self.suffix} (is_old_pigeon={self.is_old})")

    def get_matching_lot_dir(self, input_dir: str, lot_number: Optional[str]) -> Optional[str]:
        pattern = self._get_lot_pattern(lot_number)
        log_info(f'Używam wzorca regex: {pattern.pattern}')

        try:
            folders = os.listdir(input_dir)
        except FileNotFoundError:
            log_warning(f'Katalog wejściowy nie istnieje: {input_dir}')
            return None

        for folder in folders:
            log_info(f'Sprawdzam folder: {folder}')
            if pattern.match(folder):
                log_info(f'Znaleziono dopasowany folder: {folder}')
                return folder

        log_warning(f'Nie znaleziono katalogu lotu nr. {lot_number} w {input_dir}')
        return None

    def get_txt_files(self, directory: str) -> List[Tuple[str, str]]:
        matching_files: List[Tuple[str, str]] = []
        for root, _, files in os.walk(directory):
            for file in files:
                upper = file.upper()
                if upper.startswith(f'LKON_{self.suffix}') and upper.endswith('.TXT'):
                    matching_files.append((root, file))
        log_info(f'Znaleziono {len(matching_files)} plików TXT typu LKON_{self.suffix} w {directory}')
        return matching_files

    def generate_pdfs_for_lot(
            self,
            branch: Branch,
            lot_number: str,
            additional_list: bool,
            rating_list: bool,
            progress_callback=None
    ):
        input_dir = branch.input
        base_output_dir = branch.output
        os.makedirs(base_output_dir, exist_ok=True)

        matched_folder = self.get_matching_lot_dir(input_dir, lot_number)
        if not matched_folder:
            notifier.show_warning(f'Nie znaleziono katalogu dla lotu {lot_number}')
            return

        lot_path = os.path.join(input_dir, matched_folder)
        matching_files = self.get_txt_files(lot_path)

        if not matching_files:
            notifier.show_warning(f'Brak plików TXT do wygenerowania dla lotu {lot_number}')
            return

        total = len(matching_files)
        for i, (root, file) in enumerate(matching_files, 1):
            txt_path = os.path.join(root, file)

            try:
                log_info(f'Generowanie PDF z pliku: {txt_path}')

                relative_path = os.path.relpath(txt_path, branch.input)
                parts = relative_path.split(os.sep)
                lot_folder_name = next((p for p in parts if p.startswith(f"LOT_{self.suffix}_")), None)

                if not lot_folder_name:
                    raise ValueError(f"Nie znaleziono katalogu lotu w ścieżce: {txt_path}")

                output_dir = os.path.join(base_output_dir, lot_folder_name)
                os.makedirs(output_dir, exist_ok=True)

                self.pdf_generator.generate_pdf_to_path(
                    branch,
                    txt_path,
                    output_dir,
                    additional_list,
                    rating_list
                )

                log_info(f'Zapisano PDF do: {output_dir}')
            except Exception as e:
                log_error(f'Błąd generowania PDF dla {txt_path}: {e}')
                notifier.show_error(f'Błąd generowania PDF dla {txt_path}')
                return

            if progress_callback:
                progress_callback(i, total)

        notifier.show_success(
            f"Wygenerowano listy \nLot nr.: {lot_number}\nOddział: {branch.name}"
        )

    def create_lot_dirs(
            self,
            *,
            output_dir: str,
            is_old_pigeon: bool,
            lot_number: str,
            sections: int = 5
    ) -> tuple[str, str]:

        sezon = "S" if is_old_pigeon else "M"
        lot_number = lot_number.zfill(2)

        dir_name = f"LOT-{sezon}-{lot_number}"
        final_path = os.path.join(output_dir, dir_name)

        os.makedirs(final_path, exist_ok=True)

        created = []
        for i in range(1, max(1, sections) + 1):
            sec_dir = os.path.join(final_path, f"Sekcja {i:02d}")
            if not os.path.exists(sec_dir):
                os.makedirs(sec_dir, exist_ok=True)
                created.append(sec_dir)

        if created:
            log_info(f"Utworzono podkatalogi sekcji: {', '.join(created)}")
        else:
            log_info("Wszystkie podkatalogi sekcji już istniały – nic nie tworzono.")

        return final_path, final_path

    def _get_lot_pattern(self, lot_number: Optional[str]) -> re.Pattern:
        if not lot_number or str(lot_number).strip() == "":
            return re.compile(rf'^LOT_{self.suffix}_(\d{{2}})\.\d+$')
        lot_str = f"{int(lot_number):02d}"
        return re.compile(rf'^LOT_{self.suffix}_{lot_str}\.\d+$')

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
        for root, dirs, files in os.walk(directory):
            # Do not descend into II-LIGA (or fallback 'II liga') directories
            try:
                dirs[:] = [d for d in dirs if d.upper() not in ('II-LIGA', 'II LIGA')]
            except Exception:
                pass
            for file in files:
                upper = file.upper()
                if upper.startswith(f'LKON_{self.suffix}') and upper.endswith('.TXT'):
                    # Extra guard: skip any file physically under II-LIGA
                    parts_up = [p.upper() for p in os.path.normpath(root).split(os.sep)]
                    if 'II-LIGA' in parts_up or 'II LIGA' in parts_up:
                        continue
                    matching_files.append((root, file))
        log_info(f'Znaleziono {len(matching_files)} plików TXT typu LKON_{self.suffix} w {directory}')
        return matching_files

    def get_start_clock_file(self, input_dir: str) -> Optional[str]:
        data_dir = os.path.join(input_dir, 'DANE_GL')
        path = os.path.join(data_dir, 'DRLSTZEG.TXT')
        if os.path.isfile(path):
            log_info(f'Znaleziono plik listy startowo-zegarowej: {path}')
            return path
        log_warning(f'Nie znaleziono pliku DRLSTZEG.TXT w {data_dir}')
        return None

    def generate_pdfs_for_lot(
            self,
            branch: Branch,
            lot_number: str,
            additional_list: bool,
            rating_list: bool,
            league2_list: bool = False,
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
                    rating_list,
                    league2_list
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

    def generate_start_clock_pdf_for_lot(self, branch: Branch) -> Optional[str]:
        input_dir = branch.input
        output_dir = branch.output
        os.makedirs(output_dir, exist_ok=True)

        start_clock_path = self.get_start_clock_file(input_dir)
        if not start_clock_path:
            notifier.show_warning('Brak pliku DRLSTZEG.TXT w katalogu DANE_GL')
            return None

        try:
            output_path = self.pdf_generator.generate_start_clock_pdf_to_path(
                branch=branch,
                file_path=start_clock_path,
                output_dir=output_dir,
            )
            log_info(f'Wygenerowano listę startowo-zegarową do: {output_path}')
            return output_path
        except Exception as e:
            log_error(f'Błąd generowania listy startowo-zegarowej dla {start_clock_path}: {e}')
            raise

    def generate_league2_only_for_lot(
            self,
            branch: Branch,
            lot_number: str,
            additional_list: bool = False,
            progress_callback=None
    ) -> None:
        """Wygeneruj osobny PDF z II ligą (jeśli istnieje) dla list oddziałowych.

        Gdy brak pliku/katalogu II-LIGA, pomiń bez błędu.
        """
        input_dir = branch.input
        base_output_dir = branch.output
        os.makedirs(base_output_dir, exist_ok=True)

        matched_folder = self.get_matching_lot_dir(input_dir, lot_number)
        if not matched_folder:
            return

        lot_path = os.path.join(input_dir, matched_folder)
        matching_files = self.get_txt_files(lot_path)

        # tylko oddziałowe (bez SEKCJA.*)
        branch_level_files = []
        for root, file in matching_files:
            parent = os.path.basename(root)
            if not parent.upper().startswith('SEKCJA.'):
                branch_level_files.append((root, file))

        if not branch_level_files:
            return

        total = len(branch_level_files)
        for i, (root, file) in enumerate(branch_level_files, 1):
            txt_path = os.path.join(root, file)
            try:
                relative_path = os.path.relpath(txt_path, branch.input)
                parts = relative_path.split(os.sep)
                lot_folder_name = next((p for p in parts if p.startswith(f"LOT_{self.suffix}_")), None)
                if not lot_folder_name:
                    continue

                output_dir = os.path.join(base_output_dir, lot_folder_name)
                os.makedirs(output_dir, exist_ok=True)

                try:
                    self.pdf_generator.generate_league2_only_to_path(
                        branch,
                        txt_path,
                        output_dir,
                        additional_list=additional_list,
                    )
                except FileNotFoundError:
                    # brak II-LIGA – pomiń cicho
                    pass
            except Exception as e:
                log_error(f'Błąd generowania II ligi dla {txt_path}: {e}')
                continue

            if progress_callback:
                progress_callback(i, total)

    def create_lot_dirs(
            self,
            *,
            output_dir: str,
            is_old_pigeon: bool,
            lot_number: str,
            sections: int = 5
    ) -> Tuple[str, str]:

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

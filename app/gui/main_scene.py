import os
import json
import config
import tkinter as tk
from tkinter import filedialog, ttk

from app.dto.branch import Branch
from app.gui.components.collapsible_row import CollapsibleRow
from app.gui.components.tooltip import Tooltip
from app.utils import notifier
from app.utils.logger import log_info, log_error
from app.core.branch_service import BranchService
from app.core.lot_pdf_service import LotPdfService
from app.core.pdf_generator_service import PdfGeneratorService
from app.core.ranking_service import RankingService
from app.utils.ui_state import UIStateStore


class MainScene:
    def __init__(self, app, branches_file=config.BRANCHES_FILE):
        self.app = app
        self.frame = tk.Frame(app.main_frame)
        self.frame.pack(fill='both', expand=True)

        self.branch_service = BranchService(branches_file)
        self.lot_pdf_service = LotPdfService(PdfGeneratorService())
        self.ranking_service = RankingService()
        self.ui_state = UIStateStore()

        type_order = ('C', 'S', 'M', 'I', 'G')
        self.ranking_type_vars = {
            lot_type: tk.BooleanVar(master=self.frame, value=(lot_type == 'C'))
            for lot_type in type_order
        }
        self.ranking_limit_var = tk.IntVar(
            master=self.frame,
            value=RankingService.DEFAULT_TOP_LIMIT,
        )

        self.is_old_pigeon = self._load_is_old()

        self.title_label = None
        self.progress = None

    def build(self):
        header = tk.Frame(self.frame)
        header.pack(fill='x', padx=10, pady=(10, 6))

        self.title_label = tk.Label(
            header,
            text=self._title_text(),
            font=('Arial', 12, 'bold')
        )
        self.title_label.pack(side='left')

        btn_cfg = tk.Button(
            header,
            text='Zarządzaj oddziałami',
            command=self.app.show_branches_scene
        )
        btn_cfg.pack(side='right')
        Tooltip(btn_cfg, "Przejdź do dodawania/edycji oddziałów")

        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        lists_tab = ttk.Frame(notebook)
        other_tab = ttk.Frame(notebook)

        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[15, 5])

        notebook.add(lists_tab, text="Oddziały")
        notebook.add(other_tab, text="Inne")

        rows_container = tk.Frame(lists_tab)
        rows_container.pack(fill='both', expand=True)
        rows_container.columnconfigure(0, weight=1)

        for idx, branch in enumerate(self.branch_service.get_all()):
            row = CollapsibleRow(
                rows_container,
                branch=branch,
                on_generate=self._on_generate_row,
                on_create_dir=self._on_create_dir,
                state_store=self.ui_state
            )
            row.grid(row=idx, column=0, sticky="ew", padx=4, pady=2)

            sep = ttk.Separator(rows_container, orient='horizontal')
            sep.grid(row=idx + 1, column=0, sticky="ew", padx=5, pady=(2, 2))

        self.progress = ttk.Progressbar(lists_tab, orient='horizontal', mode='determinate')
        self.progress.pack(fill='x', pady=(10, 0))
        self.progress.pack_forget()

        other_inner = tk.Frame(other_tab)
        other_inner.pack(fill='both', expand=True)

        tools_frame = ttk.LabelFrame(other_tab, text="Pojedynczy PDF")
        first = other_tab.winfo_children()[0]
        tools_frame.pack(fill="x", padx=10, pady=10, before=first)

        buttons = ttk.Frame(tools_frame)
        buttons.pack(anchor="w", padx=8, pady=8)

        single_btn = ttk.Button(
            buttons,
            text="Generuj",
            command=self.generate_single_file
        )
        single_btn.grid(row=0, column=0, padx=(0, 10), pady=(0, 6), sticky="w")
        Tooltip(single_btn, "Wybierz pojedynczy plik TXT i wygeneruj PDF")

        ranking_frame = ttk.LabelFrame(other_inner, text="Ranking hodowców")
        ranking_frame.pack(fill='x', padx=10, pady=10)

        type_frame = ttk.Frame(ranking_frame)
        type_frame.grid(row=0, column=0, padx=8, pady=(8, 4), sticky='w')

        ttk.Label(type_frame, text="Typ lotu:").grid(row=0, column=0, padx=(0, 6))
        for idx, (lot_type, var) in enumerate(self.ranking_type_vars.items(), start=1):
            ttk.Checkbutton(
                type_frame,
                text=lot_type,
                variable=var
            ).grid(row=0, column=idx, padx=4)

        limit_frame = ttk.Frame(ranking_frame)
        limit_frame.grid(row=1, column=0, padx=8, pady=(0, 8), sticky='w')
        ttk.Label(limit_frame, text="Liczba konkursów:").grid(row=0, column=0, padx=(0, 6))
        limit_spin = tk.Spinbox(
            limit_frame,
            from_=1,
            to=999999,
            width=6,
            textvariable=self.ranking_limit_var,
        )
        limit_spin.grid(row=0, column=1, sticky='w')

        ranking_btn = ttk.Button(
            ranking_frame,
            text="Wczytaj WSP_LKON.TXT",
            command=self.generate_ranking_from_wsp
        )
        ranking_btn.grid(row=2, column=0, padx=8, pady=(0, 8), sticky='w')
        Tooltip(ranking_btn, "Wybierz plik WSP_LKON.TXT i utwórz punktację")

        # STERDRUK przeniesiony do Ustawień → zakładka INNE

    def _on_generate_row(self, branch: Branch, lot_number: str, additional: bool, rating: bool, league2: bool):
        self.generate_for_branch(branch, lot_number, additional, rating, league2)

    def _on_create_dir(self, branch: Branch, lot_number: str):
        try:
            lot_number = lot_number.strip()
            if not lot_number:
                notifier.show_warning("Podaj poprawny numer lotu!")
                return

            base_path, final_path = self.lot_pdf_service.create_lot_dirs(
                output_dir=branch.output,
                is_old_pigeon=self.is_old_pigeon,
                lot_number=lot_number,
            )

            log_info(f"Utworzono katalogi dla lotu nr.:{lot_number} w {final_path}")
            notifier.show_success(f"Utworzono katalogi dla lotu nr.:\n{lot_number}")

        except ValueError as ve:
            notifier.show_warning(str(ve))
            log_error(f"Błąd walidacji numeru lotu: {ve}")
        except Exception as e:
            notifier.show_error("Nie udało się utworzyć katalogu lotu.")
            log_error(f"Błąd tworzenia katalogów: {e}")

    def generate_for_branch(self, branch: Branch, lot_number: str, additional_list: bool, rating_list: bool, league2_list: bool):
        if not lot_number.strip().isdigit():
            notifier.show_warning('Podaj poprawny numer lotu!')
            return

        def update_progress(value, maximum):
            self.progress['value'] = value
            self.progress['maximum'] = maximum
            self.progress.pack(fill='x', padx=10, pady=10)
            self.frame.update_idletasks()

        self.progress['value'] = 0
        self.progress.pack()
        self.lot_pdf_service.generate_pdfs_for_lot(
            branch,
            lot_number,
            additional_list,
            rating_list,
            league2_list,
            progress_callback=update_progress
        )
        # Po głównej generacji spróbuj utworzyć osobny PDF z II ligą (jeśli istnieje katalog/plik)
        try:
            self.lot_pdf_service.generate_league2_only_for_lot(
                branch,
                lot_number,
                additional_list=additional_list,
                progress_callback=update_progress
            )
        except Exception:
            pass
        self.progress.pack_forget()

    def generate_single_file(self):
        file_path = filedialog.askopenfilename(filetypes=[('Text Files', ('*.TXT', '*.txt'))])
        if file_path:
            try:
                log_info(f'Generowanie PDF dla pliku: {file_path}')
                PdfGeneratorService().generate_single_pdf(file_path)
                notifier.show_success('Poprawnie zapisano plik PDF')
            except Exception as e:
                log_error(f'Wystąpił błąd generowania pliku PDF: {e}')
                notifier.show_error(str(e))

    def generate_ranking_from_wsp(self):
        file_path = filedialog.askopenfilename(filetypes=[('Listy konkursowe', ('WSP_LKON.TXT', '*.TXT'))])
        if not file_path:
            return
        try:
            log_info(f'Generowanie rankingu z pliku: {file_path}')
            selected_types = [
                lot_type
                for lot_type, var in self.ranking_type_vars.items()
                if var.get()
            ]
            if not selected_types:
                selected_types = ['C']

            try:
                requested_limit = int(self.ranking_limit_var.get())
            except (TypeError, ValueError):
                requested_limit = RankingService.DEFAULT_TOP_LIMIT

            output_path = self.ranking_service.generate_scoreboard(
                file_path,
                allowed_types=selected_types,
                top_limit=requested_limit,
            )
            notifier.show_success(f'Zapisano plik Punktacja.TXT:\n{output_path}')
        except FileNotFoundError as err:
            notifier.show_warning(str(err))
            log_error(f'Niepowodzenie rankingu: {err}')
        except Exception as exc:
            log_error(f'Wystąpił błąd generowania rankingu: {exc}')
            notifier.show_error(str(exc))

    def _load_is_old(self) -> bool:
        """Wczytaj is_old_pigeon z settings.json (domyślnie False = MŁODE)."""
        try:
            if not os.path.exists(config.SETTINGS_FILE):
                return False
            with open(config.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return bool(data.get('is_old_pigeon', False))
        except Exception:
            return False

    def _title_text(self) -> str:
        return f"Loty gołębi {'STARYCH' if self.is_old_pigeon else 'MŁODYCH'}"

    # (brak) – przeniesione do SettingsScene

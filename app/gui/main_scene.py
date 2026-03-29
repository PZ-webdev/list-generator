import os
import json
from datetime import datetime
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
    _POLISH_WEEKDAYS = (
        'Poniedziałek',
        'Wtorek',
        'Środa',
        'Czwartek',
        'Piątek',
        'Sobota',
        'Niedziela',
    )
    _POLISH_MONTHS = (
        'stycznia',
        'lutego',
        'marca',
        'kwietnia',
        'maja',
        'czerwca',
        'lipca',
        'sierpnia',
        'września',
        'października',
        'listopada',
        'grudnia',
    )

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
        self.start_clock_branch_var = tk.StringVar(master=self.frame, value='')
        self.start_clock_output_var = tk.StringVar(master=self.frame, value='')

        self.is_old_pigeon = self._load_is_old()

        self.title_label = None
        self.progress = None

    def build(self):
        header = tk.Frame(
            self.frame,
            bg='#f7f9fc',
            highlightbackground='#b8c4d6',
            highlightthickness=1,
            bd=0,
            padx=12,
            pady=10,
        )
        header.pack(fill='x', padx=10, pady=(10, 8))

        accent = tk.Frame(header, bg='#2f6ea5', height=3)
        accent.pack(fill='x', side='top', pady=(0, 10))

        content = tk.Frame(header, bg='#f7f9fc')
        content.pack(fill='x')

        title_wrap = tk.Frame(content, bg='#f7f9fc')
        title_wrap.pack(side='left', anchor='w')

        tk.Label(
            title_wrap,
            text=self._today_text(),
            font=('Arial', 10),
            foreground='#2f3b52',
            anchor='w',
            bg='#f7f9fc',
        ).pack(anchor='w')

        self.title_label = tk.Label(
            title_wrap,
            text=self._title_text(),
            font=('Arial', 12, 'bold'),
            anchor='w',
            bg='#f7f9fc',
            fg='#142235',
        )
        self.title_label.pack(anchor='w', pady=(2, 0))

        btn_cfg = tk.Button(
            content,
            text='Oddziały',
            command=self.app.show_branches_scene
        )
        btn_cfg.pack(side='right')
        Tooltip(btn_cfg, "Przejdź do zarządzania oddziałami")

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

        start_clock_frame = ttk.LabelFrame(other_inner, text="Lista startowo-zegarowa")
        start_clock_frame.pack(fill='x', padx=10, pady=10)

        branches = self.branch_service.get_all()
        branch_options = [self._format_branch_option(branch) for branch in branches]
        if branch_options and not self.start_clock_branch_var.get():
            self.start_clock_branch_var.set(branch_options[0])

        branch_frame = ttk.Frame(start_clock_frame)
        branch_frame.grid(row=0, column=0, padx=8, pady=(8, 4), sticky='w')
        ttk.Label(branch_frame, text="Oddział:").grid(row=0, column=0, padx=(0, 6))
        branch_combo = ttk.Combobox(
            branch_frame,
            textvariable=self.start_clock_branch_var,
            values=branch_options,
            width=28,
            state='readonly'
        )
        branch_combo.grid(row=0, column=1, sticky='w')
        branch_combo.bind("<<ComboboxSelected>>", lambda _event: self._update_start_clock_output_label())

        start_clock_btn = ttk.Button(
            start_clock_frame,
            text="Generuj",
            command=self._on_generate_start_clock,
        )
        start_clock_btn.grid(row=1, column=0, padx=8, pady=(0, 4), sticky='w')
        Tooltip(start_clock_btn, "Wygeneruj PDF z pliku DANE_GL/DRLSTZEG.TXT wybranego oddziału")

        ttk.Label(
            start_clock_frame,
            textvariable=self.start_clock_output_var,
            foreground="#555",
            justify='left',
            wraplength=520,
        ).grid(row=2, column=0, padx=8, pady=(0, 8), sticky='w')
        self._update_start_clock_output_label()

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

    def _on_generate_start_clock(self):
        try:
            branch = self._get_selected_start_clock_branch()
            self.generate_start_clock_for_branch(branch)
        except Exception as e:
            log_error(f'Błąd generowania listy startowo-zegarowej: {e}')
            notifier.show_error(str(e))

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

    def generate_start_clock_for_branch(self, branch: Branch):
        output_path = self.lot_pdf_service.generate_start_clock_pdf_for_lot(branch)
        if output_path:
            notifier.show_success('Wygenerowano listę startowo-zegarową.')

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

    def _today_text(self) -> str:
        today = datetime.today()
        weekday = self._POLISH_WEEKDAYS[today.weekday()]
        month = self._POLISH_MONTHS[today.month - 1]
        return f'{weekday}, {today.day} {month}'

    def _format_branch_option(self, branch: Branch) -> str:
        return f"{branch.number} {branch.name}"

    def _get_selected_start_clock_branch(self) -> Branch:
        selected = (self.start_clock_branch_var.get() or '').strip()
        for branch in self.branch_service.get_all():
            if self._format_branch_option(branch) == selected:
                return branch
        raise ValueError('Wybierz oddział do wygenerowania listy startowo-zegarowej.')

    def _update_start_clock_output_label(self) -> None:
        try:
            branch = self._get_selected_start_clock_branch()
            output_path = self.lot_pdf_service.pdf_generator.start_clock_service.get_output_filename(
                branch=branch,
                output_dir=branch.output,
            )
            self.start_clock_output_var.set(f"Zapis do: {output_path}")
        except Exception:
            self.start_clock_output_var.set("Zapis do: -")

    # (brak) – przeniesione do SettingsScene

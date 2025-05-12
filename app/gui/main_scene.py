import config
import tkinter as tk

from tkinter import filedialog, ttk

from app.dto.branch import Branch
from app.gui.components.tooltip import Tooltip
from app.utils import notifier
from app.utils.logger import log_info, log_error
from app.core.branch_service import BranchService
from app.core.lot_pdf_service import LotPdfService
from app.core.pdf_generator_service import PdfGeneratorService


class MainScene:
    def __init__(self, app, branches_file=config.BRANCHES_FILE):
        self.app = app
        self.frame = tk.Frame(app.main_frame)
        self.frame.pack(fill='both', expand=True)

        self.branch_service = BranchService(branches_file)
        self.lot_pdf_service = LotPdfService(PdfGeneratorService())

    def build(self):
        tk.Label(self.frame, text='Lista oddziałów', font=('Arial', 12, 'bold')).pack(pady=10)

        for branch in self.branch_service.get_all():
            row = tk.Frame(self.frame, bd=1, relief='solid')
            row.pack(fill='x', pady=5, padx=10)

            row.columnconfigure(0, weight=1)

            tk.Label(row, text=branch.name, width=20, anchor='w').grid(row=0, column=0, padx=5, sticky='w')
            tk.Label(row, text='Lot nr:', anchor='w').grid(row=0, column=1, padx=5, sticky='e')

            lot_entry = tk.Entry(row, width=3)
            lot_entry.grid(row=0, column=2, padx=5, sticky='w')
            Tooltip(lot_entry, "Podaj numer lotu")

            vcmd = (self.frame.register(lambda nv: nv.isdigit() or nv == ''), '%P')
            lot_entry.config(validate='key', validatecommand=vcmd)

            additional_list_var = tk.BooleanVar()
            cb1 = tk.Checkbutton(row, variable=additional_list_var)
            cb1.grid(row=0, column=3, padx=3, sticky='w')
            Tooltip(cb1, "Wygeneruj listy zamknięte")

            generate_btn = tk.Button(
                row,
                text='GENERUJ',
                command=lambda b=branch, le=lot_entry, al=additional_list_var:
                self.generate_for_branch(b, le.get(), al.get())
            )
            generate_btn.grid(row=0, column=4, padx=5, sticky='e')
            Tooltip(generate_btn, "Wygeneruj listy PDF dla podanego lotu i wybranego oddziału")

        self.progress = ttk.Progressbar(self.frame, orient='horizontal', mode='determinate')
        self.progress.pack(fill='x', padx=10, pady=10)
        self.progress.pack_forget()

        bottom_frame = tk.Frame(self.frame)
        bottom_frame.pack(fill='x', side='bottom', pady=20)

        btn = tk.Button(
            bottom_frame,
            text='Pojedynczy PDF',
            command=self.generate_single_file
        )
        btn.pack(side='right', padx=10)
        Tooltip(btn, "Wybierz pojedynczy plik TXT i wygeneruj PDF")

    def generate_for_branch(self, branch: Branch, lot_number: str, additional_list: bool):
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
        self.lot_pdf_service.generate_pdfs_for_lot(branch, lot_number, additional_list,
                                                   progress_callback=update_progress)
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

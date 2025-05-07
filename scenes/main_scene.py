import tkinter as tk
import re
import json
import os
from tkinter import ttk, filedialog

import config
from components.tooltip import Tooltip
from service.pdf_generator import generate_pdf_to_path, generate_single_pdf
from utils import notifier
from utils.logger import log_info, log_error, log_warning

BRANCHES_FILE = config.BRANCHES_FILE


class MainScene:
    def __init__(self, app):
        self.app = app
        self.frame = tk.Frame(app.main_frame)
        self.frame.pack(fill='both', expand=True)
        self.branches = []
        self.load_branches()

    def build(self):
        tk.Label(self.frame, text='Lista oddziałów', font=('Arial', 12, 'bold')).pack(pady=10)

        for branch in self.branches:
            row = tk.Frame(self.frame, bd=1, relief='solid')
            row.pack(fill='x', pady=5, padx=10)

            tk.Label(row, text=branch['name'], width=20, anchor='w').pack(side='left', padx=5)
            tk.Label(row, text='lot:', anchor='w').pack(side='left', padx=5)

            lot_entry = tk.Entry(row, width=10)
            lot_entry.pack(side='left', padx=5)
            Tooltip(lot_entry, "Podaj numer lotu")

            def validate_digit_input(new_value):
                return new_value.isdigit() or new_value == ''

            vcmd = (self.frame.register(validate_digit_input), '%P')
            lot_entry.config(validate='key', validatecommand=vcmd)

            additional_list_var = tk.BooleanVar()
            checkbox = tk.Checkbutton(row, variable=additional_list_var)
            checkbox.pack(side='left', padx=5)
            Tooltip(checkbox, "Wygeneruj listy zamknięte")

            generate_for_branch_button = tk.Button(
                row,
                text='GENERUJ',
                command=lambda b=branch, le=lot_entry, al=additional_list_var: self.generate_for_branch(
                    b, le.get(), al.get()
                )
            )
            generate_for_branch_button.pack(side='right', padx=5)
            Tooltip(generate_for_branch_button, "Wygeneruj listy PDF dla podanego lotu i wybranego oddziału")

        self.progress = ttk.Progressbar(self.frame, orient='horizontal', mode='determinate')
        self.progress.pack(fill='x', padx=10, pady=10)
        self.progress.pack_forget()

        bottom_frame = tk.Frame(self.frame)
        bottom_frame.pack(fill='x', side='bottom', pady=20)

        single_pdf_button = tk.Button(
            bottom_frame,
            text='Pojedynczy PDF',
            command=self.generate_single_file
        )
        single_pdf_button.pack(side='right', padx=10)
        Tooltip(single_pdf_button, "Wybierz pojedynczy plik TXT i wygeneruj PDF")

    def load_branches(self):
        if os.path.exists(BRANCHES_FILE):
            with open(BRANCHES_FILE, 'r', encoding='utf-8') as f:
                self.branches = json.load(f)

    def generate_for_branch(self, branch, lot_number, additional_list):
        if not lot_number.strip().isdigit():
            notifier.show_warning('Podaj poprawny numer lotu!')
            return

        input_dir = branch['input']
        output_dir = branch['output']

        log_info(f'Start generowania dla oddziału: {branch["name"]}, lot: {lot_number}')
        os.makedirs(output_dir, exist_ok=True)

        pattern = self.get_lot_pattern(lot_number)
        log_info(f'Używam wzorca regex: {pattern.pattern}')

        matched_folder = None
        for folder in os.listdir(input_dir):
            log_info(f'Sprawdzam folder: {folder}')
            if pattern.match(folder):
                matched_folder = folder
                log_info(f'Znaleziono dopasowany folder: {matched_folder}')
                break

        if not matched_folder:
            log_warning(f'Nie znaleziono katalogu LOT_S_{lot_number} w {input_dir}')
            notifier.show_warning(f'Nie znaleziono katalogu dla lotu {lot_number}')
            return

        lot_path = os.path.join(input_dir, matched_folder)

        matching_files = []
        for root, _, files in os.walk(lot_path):
            for file in files:
                if file.upper().startswith('LKON_S') and file.upper().endswith('.TXT'):
                    matching_files.append((root, file))

        total_files = len(matching_files)
        if total_files == 0:
            return

        self.progress['value'] = 0
        self.progress['maximum'] = total_files
        self.progress.pack(fill='x', padx=10, pady=10)
        self.frame.update_idletasks()

        for i, (root, file) in enumerate(matching_files, 1):
            relative_path = os.path.relpath(root, input_dir)
            target_folder = os.path.join(output_dir, relative_path)
            os.makedirs(target_folder, exist_ok=True)

            txt_path = os.path.join(root, file)
            output_pdf_path = os.path.join(target_folder, os.path.splitext(file)[0] + '.pdf')

            try:
                log_info(f'Generowanie PDF z pliku: {txt_path}')
                generate_pdf_to_path(txt_path, output_pdf_path, additional_list)
                log_info(f'Zapisano PDF do: {output_pdf_path}')
            except Exception as e:
                log_error(f'Błąd generowania PDF dla {txt_path}: {e}')
                notifier.show_error(f'Błąd przy {txt_path}: {e}')

            self.progress['value'] = i
            self.frame.update_idletasks()

        notifier.show_success(f'Wygenerowano {total_files} plików PDF dla lotu nr.: {lot_number}')
        self.progress.pack_forget()

    def generate_single_file(self):
        file_path = filedialog.askopenfilename(filetypes=[('Text Files', ('*.TXT', '*.txt'))])
        if file_path:
            try:
                log_info(f'Generowanie PDF dla pliku: {file_path}')

                # generate and save file
                generate_single_pdf(file_path)
                notifier.show_success('Poprawnie zapisano plik PDF')
            except Exception as e:
                log_error('Wystąpił błąd generowania pliku PDF')
                notifier.show_error(str(e))

    def get_lot_pattern(self, lot_number):
        lot_str = f"{int(lot_number):02d}"
        pattern = re.compile(rf'^LOT_S_{lot_str}\.\d+$')
        return pattern

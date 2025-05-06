import tkinter as tk
import json
import os
import re
import config
from tkinter import filedialog, ttk
from service.pdf_generator import generate_pdf, generate_pdf_to_path
from utils import notifier
from components.tooltip import Tooltip
from utils.logger import log_info, log_error


class MainScene:
    def __init__(self, app):
        self.app = app
        self.frame = tk.Frame(app.main_frame)
        self.frame.pack(fill='both', expand=True)

    def build(self):
        btn_file = tk.Button(self.frame, text='Wybierz plik TXT', command=self.select_file)
        btn_file.pack(pady=10)
        Tooltip(btn_file, "Kliknij, aby wybrać plik i wygenerować PDF")

        separator = tk.Frame(self.frame, height=2, bd=1, relief='sunken')
        separator.pack(fill='x', padx=5, pady=15)

        btn_generate = tk.Button(self.frame, text='Generuj ze ścieżek', command=self.generate_from_paths)
        btn_generate.pack(pady=10)
        Tooltip(btn_generate, "Kliknij, aby wygenerować PDF z zapisanych ścieżek")

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[('Text Files', ('*.TXT', '*.txt'))])
        if file_path:
            try:
                log_info(f'Generowanie PDF dla pliku: {file_path}')

                # generate and save file
                generate_pdf(file_path)
                notifier.show_success('Poprawnie zapisano plik PDF')
            except Exception as e:
                log_error('Wystąpił błąd generowania pliku PDF')
                notifier.show_error(str(e))

    def generate_from_paths(self):
        try:
            log_info('Rozpoczynam przetwarzanie ścieżek z settings.json')

            with open(config.SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                mappings = data.get('mappings', [])

            progress = ttk.Progressbar(self.frame, orient='horizontal', length=400, mode='determinate')
            progress.pack(pady=10)

            all_files = []
            pattern = re.compile(r'LKON_S\d+\.TXT', re.IGNORECASE)

            for entry in mappings:
                input_dir = entry.get('input')
                if not input_dir:
                    continue
                for root, dirs, files in os.walk(input_dir):
                    if not (re.search(r'SEKCJA\.\d+', root) or os.path.basename(root).startswith('LOT_S_')):
                        continue
                    for file in files:
                        if pattern.match(file):
                            all_files.append((root, file, entry['output'], input_dir))

            progress['maximum'] = len(all_files)

            for idx, (root, file, output_dir, input_dir) in enumerate(all_files, start=1):
                relative_path = os.path.relpath(root, input_dir)
                target_dir = os.path.join(output_dir, relative_path)
                os.makedirs(target_dir, exist_ok=True)

                txt_path = os.path.join(root, file)
                output_pdf_path = os.path.join(target_dir, os.path.splitext(file)[0] + '.pdf')

                try:
                    log_info(f'Generowanie PDF z pliku: {txt_path}')
                    generate_pdf_to_path(txt_path, output_pdf_path)
                    log_info(f'Zapisano PDF do: {output_pdf_path}')
                except Exception as e:
                    log_error(f'Błąd przy pliku {txt_path}: {e}')
                    notifier.show_error(f'Błąd przy {txt_path}: {e}')

                progress['value'] = idx
                self.frame.update_idletasks()

            notifier.show_success('Wszystkie pliki zostały przetworzone.')
            log_info('Zakończono przetwarzanie wszystkich plików.')

        except Exception as e:
            log_error(f'Błąd wczytywania ścieżek: {e}')
            notifier.show_error(f'Błąd wczytywania ścieżek: {e}')

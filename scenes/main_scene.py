import tkinter as tk
import json
import os
import re
import shutil
from tkinter import filedialog
from service.pdf_generator import generate_pdf, generate_pdf_bytes, generate_pdf_to_path
from utils import notifier
from components.tooltip import Tooltip
from utils.logger import log_info, log_warning, log_error


class MainScene:
    def __init__(self, app):
        self.app = app
        self.frame = tk.Frame(app.main_frame)
        self.frame.pack(fill='both', expand=True)

    def build(self):
        label = tk.Label(self.frame, text='Wybierz plik TXT i generuj PDF', font=('Arial', 12, 'bold'))
        label.pack(pady=10)

        btn_file = tk.Button(self.frame, text='Wybierz plik TXT', command=self.select_file)
        btn_file.pack(pady=10)

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
            with open('settings.json', 'r') as f:
                data = json.load(f)
                mappings = data.get('mappings', [])

            pattern = re.compile(r'LKON_S\d+\.TXT', re.IGNORECASE)

            for idx, entry in enumerate(mappings):
                input_dir = entry.get('input')
                output_dir = entry.get('output')

                log_info(f'[{idx + 1}] Przetwarzanie: input={input_dir}, output={output_dir}')

                if not input_dir or not output_dir:
                    log_warning(f'[{idx + 1}] Pominięto wpis bez input/output')
                    continue

                for root, dirs, files in os.walk(input_dir):
                    if not (re.search(r'SEKCJA\.\d+', root) or os.path.basename(root).startswith('LOT_S_')):
                        continue

                    relative_path = os.path.relpath(root, input_dir)
                    target_dir = os.path.join(output_dir, relative_path)
                    os.makedirs(target_dir, exist_ok=True)

                    for file in files:
                        if pattern.match(file):
                            txt_path = os.path.join(root, file)
                            try:
                                log_info(f'Generowanie PDF z pliku: {txt_path}')
                                output_pdf_path = os.path.join(target_dir, os.path.splitext(file)[0] + '.pdf')
                                generate_pdf_to_path(txt_path, output_pdf_path)
                                log_info(f'Zapisano PDF do: {output_pdf_path}')
                            except Exception as e:
                                log_error(f'Błąd przy pliku {txt_path}: {e}')
                                notifier.show_error(f'Błąd przy {txt_path}: {e}')
        except Exception as e:
            log_error(f'Błąd wczytywania ścieżek: {e}')
            notifier.show_error(f'Błąd wczytywania ścieżek: {e}')

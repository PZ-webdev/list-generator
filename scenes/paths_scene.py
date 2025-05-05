import tkinter as tk
from tkinter import ttk, filedialog
import json
import os
from config import SETTINGS_FILE
from dto.settings_dto import SettingsDTO
from utils import notifier

class PathsScene:
    def __init__(self, app):
        self.app = app
        self.entries = []

    def build(self):
        frame = ttk.Frame(self.app.main_frame)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        for i in range(5):
            section = ttk.LabelFrame(frame, text=f'Opcja {i + 1}')
            section.pack(fill='x', pady=5)

            in_frame = ttk.Frame(section)
            in_frame.pack(fill='x', pady=2)
            in_label = ttk.Label(in_frame, text='Skąd:')
            in_label.pack(side='left')
            in_entry = ttk.Entry(in_frame, width=40)
            in_entry.pack(side='left', expand=True, fill='x', padx=(5, 5))
            in_btn = ttk.Button(in_frame, text='Wybierz', command=lambda e=in_entry: self.choose_directory(e))
            in_btn.pack(side='left')

            out_frame = ttk.Frame(section)
            out_frame.pack(fill='x', pady=2)
            out_label = ttk.Label(out_frame, text='Dokąd:')
            out_label.pack(side='left')
            out_entry = ttk.Entry(out_frame, width=40)
            out_entry.pack(side='left', expand=True, fill='x', padx=(5, 5))
            out_btn = ttk.Button(out_frame, text='Wybierz', command=lambda e=out_entry: self.choose_directory(e))
            out_btn.pack(side='left')

            self.entries.append({'input': in_entry, 'output': out_entry})

        save_button = ttk.Button(frame, text='Zapisz ścieżki', command=self.save_paths)
        save_button.pack(pady=10)

        self.load_saved_paths()

    def choose_directory(self, entry):
        directory = filedialog.askdirectory()
        if directory:
            entry.delete(0, tk.END)
            entry.insert(0, directory)

    def save_paths(self):
        mappings = []
        for pair in self.entries:
            mappings.append({
                'input': pair['input'].get(),
                'output': pair['output'].get()
            })
        dto = SettingsDTO(mappings=mappings)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(dto.to_dict(), f, indent=4)
        notifier.show_success('Ścieżki zostały zapisane.')

    def load_saved_paths(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE) as f:
                data = json.load(f)
            dto = SettingsDTO.from_dict(data)
            for entry_pair, saved in zip(self.entries, dto.mappings):
                entry_pair['input'].insert(0, saved.get('input', ''))
                entry_pair['output'].insert(0, saved.get('output', ''))

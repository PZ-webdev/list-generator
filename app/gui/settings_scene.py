import os
import json
import tkinter as tk
from tkinter import ttk, filedialog

import config
from app.dto.settings_dto import SettingsDTO
from app.utils.logger import log_warning
from app.utils.notifier import show_success, show_error

labels = [
    ("Oddział", "filename_branch"),
    ("Oddział – l. zam", "filename_branch_closed"),
    ("Sekcja", "filename_section"),
    ("Sekcja – l. zam", "filename_section_closed"),
]

default_templates = {
    "filename_branch": "{BRANCH} {DATE} LISTA ODDZIAŁOWA.pdf",
    "filename_branch_closed": "{BRANCH} {DATE} LISTA ODDZIAŁOWA - ZAMKNIĘTA.pdf",
    "filename_section": "{BRANCH} {DATE} SEKCJA nr. {SECTION}.pdf",
    "filename_section_closed": "{BRANCH} {DATE} SEKCJA nr. {SECTION} - ZAMKNIĘTA.pdf",
}


class SettingsScene:
    def __init__(self, app):
        self.app = app
        self.frame = ttk.Frame(self.app.main_frame)

        self.is_old_var = tk.BooleanVar(value=False)

    def build(self):
        self.frame.pack(fill='both', expand=True)
        tabs = ttk.Notebook(self.frame)

        self.build_lists_tab(tabs)

        tabs.pack(fill='both', expand=True, padx=10, pady=10)

        save_btn = ttk.Button(self.frame, text="Zapisz", command=self.save_settings)
        save_btn.pack(pady=10)

        self.load_settings()

    def build_lists_tab(self, tabs: ttk.Notebook):
        lists_tab = ttk.Frame(tabs)
        tabs.add(lists_tab, text="Ogólne")

        global_frame = ttk.LabelFrame(lists_tab, text="Ustawienia globalne (sezon)")
        global_frame.grid(row=0, column=0, padx=20, pady=(10, 0), sticky='nsew')

        chk = ttk.Checkbutton(
            global_frame,
            text="Generuj dla gołębi STARYCH (odznaczone = MŁODE)",
            variable=self.is_old_var,
            command=lambda: self.status_label.config(text=self._status_text())
        )
        chk.grid(row=0, column=0, sticky='w', padx=8, pady=8)

        self.status_label = ttk.Label(global_frame, text=self._status_text())
        self.status_label.grid(row=0, column=1, sticky='w', padx=8, pady=8)

        frame_templates = ttk.LabelFrame(lists_tab, text="Nazwy plików PDF")
        frame_templates.grid(row=1, column=0, padx=20, pady=10, sticky='nsew')

        self.template_vars = {}
        for i, (label, key) in enumerate(labels):
            ttk.Label(frame_templates, text=label).grid(row=i, column=0, sticky='e', padx=5, pady=3)
            default_value = default_templates.get(key, "")
            var = tk.StringVar(value=default_value)
            self.template_vars[key] = var
            ttk.Entry(frame_templates, textvariable=var, width=50).grid(row=i, column=1, padx=5, pady=3)

        frame_files = ttk.LabelFrame(lists_tab, text="Kolejność doklejanych plików")
        frame_files.grid(row=2, column=0, padx=20, pady=10, sticky='nsew')

        self.file_order = ['PHD_1AS.TXT', 'PHDOD1A.TXT']
        self.file_listbox = tk.Listbox(frame_files, height=4, width=40)
        self.file_listbox.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.refresh_file_listbox()

        tk.Button(frame_files, text="Góra", command=self.move_up).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        tk.Button(frame_files, text="Dół", command=self.move_down).grid(row=1, column=1, sticky='w', padx=5, pady=5)

        frame_mask = ttk.LabelFrame(lists_tab, text="Maskowanie nazw obrączek")
        frame_mask.grid(row=3, column=0, padx=20, pady=10, sticky='nsew')

        self.ring_mask_var = tk.StringVar(value="#####")
        ttk.Entry(frame_mask, textvariable=self.ring_mask_var, width=40).grid(row=0, column=0, padx=5, pady=5)

        frame_output_dir = ttk.LabelFrame(lists_tab, text="Domyślny katalog dla pojedynczego PDF")
        frame_output_dir.grid(row=4, column=0, padx=20, pady=10, sticky='nsew')

        self.default_pdf_dir = tk.StringVar(value="")
        entry = ttk.Entry(frame_output_dir, textvariable=self.default_pdf_dir, width=50, state='readonly')
        entry.grid(row=0, column=0, padx=5, pady=5)

        def choose_directory():
            selected_dir = filedialog.askdirectory()
            if selected_dir:
                self.default_pdf_dir.set(selected_dir)

        tk.Button(frame_output_dir, text="Wybierz katalog", command=choose_directory).grid(
            row=0, column=1, padx=5, pady=5
        )

    def load_settings(self):
        data = {}

        try:
            with open(config.SETTINGS_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                if isinstance(raw, dict):
                    data = raw
        except FileNotFoundError:
            data = {}
        except Exception as e:
            log_warning(f"Nie udało się odczytać settings.json: {e}")
            data = {}

        is_old = bool(data.get("is_old_pigeon", data.get("is_old_pigeon", False)))
        self.is_old_var.set(is_old)
        if hasattr(self, "status_label"):
            self.status_label.config(text=self._status_text())

        for key in self.template_vars:
            value = (data.get(key) or "").strip()
            self.template_vars[key].set(value if value else default_templates.get(key, ""))

        self.file_order = data.get("attached_files", self.file_order)
        self.refresh_file_listbox()

        self.ring_mask_var.set(data.get("ring_mask", self.ring_mask_var.get()))
        self.default_pdf_dir.set(data.get("default_pdf_dir", self.default_pdf_dir.get()))

    def move_up(self):
        idx = self.file_listbox.curselection()
        if idx and idx[0] > 0:
            i = idx[0]
            self.file_order[i - 1], self.file_order[i] = self.file_order[i], self.file_order[i - 1]
            self.refresh_file_listbox()
            self.file_listbox.select_set(i - 1)

    def move_down(self):
        idx = self.file_listbox.curselection()
        if idx and idx[0] < len(self.file_order) - 1:
            i = idx[0]
            self.file_order[i + 1], self.file_order[i] = self.file_order[i], self.file_order[i + 1]
            self.refresh_file_listbox()
            self.file_listbox.select_set(i + 1)

    def refresh_file_listbox(self):
        self.file_listbox.delete(0, tk.END)
        for file in self.file_order:
            self.file_listbox.insert(tk.END, file)

    def save_settings(self):
        settings = SettingsDTO(
            filename_branch=self.template_vars['filename_branch'].get(),
            filename_branch_closed=self.template_vars['filename_branch_closed'].get(),
            filename_section=self.template_vars['filename_section'].get(),
            filename_section_closed=self.template_vars['filename_section_closed'].get(),
            attached_files=self.file_order,
            ring_mask=self.ring_mask_var.get(),
            default_pdf_dir=self.default_pdf_dir.get(),
            is_old_pigeon=self.is_old_var.get()
        )

        try:
            setattr(settings, "is_old_pigeon", bool(self.is_old_var.get()))
        except Exception:
            pass

        settings.to_json()

        try:
            path = config.SETTINGS_FILE
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    data = {}
            except Exception:
                data = {}

            data["is_old_pigeon"] = bool(self.is_old_var.get())

            os.makedirs(os.path.dirname(path), exist_ok=True)
            tmp = f"{path}.tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, path)
        except Exception as e:
            show_error(f"Nie udało się zapisać ustawienia sezonu: {e}")
            return

        show_success('Zapisano ustawienia!')

    def _status_text(self) -> str:
        return f"Aktualny typ: {'STARE' if self.is_old_var.get() else 'MŁODE'}"

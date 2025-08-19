import tkinter as tk
from tkinter import ttk, filedialog

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

        frame_templates = ttk.LabelFrame(lists_tab, text="Nazwy plików PDF")
        frame_templates.grid(row=0, column=0, padx=20, pady=10, sticky='nsew')

        self.template_vars = {}
        for i, (label, key) in enumerate(labels):
            ttk.Label(frame_templates, text=label).grid(row=i, column=0, sticky='e', padx=5, pady=3)
            default_value = default_templates.get(key, "")
            var = tk.StringVar(value=default_value)
            self.template_vars[key] = var
            ttk.Entry(frame_templates, textvariable=var, width=50).grid(row=i, column=1, padx=5, pady=3)

        frame_files = ttk.LabelFrame(lists_tab, text="Kolejność doklejanych plików")
        frame_files.grid(row=1, column=0, padx=20, pady=10, sticky='nsew')

        self.file_order = ['PHD_1AS.TXT', 'PHDOD1A.TXT']
        self.file_listbox = tk.Listbox(frame_files, height=4, width=40)
        self.file_listbox.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.refresh_file_listbox()

        tk.Button(frame_files, text="Góra", command=self.move_up).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        tk.Button(frame_files, text="Dół", command=self.move_down).grid(row=1, column=1, sticky='w', padx=5, pady=5)

        frame_mask = ttk.LabelFrame(lists_tab, text="Maskowanie nazw obrączek")
        frame_mask.grid(row=2, column=0, padx=20, pady=10, sticky='nsew')

        self.ring_mask_var = tk.StringVar(value="#####")
        ttk.Entry(frame_mask, textvariable=self.ring_mask_var, width=40).grid(row=0, column=0, padx=5, pady=5)

        frame_output_dir = ttk.LabelFrame(lists_tab, text="Domyślny katalog dla pojedynczego PDF")
        frame_output_dir.grid(row=3, column=0, padx=20, pady=10, sticky='nsew')

        self.default_pdf_dir = tk.StringVar(value="")

        entry = ttk.Entry(frame_output_dir, textvariable=self.default_pdf_dir, width=50, state='readonly')
        entry.grid(row=0, column=0, padx=5, pady=5)

        def choose_directory():
            selected_dir = filedialog.askdirectory()
            if selected_dir:
                self.default_pdf_dir.set(selected_dir)

        tk.Button(frame_output_dir, text="Wybierz katalog", command=choose_directory).grid(row=0, column=1, padx=5,
                                                                                           pady=5)

    def load_settings(self):
        try:
            settings = SettingsDTO.from_json()

            for key in self.template_vars:
                value = getattr(settings, key, "").strip()
                if value:
                    self.template_vars[key].set(value)
                else:
                    self.template_vars[key].set(self.default_templates.get(key, ""))

            self.file_order = settings.attached_files
            self.refresh_file_listbox()

            self.ring_mask_var.set(settings.ring_mask)

            self.default_pdf_dir.set(settings.default_pdf_dir)

        except Exception as e:
            log_warning("Nie udało się załadować ustawień, lub nie znaleziono pliku")

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
            default_pdf_dir=self.default_pdf_dir.get()
        )

        settings.to_json()
        show_success('Zapisano ustawienia!')

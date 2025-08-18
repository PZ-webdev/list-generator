import json
import os
import tkinter as tk
from tkinter import filedialog, ttk

import config
from app.core.branch_service import BranchService
from app.dto.branch import Branch
from app.utils.notifier import show_error, show_success
from app.utils.validator import validate_number


class BranchesScene:
    def __init__(self, app, branches_file=config.BRANCHES_FILE):
        self.app = app
        self.service = BranchService(branches_file)

        self.frame = tk.Frame(app.main_frame)
        self.frame.pack(fill='both', expand=True)

        self.form_frame = None
        self.list_frame = None

        self.name_entry = None
        self.input_entry = None
        self.output_entry = None
        self.number_entry = None

        self.is_old_mode = self._load_is_old()

    def build(self):
        self.build_form()
        self.build_list()

    def build_form(self):
        if self.form_frame:
            self.form_frame.destroy()

        self.form_frame = ttk.LabelFrame(
            self.frame,
            text=f"Nowy oddział — tryb: {'STARE' if self.is_old_mode else 'MŁODE'} (nowe wpisy zapiszą ten atrybut)"
        )
        self.form_frame.pack(fill='x', padx=12, pady=(12, 8))

        self.form_frame.grid_columnconfigure(1, weight=1)
        self.form_frame.grid_columnconfigure(2, minsize=110)

        pad_x, pad_y = 8, 6

        ttk.Label(self.form_frame, text="Nazwa:").grid(row=0, column=0, sticky="e", padx=pad_x, pady=pad_y)
        self.name_entry = ttk.Entry(self.form_frame)
        self.name_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=pad_x, pady=pad_y)

        ttk.Label(self.form_frame, text="Numer oddziału:").grid(row=1, column=0, sticky="e", padx=pad_x, pady=pad_y)
        vcmd = (self.form_frame.register(validate_number(999)), '%P')
        self.number_entry = ttk.Entry(self.form_frame, validate='key', validatecommand=vcmd, width=12, justify='center')
        self.number_entry.grid(row=1, column=1, sticky="w", padx=pad_x, pady=pad_y)

        ttk.Label(self.form_frame, text="Katalog roboczy:").grid(row=2, column=0, sticky="e", padx=pad_x, pady=pad_y)
        self.input_entry = ttk.Entry(self.form_frame)
        self.input_entry.grid(row=2, column=1, sticky="ew", padx=pad_x, pady=pad_y)
        ttk.Button(self.form_frame, text="Wybierz", command=self.select_input).grid(row=2, column=2, padx=(0, pad_x),
                                                                                    pady=pad_y, sticky="w")

        ttk.Label(self.form_frame, text="Katalog docelowy:").grid(row=3, column=0, sticky="e", padx=pad_x, pady=pad_y)
        self.output_entry = ttk.Entry(self.form_frame)
        self.output_entry.grid(row=3, column=1, sticky="ew", padx=pad_x, pady=pad_y)
        ttk.Button(self.form_frame, text="Wybierz", command=self.select_output).grid(row=3, column=2, padx=(0, pad_x),
                                                                                     pady=pad_y, sticky="w")

        btns = ttk.Frame(self.form_frame)
        btns.grid(row=4, column=0, columnspan=3, sticky="e", padx=pad_x, pady=(pad_y, 2))

        ttk.Button(btns, text="Wyczyść", command=self.clear_form).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btns, text="Zapisz", command=self.add_branch).grid(row=0, column=1)

        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', padx=12, pady=(8, 10))

    def build_list(self):
        if self.list_frame:
            self.list_frame.destroy()

        self.list_frame = ttk.LabelFrame(
            self.frame,
            text=f"Oddziały — {'STARE' if self.is_old_mode else 'MŁODE'}"
        )
        self.list_frame.pack(fill='both', expand=True, padx=12, pady=(0, 12))

        self.rows_container = ttk.Frame(self.list_frame)
        self.rows_container.pack(fill='x', padx=10, pady=8)

        self.refresh_list()

    def refresh_list(self):
        for w in self.rows_container.winfo_children():
            w.destroy()

        filtered = self.service.get_by_season(self.is_old_mode)

        for i, b in enumerate(filtered):
            row = ttk.Frame(self.rows_container, padding=(5, 3))
            row.pack(fill='x', pady=2)

            row.columnconfigure(0, weight=1)

            ttk.Label(
                row,
                text=f"{self._format_number(b.number)} {b.name.upper()}",
                font=('Arial', 10, 'bold')
            ).grid(row=0, column=0, sticky='w')

            actions = ttk.Frame(row)
            actions.grid(row=0, column=1, sticky='e')
            ttk.Button(actions, text="Edytuj", width=10,
                       command=lambda x=b: self.edit_branch(x)).pack(side='left', padx=(0, 6))
            ttk.Button(actions, text="Usuń", width=8,
                       command=lambda x=b: self.delete_branch(x)).pack(side='left')

            if i < len(filtered) - 1:
                ttk.Separator(self.rows_container, orient='horizontal').pack(
                    fill='x', padx=5, pady=(2, 2)
                )

    def select_input(self):
        path = filedialog.askdirectory()
        if path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, path)

    def select_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, path)

    def add_branch(self):
        name = (self.name_entry.get() or "").strip()
        input_path = (self.input_entry.get() or "").strip()
        output_path = (self.output_entry.get() or "").strip()
        number = (self.number_entry.get() or "").strip()

        if not name or not number or not input_path or not output_path:
            show_error('Wypełnij wszystkie pola!')
            return

        self.service.add_branch(
            name=name,
            number=number,
            input_path=input_path,
            output_path=output_path,
            is_old_pigeon=self.is_old_mode,
        )
        show_success('Dodano oddział!')
        self.refresh_list()
        self.clear_form()

    def delete_branch(self, branch: Branch):
        self.service.delete_branch(branch.id)
        show_success('Usunięto oddział!')
        self.refresh_list()

    def edit_branch(self, branch: Branch):
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, branch.name)
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, branch.input)
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, branch.output)
        self.number_entry.delete(0, tk.END)
        self.number_entry.insert(0, branch.number)

        self.service.delete_branch(branch.id)

    def clear_form(self):
        for e in (self.name_entry, self.input_entry, self.output_entry, self.number_entry):
            e.delete(0, tk.END)

    # --------------- helpers ---------------
    def _load_is_old(self) -> bool:
        """Czy globalnie wybrano STARE? (settings.json -> isOldPigeon)"""
        try:
            if not os.path.exists(config.SETTINGS_FILE):
                return False
            with open(config.SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return bool(data.get("is_old_pigeon", False))
        except Exception:
            return False

    def _format_number(self, num: str) -> str:
        """Zwraca numer w formacie 4-cyfrowym (np. 292 -> 0292)."""
        digits = "".join(ch for ch in (num or "") if ch.isdigit())
        return digits.zfill(4) if digits else (num or "")

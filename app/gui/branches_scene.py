import tkinter as tk
import config

from tkinter import filedialog
from app.core.branch_service import BranchService
from app.dto.branch import Branch
from app.utils.notifier import show_error, show_success


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

    def build(self):
        self.build_form()
        self.build_list()

    def build_form(self):
        self.form_frame = tk.Frame(self.frame)
        self.form_frame.pack(pady=10)

        tk.Label(self.form_frame, text="Nazwa:").grid(row=0, column=0)
        self.name_entry = tk.Entry(self.form_frame, width=40)
        self.name_entry.grid(row=0, column=1)

        tk.Label(self.form_frame, text="Katalog roboczy:").grid(row=1, column=0)
        self.input_entry = tk.Entry(self.form_frame, width=40)
        self.input_entry.grid(row=1, column=1)
        tk.Button(self.form_frame, text="Wybierz", command=self.select_input).grid(row=1, column=2)

        tk.Label(self.form_frame, text="Katalog docelowy:").grid(row=2, column=0)
        self.output_entry = tk.Entry(self.form_frame, width=40)
        self.output_entry.grid(row=2, column=1)
        tk.Button(self.form_frame, text="Wybierz", command=self.select_output).grid(row=2, column=2)

        tk.Button(self.form_frame, text="Dodaj", command=self.add_branch).grid(row=3, column=0, columnspan=3, pady=10)

        separator = tk.Frame(self.frame, height=2, bd=1, relief='sunken')
        separator.pack(fill='x', padx=5, pady=10)

    def build_list(self):
        if self.list_frame:
            self.list_frame.destroy()

        self.list_frame = tk.Frame(self.frame)
        self.list_frame.pack(pady=5)

        self.refresh_list()

    def refresh_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        for branch in self.service.get_all():
            frame = tk.Frame(self.list_frame, bd=1, relief='solid')
            frame.pack(fill='x', pady=2)

            tk.Label(frame, text=branch.name, anchor='w').pack(side='left', padx=5)
            tk.Button(frame, text="Usuń", command=lambda b=branch: self.delete_branch(b)).pack(side='right', padx=2)
            tk.Button(frame, text="Edytuj", command=lambda b=branch: self.edit_branch(b)).pack(side='right', padx=2)

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
        name = self.name_entry.get().strip()
        input_path = self.input_entry.get().strip()
        output_path = self.output_entry.get().strip()

        if not name or not input_path or not output_path:
            show_error('Wypełnij wszystkie pola!')
            return

        self.service.add_branch(name, input_path, output_path)
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

        self.service.delete_branch(branch.id)

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.input_entry.delete(0, tk.END)
        self.output_entry.delete(0, tk.END)

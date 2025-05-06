import tkinter as tk
from tkinter import filedialog
import json
import os
from utils.notifier import show_success, show_error

BRANCHES_FILE = 'branches.json'


class BranchesScene:
    def __init__(self, app):
        self.app = app
        self.frame = tk.Frame(app.main_frame)
        self.frame.pack(fill='both', expand=True)
        self.branches = []
        self.load_branches()

    def build(self):
        # Formularz u góry
        form_frame = tk.Frame(self.frame)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Nazwa:").grid(row=0, column=0)
        self.name_entry = tk.Entry(form_frame, width=40)
        self.name_entry.grid(row=0, column=1)

        tk.Label(form_frame, text="Katalog roboczy:").grid(row=1, column=0)
        self.input_entry = tk.Entry(form_frame, width=40)
        self.input_entry.grid(row=1, column=1)
        tk.Button(form_frame, text="Wybierz", command=self.select_input).grid(row=1, column=2)

        tk.Label(form_frame, text="Katalog docelowy:").grid(row=2, column=0)
        self.output_entry = tk.Entry(form_frame, width=40)
        self.output_entry.grid(row=2, column=1)
        tk.Button(form_frame, text="Wybierz", command=self.select_output).grid(row=2, column=2)

        tk.Button(self.frame, text="Dodaj", command=self.add_branch).pack(pady=5)

        separator = tk.Frame(self.frame, height=2, bd=1, relief='sunken')
        separator.pack(fill='x', padx=5, pady=15)

        # Lista oddziałów poniżej
        self.list_frame = tk.Frame(self.frame)
        self.list_frame.pack(pady=5)
        self.refresh_list()

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

    def load_branches(self):
        if os.path.exists(BRANCHES_FILE):
            with open(BRANCHES_FILE, 'r', encoding='utf-8') as f:
                self.branches = json.load(f)

    def save_branches(self):
        with open(BRANCHES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.branches, f, indent=4, ensure_ascii=False)
        show_success('Zapisano dane oddziałów!')

    def add_branch(self):
        name = self.name_entry.get()
        input_path = self.input_entry.get()
        output_path = self.output_entry.get()

        if not name or not input_path or not output_path:
            show_error('Wypełnij wszystkie pola!')
            return

        next_id = str(max([int(b['id']) for b in self.branches], default=0) + 1)
        new_branch = {'id': next_id, 'name': name, 'input': input_path, 'output': output_path}
        self.branches.append(new_branch)
        self.save_branches()
        self.refresh_list()
        self.clear_form()

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.input_entry.delete(0, tk.END)
        self.output_entry.delete(0, tk.END)

    def refresh_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        for branch in self.branches:
            frame = tk.Frame(self.list_frame, bd=1, relief='solid')
            frame.pack(fill='x', pady=2)

            info = f"{branch['name']}"
            tk.Label(frame, text=info, anchor='w').pack(side='left', padx=5)

            tk.Button(frame, text="Edytuj", command=lambda b=branch: self.edit_branch(b)).pack(side='right', padx=2)
            tk.Button(frame, text="Usuń", command=lambda b=branch: self.delete_branch(b)).pack(side='right', padx=2)

    def delete_branch(self, branch):
        self.branches = [b for b in self.branches if b['id'] != branch['id']]
        self.save_branches()
        self.refresh_list()

    def edit_branch(self, branch):
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, branch['name'])
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, branch['input'])
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, branch['output'])

        self.branches = [b for b in self.branches if b['id'] != branch['id']]

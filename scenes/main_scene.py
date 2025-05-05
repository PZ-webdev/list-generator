import tkinter as tk
from tkinter import ttk, filedialog
from service.pdf_generator import generate_pdf
from utils import notifier
from components.tooltip import Tooltip

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
                output_path = generate_pdf(file_path)
                notifier.show_success(f'PDF zapisany jako: {output_path}')
            except Exception as e:
                notifier.show_error(str(e))

    def generate_from_paths(self):
            # tutaj logika generowania ze ścieżek
        pass
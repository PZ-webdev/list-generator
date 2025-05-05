import tkinter as tk
from tkinter import ttk, filedialog
from service.pdf_generator import generate_pdf
from utils import notifier

class MainScene:
    def __init__(self, app):
        self.app = app

    def build(self):
        ttk.Label(self.app.main_frame, text='Wybierz plik TXT i generuj PDF', font=('Helvetica', 12, 'bold')).pack(pady=10)
        ttk.Button(
            self.app.main_frame,
            text='Wybierz plik TXT',
            command=self.select_file,
            width=40
        ).pack(pady=10)

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[('Text Files', ('*.TXT', '*.txt'))])
        if file_path:
            try:
                output_path = generate_pdf(file_path)
                notifier.show_success(f'PDF zapisany jako: {output_path}')
            except Exception as e:
                notifier.show_error(str(e))

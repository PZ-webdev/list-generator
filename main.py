import tkinter as tk
from tkinter import filedialog, messagebox
from pdf_generator import generate_pdf

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[('Text Files', '*.TXT')])
    if file_path:
        try:
            output_path = generate_pdf(file_path)
            messagebox.showinfo('Sukces', f'PDF zapisany jako: {output_path}')
        except Exception as e:
            messagebox.showerror('Błąd', str(e))

root = tk.Tk()
root.title('Flight Report PDF Generator')

button = tk.Button(root, text='Wybierz plik TXT i generuj PDF', command=select_file, width=40, height=2)
button.pack(padx=20, pady=20)

root.mainloop()

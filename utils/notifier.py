from tkinter import messagebox

def show_success(message, title='Sukces'):
    messagebox.showinfo(title, message)

def show_error(message, title='Błąd'):
    messagebox.showerror(title, message)

def show_warning(message, title='Uwaga'):
    messagebox.showwarning(title, message)

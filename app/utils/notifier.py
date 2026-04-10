from tkinter import messagebox


def show_success(message: str, title: str = 'Sukces') -> None:
    messagebox.showinfo(title, message)


def show_error(message: str, title: str = 'Błąd') -> None:
    messagebox.showerror(title, message)


def show_warning(message: str, title: str = 'Uwaga') -> None:
    messagebox.showwarning(title, message)

import tkinter as tk

from app.gui.pdf_app import PdfApp


def main():
    root = tk.Tk()
    app = PdfApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()

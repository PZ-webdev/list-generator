import pathlib
import re
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
import config


def show_about(parent):
    win = tk.Toplevel(parent)
    win.title("O programie")
    win.transient(parent)
    win.resizable(False, False)
    win.grab_set()

    frm = ttk.Frame(win, padding=16)
    frm.pack(fill="both", expand=True)

    VERSION = (pathlib.Path(__file__).resolve().parents[3] / 'VERSION').read_text().strip()

    ttk.Label(frm, text="Generator list PDF", font=("TkDefaultFont", 12, "bold")).grid(row=0, column=0, sticky="w")
    ttk.Label(frm, text=f"Wersja: v{VERSION}").grid(row=1, column=0, sticky="w", pady=(6, 0))
    ttk.Label(frm, text=f"Autor: {config.APP_AUTHOR}").grid(row=2, column=0, sticky="w")
    ttk.Label(frm, text=f"E-mail: {config.APP_AUTHOR_EMAIL}").grid(row=3, column=0, sticky="w")

    ttk.Separator(frm).grid(row=4, column=0, sticky="ew", pady=10)

    ttk.Label(frm, text="Licencja / informacje:", foreground="#555").grid(row=5, column=0, sticky="w")
    txt = (
        "Program do generowania list PDF.\n"
        "© 2025 – wszelkie prawa zastrzeżone."
    )
    ttk.Label(frm, text=txt, justify="left").grid(row=6, column=0, sticky="w")

    btns = ttk.Frame(frm)
    btns.grid(row=7, column=0, sticky="e", pady=(12, 0))
    ttk.Button(btns, text="Zamknij", command=win.destroy).pack(side="right")

    win.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() - win.winfo_width()) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - win.winfo_height()) // 2
    win.geometry(f"+{x}+{y}")


def show_changelog(parent):
    path = config.CHANGELOG_FILE
    if not path.exists():
        messagebox.showwarning("Dziennik zmian", f"Nie znaleziono pliku:\n{path}")
        return

    win = tk.Toplevel(parent)
    win.title("Dziennik zmian")
    win.geometry("760x560")
    win.transient(parent)
    win.grab_set()

    frm = ttk.Frame(win, padding=8)
    frm.pack(fill="both", expand=True)

    text = tk.Text(frm, wrap="word", padx=8, pady=8, borderwidth=0)
    scroll = ttk.Scrollbar(frm, orient="vertical", command=text.yview)
    text.configure(yscrollcommand=scroll.set)
    text.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    base_font = tkfont.nametofont("TkDefaultFont")
    h1 = base_font.copy()
    h1.configure(size=base_font.cget("size") + 6, weight="bold")
    h2 = base_font.copy()
    h2.configure(size=base_font.cget("size") + 3, weight="bold")
    h3 = base_font.copy()
    h3.configure(size=base_font.cget("size") + 1, weight="bold")
    mono = tkfont.Font(family="TkFixedFont")

    text.tag_configure("h1", font=h1, spacing1=6, spacing3=6)
    text.tag_configure("h2", font=h2, spacing1=6, spacing3=4)
    text.tag_configure("h3", font=h3, spacing1=4, spacing3=2)
    text.tag_configure("li", lmargin1=20, lmargin2=40)
    text.tag_configure("sep", foreground="#888")
    text.tag_configure("code", font=mono, background="#f2f2f2")
    text.tag_configure("bold", font=h3)

    md = path.read_text(encoding="utf-8").splitlines()

    code_span = re.compile(r"`([^`]+)`")

    def insert_with_codes(line: str, extra_tags=()):
        """Wstaw tekst z wyróżnieniem `code`."""
        start = 0
        for m in code_span.finditer(line):
            if m.start() > start:
                text.insert("end", line[start:m.start()], extra_tags)
            text.insert("end", m.group(1), (*extra_tags, "code"))
            start = m.end()
        if start < len(line):
            text.insert("end", line[start:], extra_tags)
        text.insert("end", "\n")

    for raw in md:
        line = raw.rstrip()

        if not line:
            text.insert("end", "\n")
            continue

        if line.startswith("# "):  # H1
            text.insert("end", line[2:] + "\n", ("h1",))
        elif line.startswith("## "):  # H2
            text.insert("end", line[3:] + "\n", ("h2",))
        elif line.startswith("### "):  # H3
            text.insert("end", line[4:] + "\n", ("h3",))
        elif line.startswith("---"):  # pozioma linia/separator z MD
            text.insert("end", "────────────\n", ("sep",))
        elif line.startswith(("- ", "* ")):  # listy
            bullet = "• "
            insert_with_codes(bullet + line[2:], ("li",))
        else:
            insert_with_codes(line)

    text.configure(state="disabled")

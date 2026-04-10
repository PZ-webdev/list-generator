import pathlib
import re
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
import config


def _center_toplevel(win, parent):
    win.update_idletasks()
    width = max(win.winfo_width(), win.winfo_reqwidth())
    height = max(win.winfo_height(), win.winfo_reqheight())
    x = max(parent.winfo_rootx() + (parent.winfo_width() - width) // 2, 0)
    y = max(parent.winfo_rooty() + (parent.winfo_height() - height) // 2, 0)
    win.geometry(f"{width}x{height}+{x}+{y}")


def show_about(parent):
    win = tk.Toplevel(parent)
    win.title("O programie")
    win.transient(parent)
    win.resizable(False, False)
    win.grab_set()
    win.configure(bg="#f3f4f6")

    accent = "#d97706"
    header_bg = "#111827"
    panel_bg = "#f9fafb"
    body_fg = "#1f2937"
    muted_fg = "#6b7280"

    outer = tk.Frame(win, bg="#f3f4f6", padx=18, pady=18)
    outer.pack(fill="both", expand=True)

    card = tk.Frame(
        outer,
        bg=panel_bg,
        highlightbackground="#d1d5db",
        highlightthickness=1,
        bd=0,
    )
    card.pack(fill="both", expand=True)

    VERSION = (pathlib.Path(__file__).resolve().parents[3] / 'VERSION').read_text().strip()

    header = tk.Frame(card, bg=header_bg, padx=20, pady=18)
    header.pack(fill="x")

    tk.Label(
        header,
        text=config.APP_NAME,
        bg=header_bg,
        fg="white",
        font=("Segoe UI", 16, "bold"),
        anchor="w",
    ).pack(fill="x")
    tk.Label(
        header,
        text=config.APP_SUBTITLE,
        bg=header_bg,
        fg="#d1d5db",
        font=("Segoe UI", 10),
        anchor="w",
        pady=4,
    ).pack(fill="x")

    body = tk.Frame(card, bg=panel_bg, padx=20, pady=18)
    body.pack(fill="both", expand=True)

    tk.Label(
        body,
        text=f"Wersja {VERSION}",
        bg=panel_bg,
        fg=accent,
        font=("Segoe UI", 10, "bold"),
        anchor="w",
    ).pack(fill="x")

    tk.Label(
        body,
        text=(
            "Aplikacja przygotowuje czytelne pliki PDF z wynikami i listami "
            "zapisanymi w plikach TXT. Usprawnia generowanie dokumentów "
            "oddziałowych, sekcyjnych oraz dodatkowych zestawień."
        ),
        bg=panel_bg,
        fg=body_fg,
        font=("Segoe UI", 10),
        justify="left",
        wraplength=420,
        anchor="w",
        pady=10,
    ).pack(fill="x")

    meta = tk.Frame(body, bg="#ffffff", padx=14, pady=12)
    meta.pack(fill="x", pady=(0, 14))

    tk.Label(
        meta,
        text="Autor",
        bg="#ffffff",
        fg=muted_fg,
        font=("Segoe UI", 9, "bold"),
        anchor="w",
    ).grid(row=0, column=0, sticky="w")
    tk.Label(
        meta,
        text=config.APP_AUTHOR,
        bg="#ffffff",
        fg=body_fg,
        font=("Segoe UI", 10),
        anchor="w",
    ).grid(row=1, column=0, sticky="w", pady=(2, 10))

    tk.Label(
        meta,
        text="Kontakt",
        bg="#ffffff",
        fg=muted_fg,
        font=("Segoe UI", 9, "bold"),
        anchor="w",
    ).grid(row=2, column=0, sticky="w")
    tk.Label(
        meta,
        text=config.APP_AUTHOR_EMAIL,
        bg="#ffffff",
        fg=body_fg,
        font=("Segoe UI", 10),
        anchor="w",
    ).grid(row=3, column=0, sticky="w", pady=(2, 0))

    btns = tk.Frame(body, bg=panel_bg)
    btns.pack(fill="x", pady=(6, 0))
    tk.Button(
        btns,
        text="Zamknij",
        command=win.destroy,
        bg="white",
        fg=body_fg,
        activebackground="#f3f4f6",
        activeforeground=body_fg,
        relief="solid",
        bd=1,
        padx=18,
        pady=6,
        font=("Segoe UI", 10),
    ).pack(side="right")

    _center_toplevel(win, parent)


def show_changelog(parent):
    path = config.CHANGELOG_FILE
    if not path.exists():
        messagebox.showwarning("Dziennik zmian", f"Nie znaleziono pliku:\n{path}")
        return

    accent = "#d97706"
    header_bg = "#111827"
    panel_bg = "#f9fafb"
    body_bg = "#f3f4f6"
    border = "#d1d5db"
    body_fg = "#1f2937"
    muted_fg = "#6b7280"

    win = tk.Toplevel(parent)
    win.title("Dziennik zmian")
    win.geometry("760x560")
    win.transient(parent)
    win.grab_set()
    win.configure(bg=body_bg)

    outer = tk.Frame(win, bg=body_bg, padx=18, pady=18)
    outer.pack(fill="both", expand=True)

    card = tk.Frame(
        outer,
        bg=panel_bg,
        highlightbackground=border,
        highlightthickness=1,
        bd=0,
    )
    card.pack(fill="both", expand=True)

    header = tk.Frame(card, bg=header_bg, padx=20, pady=18)
    header.pack(fill="x")

    tk.Label(
        header,
        text="Dziennik zmian",
        bg=header_bg,
        fg="white",
        font=("Segoe UI", 16, "bold"),
        anchor="w",
    ).pack(fill="x")
    tk.Label(
        header,
        text="Historia zmian i usprawnień w aplikacji.",
        bg=header_bg,
        fg="#d1d5db",
        font=("Segoe UI", 10),
        anchor="w",
        pady=4,
    ).pack(fill="x")

    content = tk.Frame(card, bg=panel_bg, padx=18, pady=18)
    content.pack(fill="both", expand=True)

    topbar = tk.Frame(content, bg=panel_bg)
    topbar.pack(fill="x", pady=(0, 10))

    tk.Label(
        topbar,
        text="CHANGELOG.md",
        bg=panel_bg,
        fg=accent,
        font=("Segoe UI", 9, "bold"),
        anchor="w",
    ).pack(side="left")
    tk.Label(
        topbar,
        text="Najnowsze wpisy są widoczne poniżej.",
        bg=panel_bg,
        fg=muted_fg,
        font=("Segoe UI", 9),
        anchor="e",
    ).pack(side="right")

    editor_wrap = tk.Frame(
        content,
        bg="#ffffff",
        highlightbackground=border,
        highlightthickness=1,
        bd=0,
    )
    editor_wrap.pack(fill="both", expand=True)

    text = tk.Text(
        editor_wrap,
        wrap="word",
        padx=14,
        pady=14,
        borderwidth=0,
        relief="flat",
        bg="#ffffff",
        fg=body_fg,
        insertbackground=body_fg,
    )
    scroll = ttk.Scrollbar(editor_wrap, orient="vertical", command=text.yview)
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

    text.configure(font=("Segoe UI", 10))

    text.tag_configure("h1", font=h1, foreground=body_fg, spacing1=10, spacing3=8)
    text.tag_configure("h2", font=h2, foreground=body_fg, spacing1=10, spacing3=5)
    text.tag_configure("h3", font=h3, foreground=body_fg, spacing1=6, spacing3=3)
    text.tag_configure("li", lmargin1=20, lmargin2=40)
    text.tag_configure("sep", foreground="#9ca3af", spacing1=6, spacing3=6)
    text.tag_configure("code", font=mono, background="#f3f4f6", foreground=body_fg)
    text.tag_configure("bold", font=h3, foreground=body_fg)

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

    footer = tk.Frame(content, bg=panel_bg)
    footer.pack(fill="x", pady=(12, 0))

    tk.Button(
        footer,
        text="Zamknij",
        command=win.destroy,
        bg="white",
        fg=body_fg,
        activebackground="#f3f4f6",
        activeforeground=body_fg,
        relief="solid",
        bd=1,
        padx=18,
        pady=6,
        font=("Segoe UI", 10),
    ).pack(side="right")

    text.configure(state="disabled")
    _center_toplevel(win, parent)

import tkinter as tk
from tkinter import ttk

from app.dto.branch import Branch
from app.gui.components.tooltip import Tooltip
from app.utils import notifier
from app.utils.validator import validate_number


class CollapsibleRow(ttk.Frame):
    """
    Wiersz oddziału z nagłówkiem i sekcją rozwijaną.
    Klik w nazwę oddziału lub wolne pole w wierszu -> toggle.
    """

    def __init__(self, parent, *,
                 branch: Branch,
                 on_generate,
                 on_create_dir):
        """
        :param parent: widget rodzic
        :param branch: obiekt Branch
        :param on_generate: callback(branch, lot_number:str, additional:bool, rating:bool)
        :param on_create_dir: callback(branch, lot_number:str) -> None
        """
        super().__init__(parent)
        self.branch = branch
        self.on_generate = on_generate
        self.on_create_dir = on_create_dir

        self._expanded = False

        self.additional_var = tk.BooleanVar(value=False)
        self.rating_var = tk.BooleanVar(value=False)

        # UI
        self._build_header()
        self._build_body()
        self._hide_body()

        self.columnconfigure(0, weight=1)

    # ---------- UI ----------
    def _build_header(self):
        self.header = ttk.Frame(self)
        self.header.grid(row=0, column=0, sticky="ew", padx=(5, 5), pady=(4, 0))

        for c in range(8):
            self.header.columnconfigure(c, weight=0)
        self.header.columnconfigure(2, weight=1)

        self.arrow_lbl = ttk.Label(self.header, text="▸", width=2, anchor="w")
        self.arrow_lbl.grid(row=0, column=0, sticky="w")

        name = f"{self.branch.number} {self.branch.name}"
        self.name_lbl = ttk.Label(self.header, text=name, font=('Arial', 11, 'bold'), anchor="w")
        self.name_lbl.grid(row=0, column=1, sticky="w", padx=(2, 6))

        self.spacer = ttk.Frame(self.header)
        self.spacer.grid(row=0, column=2, sticky="ew")

        ttk.Label(self.header, text='Lot nr:').grid(row=0, column=3, padx=(10, 2), sticky='e')
        vcmd = (self.register(validate_number(99)), '%P')
        self.lot_entry = ttk.Entry(self.header, width=5, justify='center', validate='key', validatecommand=vcmd)
        self.lot_entry.grid(row=0, column=4, padx=(0, 10))
        Tooltip(self.lot_entry, "Podaj numer lotu (0–99)")

        self.cb_additional = ttk.Checkbutton(self.header, variable=self.additional_var)
        self.cb_additional.grid(row=0, column=5, padx=3, sticky='w')
        Tooltip(self.cb_additional, "Wygeneruj listy zamknięte")

        self.cb_rating = ttk.Checkbutton(self.header, variable=self.rating_var)
        self.cb_rating.grid(row=0, column=6, padx=3, sticky='w')
        Tooltip(self.cb_rating, "Dołącz listy klasyfikacji")

        self.generate_btn = ttk.Button(self.header, text='Generuj', command=self._on_click_generate)
        self.generate_btn.grid(row=0, column=7, padx=(10, 0), sticky='e')
        Tooltip(self.generate_btn, "Wygeneruj listy PDF dla podanego lotu i wybranego oddziału")

        for w in (self.name_lbl, self.spacer):
            w.bind("<Button-1>", self._toggle)
            w.configure(cursor="hand2")

    def _build_body(self):
        self.body = ttk.Frame(self, padding=(24, 8, 8, 8))
        self.body.columnconfigure(0, weight=1)

        actions = ttk.Frame(self.body)
        actions.grid(row=0, column=0, sticky="w")

        create_btn = ttk.Button(actions, text="Utwórz katalog lotu", command=self._on_click_create_dir)
        create_btn.grid(row=0, column=0, sticky="w")
        Tooltip(create_btn, "Utwórz katalog: LOT_{S|M}_{NN}.001 w katalogu wejściowym oddziału")

    def _on_click_generate(self):
        lot = self.lot_entry.get().strip()
        if not lot.isdigit():
            notifier.show_warning('Podaj poprawny numer lotu!')
            return
        self.on_generate(self.branch, lot, bool(self.additional_var.get()), bool(self.rating_var.get()))

    def _on_click_create_dir(self):
        lot = self.lot_entry.get().strip()
        if not lot.isdigit():
            notifier.show_warning('Wpisz numer lotu')
            return
        self.on_create_dir(self.branch, lot)

    def _toggle(self, _=None):
        if self._expanded:
            self._hide_body()
        else:
            self._show_body()

    def _show_body(self):
        self._expanded = True
        self.arrow_lbl.configure(text="▾")
        self.body.grid(row=1, column=0, sticky="ew")

    def _hide_body(self):
        self._expanded = False
        self.arrow_lbl.configure(text="▸")
        self.body.grid_remove()

import tkinter as tk


class AppMenu:
    def __init__(self, app):
        self.app = app
        self.build_menu()

    def build_menu(self):
        menubar = tk.Menu(self.app.root)
        self.app.root.config(menu=menubar)

        menubar.add_command(label="Start", command=self.app.show_main_scene)
        menubar.add_command(label="Ustawienia", command=self.app.show_settings_scene)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="O programie", command=self.app.show_about)
        helpmenu.add_command(label="Dziennik zmian", command=self.app.show_changelog)
        menubar.add_cascade(label="Pomoc", menu=helpmenu)

        # (opcjonalnie) skrót klawiszowy F1 do "O programie…"
        self.app.root.bind("<F1>", lambda e: self.app.show_about())

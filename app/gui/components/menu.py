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
        menubar.add_command(label="Pomoc", command=self.app.show_about)

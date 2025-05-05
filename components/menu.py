import tkinter as tk

class AppMenu:
    def __init__(self, app):
        self.app = app
        self.build_menu()

    def build_menu(self):
        menubar = tk.Menu(self.app.root)
        self.app.root.config(menu=menubar)

        menu_section = tk.Menu(menubar, tearoff=0)
        menu_section.add_command(label='Start', command=self.app.show_main_scene)
        menu_section.add_command(label='Scieżki', command=self.app.show_paths_scene)
        menubar.add_cascade(label='Menu', menu=menu_section)

        help_section = tk.Menu(menubar, tearoff=0)
        help_section.add_command(label='O programie', command=self.app.show_about)
        menubar.add_cascade(label='Pomoc', menu=help_section)
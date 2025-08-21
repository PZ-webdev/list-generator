import config
import tkinter as tk
import pathlib
from app.gui.branches_scene import BranchesScene
from app.gui.components.menu import AppMenu
from app.gui.dialogs.about import show_about, show_changelog
from app.gui.main_scene import MainScene
from app.gui.settings_scene import SettingsScene
from app.utils import notifier


class PdfApp:
    def __init__(self, root):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.resizable(config.WINDOW_RESIZABLE, config.WINDOW_RESIZABLE)
        self.center_window()

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)

        self.menu = AppMenu(self)
        self.show_main_scene()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"+{x}+{y}")

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_main_scene(self):
        self.clear_main_frame()
        MainScene(self).build()

    def show_branches_scene(self):
        self.clear_main_frame()
        BranchesScene(self).build()

    def show_settings_scene(self):
        self.clear_main_frame()
        SettingsScene(self).build()

    # @staticmethod
    # def show_about():
    #     VERSION = (pathlib.Path(__file__).resolve().parents[2] / 'VERSION').read_text().strip()
    #     notifier.show_success(f'Wersja programu: v{VERSION}', 'Informacja')

    def show_about(self):
        show_about(self.root)

    def show_changelog(self):
        show_changelog(self.root)

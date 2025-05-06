import config
import tkinter as tk
from components.menu import AppMenu
from scenes.main_scene import MainScene
from scenes.paths_scene import PathsScene
from utils import notifier


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

    def show_paths_scene(self):
        self.clear_main_frame()
        PathsScene(self).build()

    def show_about(self):
        notifier.show_success('Generator list PDF\nWersja 0.0.1', 'Informacja')

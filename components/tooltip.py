import tkinter as tk

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = tk.Toplevel(widget)
        self.tooltip.withdraw()
        self.tooltip.wm_overrideredirect(True)
        label = tk.Label(
            self.tooltip,
            text=text,
            background="#fdfd96",
            relief='solid',
            borderwidth=1,
            padx=4,
            pady=2,
            font=("Segoe UI", 9)
        )
        label.pack()
        widget.bind("<Enter>", self.enter)
        widget.bind("<Leave>", self.leave)

    def enter(self, event):
        x = event.x_root + 12
        y = event.y_root + 12
        self.tooltip.geometry(f"+{x}+{y}")
        self.tooltip.deiconify()

    def leave(self, event):
        self.tooltip.withdraw()

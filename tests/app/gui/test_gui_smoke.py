from unittest import SkipTest


def test_tk_smoketest():
    try:
        import tkinter as tk
    except Exception:
        raise SkipTest('Tkinter not available on this environment')

    try:
        root = tk.Tk()
        root.withdraw()
        root.update_idletasks()
        root.destroy()
    except Exception:
        raise SkipTest('Headless environment without display; skipping GUI smoke')

import pytest


def test_tk_smoketest():
    try:
        import tkinter as tk
    except Exception:
        pytest.skip('Tkinter not available on this environment')

    try:
        root = tk.Tk()
        root.withdraw()
        root.update_idletasks()
        root.destroy()
    except Exception:
        pytest.skip('Headless environment without display; skipping GUI smoke')

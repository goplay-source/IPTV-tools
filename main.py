import sys
import os

# ── DPI 适配（仅 Windows）─────────────────────────────────────────────────────
if sys.platform == 'win32':
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

import tkinter as tk
from tkinter import ttk

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

from gui import IPTVApp


def main():
    root = tk.Tk()
    root.title("IPTV直播源测试工具 v2.0 - iptv-search.com")
    root.geometry("1100x750")
    root.minsize(900, 600)
    IPTVApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

# main.py
import tkinter as tk
from gui import MemoryTrackerGUI
import customtkinter as ctk

def main():
    ctk.set_appearance_mode("Red")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = MemoryTrackerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

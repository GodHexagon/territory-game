import tkinter as tk
from tkinter import messagebox

class ErrorDialog:
    def __init__(self, message: str):
        root = tk.Tk()
        root.withdraw()  # メインウィンドウを表示しない
        messagebox.showerror("Territory Game: Error", message)
        root.destroy()

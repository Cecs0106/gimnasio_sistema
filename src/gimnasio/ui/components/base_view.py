import tkinter as tk
from tkinter import ttk


class BaseView(ttk.Frame):
    """Frame base que facilita limpiar y configurar estilos."""

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

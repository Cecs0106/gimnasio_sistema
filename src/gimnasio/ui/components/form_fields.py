import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Tuple


def build_form(parent: ttk.Frame, fields: List[Tuple[str, str, bool]]) -> Dict[str, ttk.Entry]:
    entries: Dict[str, ttk.Entry] = {}
    for label_text, field_name, required in fields:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=6)
        display_text = f"{label_text}{' *' if required else ''}"
        ttk.Label(row, text=display_text, width=22, anchor="e").pack(side=tk.LEFT, padx=(0, 10))
        entry = ttk.Entry(row, width=30)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if required:
            entry.configure(style="Required.TEntry")
        entries[field_name] = entry
    return entries

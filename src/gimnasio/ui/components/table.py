import tkinter as tk
from tkinter import ttk
from typing import Iterable, List, Sequence, Tuple


def build_table(
    parent: ttk.Frame,
    columns: Sequence[Tuple[str, str, int]],
    height: int = 12,
) -> ttk.Treeview:
    tree = ttk.Treeview(parent, columns=[col for col, *_ in columns], show="headings", height=height)
    for column_id, heading, width in columns:
        tree.heading(column_id, text=heading)
        tree.column(column_id, width=width, anchor=tk.CENTER)

    scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    return tree

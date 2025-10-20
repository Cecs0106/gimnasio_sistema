from tkinter import ttk

from gimnasio.config import settings


def configure_styles() -> None:
    style = ttk.Style()
    style.configure(
        "Primary.TButton",
        font=("Arial", 11, "bold"),
        padding=8,
        background=settings.THEME_COLORS["primary"],
        foreground="white",
    )
    style.map(
        "Primary.TButton",
        background=[("active", settings.THEME_COLORS["primary_dark"])],
    )

    style.configure(
        "Success.TButton",
        font=("Arial", 11, "bold"),
        padding=6,
        background=settings.THEME_COLORS["success"],
        foreground="white",
    )
    style.configure(
        "Danger.TButton",
        font=("Arial", 11),
        padding=6,
        background=settings.THEME_COLORS["danger"],
        foreground="white",
    )
    style.configure("Required.TEntry", foreground="black")

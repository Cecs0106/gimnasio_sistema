import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Optional, Type

from gimnasio.config import settings
from gimnasio.ui.components import styles
from gimnasio.ui.views.accesses_view import AccessesView
from gimnasio.ui.views.clients.clients_view import ClientsView
from gimnasio.ui.views.payments.payments_view import PaymentsView
from gimnasio.ui.views.reportes.dashboard_view import DashboardView
from gimnasio.ui.views.settings.settings_view import SettingsView


class MainWindow:
    def __init__(self, root: tk.Tk, dependencies: Dict[str, object]) -> None:
        self.root = root
        self.dependencies = dependencies
        self.current_view: Optional[ttk.Frame] = None
        self._configure_root()
        styles.configure_styles()
        self.show_main_menu()

    def _configure_root(self) -> None:
        self.root.title(settings.APP_TITLE)
        self.root.geometry(settings.WINDOW_SIZE)
        self.root.configure(bg=settings.BACKGROUND_COLOR)

    def clear(self) -> None:
        for widget in self.root.winfo_children():
            widget.destroy()
        self.current_view = None

    def show_main_menu(self) -> None:
        self.clear()
        container = tk.Frame(self.root, bg=settings.BACKGROUND_COLOR, padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            container,
            text="GIMNASIO FITNESS",
            font=("Arial", 20, "bold"),
            bg=settings.BACKGROUND_COLOR,
            fg="#2c3e50",
        ).pack(pady=20)
        tk.Label(
            container,
            text="SISTEMA DE CONTROL",
            font=("Arial", 14),
            bg=settings.BACKGROUND_COLOR,
            fg="#34495e",
        ).pack(pady=10)

        button_frame = tk.Frame(container, bg=settings.BACKGROUND_COLOR)
        button_frame.pack(pady=30)

        buttons: Dict[str, Callable[[], None]] = {
            "🚪 Control de Accesos": lambda: self.open_view(AccessesView),
            "👥 Gestión de Clientes": lambda: self.open_view(ClientsView),
            "💰 Gestión de Pagos": lambda: self.open_view(PaymentsView),
            "📊 Reportes y Estadísticas": lambda: self.open_view(DashboardView),
            "⚙️ Configuración": lambda: self.open_view(SettingsView),
            "🚪 Salir": self.root.quit,
        }

        for text, command in buttons.items():
            btn = tk.Button(
                button_frame,
                text=text,
                font=("Arial", 12),
                bg=settings.THEME_COLORS["primary"],
                fg="white",
                padx=20,
                pady=10,
                width=25,
                command=command,
            )
            btn.pack(pady=8)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=settings.THEME_COLORS["primary_dark"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=settings.THEME_COLORS["primary"]))

    def open_view(self, view_cls: Type[ttk.Frame]) -> None:
        self.clear()
        top_frame = tk.Frame(self.root, bg=settings.BACKGROUND_COLOR)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(
            top_frame, text="← Volver al Menú Principal", command=self.show_main_menu
        ).pack(side=tk.LEFT)

        view_container = tk.Frame(self.root, bg=settings.BACKGROUND_COLOR)
        view_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.current_view = view_cls(view_container, **self.dependencies)

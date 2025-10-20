import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

from gimnasio.services.accesses_service import AccessesService
from gimnasio.utils import formatters


class AccessesView(ttk.Frame):
    def __init__(self, parent, accesses_service: AccessesService, **_extra_kwargs):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        self.accesses_service = accesses_service
        self._build_ui()

    def _build_ui(self) -> None:
        titulo = ttk.Label(self, text="🚪 CONTROL DE ACCESOS AL GIMNASIO", font=("Arial", 16, "bold"))
        titulo.pack(pady=10)

        control_frame = ttk.LabelFrame(self, text="Registro Rápido de Acceso")
        control_frame.pack(fill=tk.X, pady=10)

        ttk.Label(control_frame, text="Cédula del cliente:", font=("Arial", 10)).grid(
            row=0, column=0, sticky=tk.W, pady=10, padx=5
        )

        self.cedula_var = tk.StringVar()
        self.entry_cedula = ttk.Entry(control_frame, textvariable=self.cedula_var, width=20, font=("Arial", 12))
        self.entry_cedula.grid(row=0, column=1, padx=5, pady=10)
        self.entry_cedula.bind("<Return>", self.registrar_entrada)
        self.entry_cedula.focus()

        ttk.Button(
            control_frame,
            text="✅ REGISTRAR ENTRADA",
            command=self.registrar_entrada,
            style="Success.TButton",
        ).grid(row=0, column=2, padx=5, pady=10)

        ttk.Button(
            control_frame,
            text="❌ REGISTRAR SALIDA",
            command=self.registrar_salida,
            style="Danger.TButton",
        ).grid(row=0, column=3, padx=5, pady=10)

        self.info_frame = ttk.LabelFrame(self, text="Información del Cliente")
        self.info_frame.pack(fill=tk.X, pady=10)

        self.info_label = ttk.Label(
            self.info_frame, text="Ingrese una cédula para verificar", font=("Arial", 10), foreground="gray"
        )
        self.info_label.pack(padx=10, pady=10)

        stats_frame = ttk.LabelFrame(self, text="Estadísticas de Hoy")
        stats_frame.pack(fill=tk.X, pady=10)

        self.stats_label = ttk.Label(stats_frame, text="", font=("Arial", 9))
        self.stats_label.pack(padx=10, pady=5)

        accesos_frame = ttk.LabelFrame(self, text="Accesos Recientes (Últimos 20)")
        accesos_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("cedula", "nombre", "tipo", "fecha")
        self.tree = ttk.Treeview(accesos_frame, columns=columns, show="headings", height=15)
        for column_id, heading, width in [
            ("cedula", "Cédula", 100),
            ("nombre", "Nombre Completo", 200),
            ("tipo", "Tipo", 80),
            ("fecha", "Fecha y Hora", 150),
        ]:
            self.tree.heading(column_id, text=heading)
            self.tree.column(column_id, width=width, anchor=tk.CENTER if column_id != "nombre" else tk.W)

        scrollbar = ttk.Scrollbar(accesos_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._refresh_data()

    def registrar_entrada(self, event=None):
        self._registrar("Entrada")

    def registrar_salida(self, event=None):
        self._registrar("Salida")

    def _registrar(self, movimiento: str) -> None:
        cedula = self.cedula_var.get().strip()
        if not cedula:
            messagebox.showwarning("Advertencia", "Por favor ingrese una cédula")
            return

        success, message, cliente = self.accesses_service.registrar(cedula, movimiento)
        if success:
            messagebox.showinfo("Éxito", message)
            self.cedula_var.set("")
            self.entry_cedula.focus()
            if cliente:
                self.info_label.config(
                    text=f"Cliente: {cliente.full_name} | Cédula: {cliente.cedula}",
                    foreground="black",
                )
            else:
                self.info_label.config(text="Ingrese una cédula para verificar", foreground="gray")
        else:
            messagebox.showerror("Error", message)

        self._refresh_data()

    def _refresh_data(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for acceso in self.accesses_service.recientes(20):
            nombre_completo = f"{acceso['nombre']} {acceso['apellido']}"
            fecha_hora = acceso["fecha_hora"]
            try:
                fecha_dt = datetime.fromisoformat(fecha_hora)
            except (ValueError, TypeError):
                fecha_dt = None
            self.tree.insert(
                "",
                0,
                values=(
                    acceso["cedula_cliente"],
                    nombre_completo,
                    acceso["tipo_movimiento"],
                    formatters.format_date(fecha_dt),
                ),
            )

        stats = self.accesses_service.estadisticas()
        texto = (
            f"✅ Entradas hoy: {stats['accesos_hoy']} | "
            f"📅 Entradas esta semana: {stats['accesos_semana']} | "
            f"🕐 Hora pico: {stats['hora_pico']}:00"
        )
        self.stats_label.config(text=texto)

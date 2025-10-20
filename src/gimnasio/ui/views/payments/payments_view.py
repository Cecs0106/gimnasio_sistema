import tkinter as tk
from tkinter import ttk, messagebox

from gimnasio.services.clients_service import ClientsService
from gimnasio.services.payments_service import PaymentsService
from gimnasio.utils import formatters
from gimnasio.utils.validators import ValidationError


class PaymentsView(ttk.Frame):
    def __init__(
        self,
        parent,
        payments_service: PaymentsService,
        clients_service: ClientsService,
        **_extra_kwargs,
    ):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        self.payments_service = payments_service
        self.clients_service = clients_service
        self.cliente_actual = None
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="💰 SISTEMA DE PAGOS", font=("Arial", 16, "bold")).pack(pady=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._build_register_tab()
        self._build_history_tab()
        self._build_overdue_tab()

    def _build_register_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="💳 Registrar Pago")

        buscador = ttk.LabelFrame(tab, text="🔍 Buscar Cliente")
        buscador.pack(fill=tk.X, pady=10)

        ttk.Label(buscador, text="Cédula:").grid(row=0, column=0, padx=5, pady=5)
        self.cedula_var = tk.StringVar()
        self.cedula_entry = ttk.Entry(buscador, textvariable=self.cedula_var, width=20)
        self.cedula_entry.grid(row=0, column=1, padx=5, pady=5)
        self.cedula_entry.bind("<Return>", self._buscar_cliente)
        ttk.Button(buscador, text="Buscar", command=self._buscar_cliente).grid(row=0, column=2, padx=5, pady=5)

        self.info_cliente_label = ttk.Label(tab, text="Ingrese una cédula para buscar", font=("Arial", 10))
        self.info_cliente_label.pack(fill=tk.X, padx=10, pady=10)

        self.membresia_label = ttk.Label(tab, text="No hay información de membresía", font=("Arial", 9))
        self.membresia_label.pack(fill=tk.X, padx=10, pady=(0, 10))

        formulario = ttk.LabelFrame(tab, text="💰 Registrar Nuevo Pago")
        formulario.pack(fill=tk.X, pady=10)

        ttk.Label(formulario, text="Monto ($):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.monto_var = tk.StringVar()
        self.monto_entry = ttk.Entry(formulario, textvariable=self.monto_var, width=15)
        self.monto_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(formulario, text="Duración:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.duracion_var = tk.StringVar(value="1")
        duracion_frame = ttk.Frame(formulario)
        duracion_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        for text, value in [("1 Mes", "1"), ("3 Meses", "3"), ("6 Meses", "6"), ("1 Año", "12")]:
            ttk.Radiobutton(duracion_frame, text=text, variable=self.duracion_var, value=value).pack(
                side=tk.LEFT, padx=5
            )

        ttk.Label(formulario, text="Método de pago:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.metodo_var = tk.StringVar(value="Efectivo")
        ttk.Combobox(
            formulario,
            textvariable=self.metodo_var,
            values=["Efectivo", "Transferencia", "Tarjeta"],
            state="readonly",
            width=18,
        ).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        botones = ttk.Frame(formulario)
        botones.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(botones, text="💾 Registrar Pago", style="Success.TButton", command=self._registrar_pago).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(botones, text="🗑️ Limpiar", command=self._limpiar_formulario).pack(side=tk.LEFT, padx=5)

    def _build_history_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📋 Historial")

        filtros = ttk.Frame(tab)
        filtros.pack(fill=tk.X, pady=10)

        ttk.Label(filtros, text="Cédula:").pack(side=tk.LEFT, padx=5)
        self.hist_cedula_var = tk.StringVar()
        entrada = ttk.Entry(filtros, textvariable=self.hist_cedula_var, width=20)
        entrada.pack(side=tk.LEFT, padx=5)
        entrada.bind("<Return>", self._cargar_historial)
        ttk.Button(filtros, text="Buscar", command=self._cargar_historial).pack(side=tk.LEFT, padx=5)
        ttk.Button(filtros, text="Todos", command=self._cargar_historial_todos).pack(side=tk.LEFT, padx=5)

        contenedor = ttk.Frame(tab)
        contenedor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.hist_tree = ttk.Treeview(
            contenedor,
            columns=("id", "cedula", "cliente", "monto", "duracion", "fecha_pago", "fecha_vencimiento", "metodo", "estado"),
            show="headings",
            height=15,
        )
        for col, heading, width in [
            ("id", "ID", 50),
            ("cedula", "Cédula", 90),
            ("cliente", "Cliente", 150),
            ("monto", "Monto", 90),
            ("duracion", "Duración", 80),
            ("fecha_pago", "Fecha Pago", 110),
            ("fecha_vencimiento", "Vence", 110),
            ("metodo", "Método", 90),
            ("estado", "Estado", 90),
        ]:
            self.hist_tree.heading(col, text=heading)
            self.hist_tree.column(col, width=width)

        scrollbar = ttk.Scrollbar(contenedor, orient=tk.VERTICAL, command=self.hist_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.hist_tree.configure(yscrollcommand=scrollbar.set)
        self.hist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._cargar_historial_todos()

    def _build_overdue_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚠️ Vencidos")

        contenedor = ttk.Frame(tab)
        contenedor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.vencidos_tree = ttk.Treeview(
            contenedor,
            columns=("cedula", "cliente", "telefono", "fecha_vencimiento", "dias_vencido"),
            show="headings",
            height=15,
        )
        for col, heading, width in [
            ("cedula", "Cédula", 100),
            ("cliente", "Cliente", 180),
            ("telefono", "Teléfono", 120),
            ("fecha_vencimiento", "Vencimiento", 120),
            ("dias_vencido", "Días Vencido", 100),
        ]:
            self.vencidos_tree.heading(col, text=heading)
            self.vencidos_tree.column(col, width=width)

        scrollbar = ttk.Scrollbar(contenedor, orient=tk.VERTICAL, command=self.vencidos_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vencidos_tree.configure(yscrollcommand=scrollbar.set)
        self.vencidos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Button(tab, text="🔄 Actualizar", command=self._cargar_vencidos).pack(pady=5)
        self._cargar_vencidos()

    # --- Funcionalidad ---
    def _buscar_cliente(self, _event=None):
        cedula = self.cedula_var.get().strip()
        if not cedula:
            messagebox.showwarning("Advertencia", "Ingrese una cédula")
            return
        cliente = self.clients_service.get(cedula)
        if not cliente:
            messagebox.showerror("Error", "Cliente no encontrado")
            self._limpiar_info()
            return
        self.cliente_actual = cliente
        self.info_cliente_label.config(
            text=f"✅ {cliente.full_name}\n📞 Teléfono: {cliente.telefono or 'No tiene'}\n🆔 Cédula: {cliente.cedula}"
        )
        self._mostrar_membresia(cedula)

    def _mostrar_membresia(self, cedula: str):
        pago = self.payments_service.pago_activo(cedula)
        if not pago:
            self.membresia_label.config(text="❌ No tiene membresía activa", foreground="orange")
            return
        dias_restantes = pago.vence_en()
        if dias_restantes >= 0:
            estado = f"🟢 ACTIVA - Vence en {dias_restantes} días"
            color = "green"
        else:
            estado = f"🔴 VENCIDA - {-dias_restantes} días de retraso"
            color = "red"
        info = (
            f"💰 Último pago: {formatters.format_currency(pago.monto)}\n"
            f"⏰ Vencimiento: {pago.fecha_vencimiento}\n"
            f"📆 Duración: {pago.duracion_meses} mes(es)\n"
            f"💳 Método: {pago.metodo_pago}\n"
            f"{estado}"
        )
        self.membresia_label.config(text=info, foreground=color)

    def _registrar_pago(self):
        if not self.cliente_actual:
            messagebox.showwarning("Advertencia", "Busque un cliente antes de registrar un pago")
            return
        try:
            monto = float(self.monto_var.get())
            duracion = int(self.duracion_var.get())
            metodo = self.metodo_var.get()
            pago = self.payments_service.registrar_pago(self.cliente_actual.cedula, monto, duracion, metodo)
            messagebox.showinfo(
                "Éxito",
                f"Pago registrado correctamente.\n"
                f"Vence el {pago.fecha_vencimiento}\n"
                f"Monto: {formatters.format_currency(pago.monto)}",
            )
            self._mostrar_membresia(self.cliente_actual.cedula)
            self._cargar_historial_todos()
            self._cargar_vencidos()
            self._limpiar_formulario()
        except ValueError:
            messagebox.showerror("Error", "Monto o duración inválidos")
        except ValidationError as exc:
            messagebox.showerror("Error", str(exc))
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo registrar el pago: {exc}")

    def _limpiar_info(self):
        self.cliente_actual = None
        self.info_cliente_label.config(text="Ingrese una cédula para buscar")
        self.membresia_label.config(text="No hay información de membresía", foreground="black")

    def _limpiar_formulario(self):
        self.cedula_var.set("")
        self.monto_var.set("")
        self.duracion_var.set("1")
        self.metodo_var.set("Efectivo")
        self._limpiar_info()
        self.cedula_entry.focus()

    def _cargar_historial(self, _event=None):
        cedula = self.hist_cedula_var.get().strip()
        if not cedula:
            messagebox.showwarning("Advertencia", "Ingrese una cédula")
            return
        self._render_historial(self.payments_service.historial_cliente(cedula))

    def _cargar_historial_todos(self, _event=None):
        self._render_historial(self.payments_service.todos())

    def _render_historial(self, pagos):
        for item in self.hist_tree.get_children():
            self.hist_tree.delete(item)
        for pago in pagos:
            cliente = self.clients_service.get(pago.cedula_cliente)
            self.hist_tree.insert(
                "",
                tk.END,
                values=(
                    pago.id or "-",
                    pago.cedula_cliente,
                    cliente.full_name if cliente else "N/A",
                    formatters.format_currency(pago.monto),
                    f"{pago.duracion_meses} mes(es)",
                    pago.fecha_pago,
                    pago.fecha_vencimiento,
                    pago.metodo_pago,
                    "Activo" if pago.esta_activo else "Vencido",
                ),
            )

    def _cargar_vencidos(self):
        data = self.payments_service.clientes_vencidos()
        for item in self.vencidos_tree.get_children():
            self.vencidos_tree.delete(item)
        for row in data:
            self.vencidos_tree.insert(
                "",
                tk.END,
                values=(
                    row["cedula"],
                    f"{row['nombre']} {row['apellido']}",
                    row["telefono"] or "N/A",
                    row["fecha_vencimiento"],
                    int(row["dias_vencido"]),
                ),
            )

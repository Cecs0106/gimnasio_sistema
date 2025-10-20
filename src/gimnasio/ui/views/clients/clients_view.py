import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, List, Optional

import pandas as pd

from gimnasio.services.clients_service import ClientsService
from gimnasio.services.payments_service import PaymentsService
from gimnasio.utils import formatters
from gimnasio.utils.validators import ValidationError
from gimnasio.ui.components.form_fields import build_form
from gimnasio.ui.components.table import build_table


class ClientsView(ttk.Frame):
    def __init__(
        self,
        parent,
        clients_service: ClientsService,
        payments_service: PaymentsService,
        **_extra_kwargs,
    ):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        self.clients_service = clients_service
        self.payments_service = payments_service
        self._build_ui()

    def _build_ui(self):
        title = ttk.Label(self, text="👥 GESTIÓN DE CLIENTES", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._build_register_tab()
        self._build_list_tab()

    # --- Registro ---
    def _build_register_tab(self):
        self.register_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.register_tab, text="➕ Registrar Cliente")

        form_frame = ttk.Frame(self.register_tab)
        form_frame.pack(pady=20, padx=30, fill=tk.BOTH, expand=True)

        campos = [
            ("Cédula", "cedula", True),
            ("Nombre", "nombre", True),
            ("Apellido", "apellido", True),
            ("Teléfono", "telefono", False),
            ("Teléfono emergencia", "telefono_emergencia", False),
            ("Dirección", "direccion", False),
            ("Email", "email", False),
        ]
        self.form_entries = build_form(form_frame, campos)

        buttons_frame = ttk.Frame(self.register_tab)
        buttons_frame.pack(pady=10)

        ttk.Button(
            buttons_frame, text="💾 Guardar", style="Success.TButton", command=self._on_save_client
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🗑️ Limpiar", command=self._clear_form).pack(side=tk.LEFT, padx=5)

    def _get_form_data(self) -> Dict[str, str]:
        return {field: entry.get().strip() for field, entry in self.form_entries.items()}

    def _clear_form(self):
        for entry in self.form_entries.values():
            entry.delete(0, tk.END)

    def _on_save_client(self):
        data = self._get_form_data()
        try:
            self.clients_service.register(data)
            messagebox.showinfo("Éxito", "Cliente registrado correctamente.")
            self._clear_form()
            self._refresh_list()
        except ValidationError as exc:
            messagebox.showerror("Error", str(exc))
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo guardar el cliente: {exc}")

    # --- Lista ---
    def _build_list_tab(self):
        self.list_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.list_tab, text="📋 Lista de Clientes")

        filters_frame = ttk.LabelFrame(self.list_tab, text="Filtros de búsqueda")
        filters_frame.pack(fill=tk.X, padx=10, pady=10)

        self.search_entries: Dict[str, ttk.Entry] = {}
        for index, (label, field) in enumerate(
            [
                ("Cédula", "cedula"),
                ("Nombre", "nombre"),
                ("Apellido", "apellido"),
                ("Teléfono", "telefono"),
            ]
        ):
            row = ttk.Frame(filters_frame)
            row.grid(row=index // 2, column=(index % 2), padx=5, pady=5, sticky="w")
            ttk.Label(row, text=f"{label}:").pack(side=tk.LEFT, padx=(0, 5))
            entry = ttk.Entry(row, width=20)
            entry.pack(side=tk.LEFT)
            entry.bind("<Return>", lambda *_: self._refresh_list())
            self.search_entries[field] = entry

        estado_frame = ttk.Frame(filters_frame)
        estado_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Label(estado_frame, text="Estado:").pack(side=tk.LEFT, padx=(0, 10))
        self.estado_var = tk.StringVar(value="Todos")
        for text in ["Todos", "Activos", "Vencidos"]:
            ttk.Radiobutton(
                estado_frame,
                text=text,
                variable=self.estado_var,
                value=text,
                command=self._refresh_list,
            ).pack(side=tk.LEFT, padx=5)

        action_frame = ttk.Frame(filters_frame)
        action_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(action_frame, text="🔍 Buscar", command=self._refresh_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🗑️ Limpiar", command=self._clear_filters).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📁 Importar Excel", command=self._bulk_import).pack(side=tk.LEFT, padx=5)

        table_frame = ttk.Frame(self.list_tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree = build_table(
            table_frame,
            [
                ("cedula", "Cédula", 100),
                ("nombre", "Nombre", 150),
                ("apellido", "Apellido", 150),
                ("telefono", "Teléfono", 120),
                ("estado", "Estado", 80),
                ("vence", "Vence", 100),
            ],
            height=12,
        )

        self.tree.bind("<<TreeviewSelect>>", self._on_select_client)

        footer = ttk.Frame(self.list_tab)
        footer.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.summary_label = ttk.Label(footer, text="")
        self.summary_label.pack(side=tk.LEFT)

        btns = ttk.Frame(footer)
        btns.pack(side=tk.RIGHT)

        ttk.Button(btns, text="💰 Ver Pagos", command=self._show_payments).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="🗑️ Eliminar", style="Danger.TButton", command=self._delete_client).pack(
            side=tk.LEFT, padx=5
        )

        self._refresh_list()

    def _collect_filters(self) -> Dict[str, str]:
        return {field: entry.get().strip() for field, entry in self.search_entries.items() if entry.get().strip()}

    def _refresh_list(self, _event=None):
        filtros = self._collect_filters()
        resultados = list(self.clients_service.search(filtros, self.estado_var.get()))

        for item in self.tree.get_children():
            self.tree.delete(item)

        for resultado in resultados:
            cliente = resultado["cliente"]
            estado_pago = resultado["estado_pago"]
            fecha_vencimiento = resultado["fecha_vencimiento"]
            self.tree.insert(
                "",
                tk.END,
                iid=cliente.cedula,
                values=(
                    cliente.cedula,
                    cliente.nombre,
                    cliente.apellido,
                    cliente.telefono or "N/A",
                    estado_pago,
                    fecha_vencimiento or "N/A",
                ),
            )
        self.summary_label.config(text=f"Total mostrados: {len(resultados)}")

    def _clear_filters(self):
        for entry in self.search_entries.values():
            entry.delete(0, tk.END)
        self.estado_var.set("Todos")
        self._refresh_list()

    def _bulk_import(self):
        path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel", filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if not path:
            return
        try:
            df = pd.read_excel(path)
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo leer el archivo: {exc}")
            return

        required = {"cedula", "nombre", "apellido"}
        if not required.issubset(set(df.columns)):
            messagebox.showerror("Error", f"El archivo debe contener las columnas: {', '.join(sorted(required))}")
            return

        registrados = 0
        duplicados: List[str] = []
        errores = 0
        for _, row in df.iterrows():
            data = {key: str(row.get(key, "")).strip() for key in df.columns}
            try:
                self.clients_service.register(data)
                registrados += 1
            except ValidationError as exc:
                duplicados.append(data.get("cedula", ""))
                errores += 1
            except Exception:
                errores += 1

        mensaje = f"✅ Registrados: {registrados}\n"
        mensaje += f"❌ Errores/Duplicados: {errores}"
        if duplicados:
            mensaje += f"\nCédulas repetidas: {', '.join([d for d in duplicados if d][:5])}"
        messagebox.showinfo("Resultado de importación", mensaje)
        self._refresh_list()

    def _get_selected_cedula(self) -> Optional[str]:
        selection = self.tree.selection()
        if not selection:
            return None
        return selection[0]

    def _on_select_client(self, _event=None):
        pass

    def _show_payments(self):
        cedula = self._get_selected_cedula()
        if not cedula:
            messagebox.showwarning("Advertencia", "Seleccione un cliente")
            return
        pagos = self.payments_service.historial_cliente(cedula)
        if not pagos:
            messagebox.showinfo("Pagos", "El cliente no posee pagos registrados.")
            return
        lineas = []
        for pago in pagos[:10]:
            lineas.append(
                f"{pago.fecha_pago} - {formatters.format_currency(pago.monto)} - "
                f"Vence: {pago.fecha_vencimiento} ({'Activo' if pago.esta_activo else 'Vencido'})"
            )
        messagebox.showinfo("Pagos", "\n".join(lineas))

    def _delete_client(self):
        cedula = self._get_selected_cedula()
        if not cedula:
            messagebox.showwarning("Advertencia", "Seleccione un cliente")
            return

        confirm = messagebox.askyesno("Eliminar", f"¿Eliminar al cliente {cedula}?")
        if not confirm:
            return

        eliminado = self.clients_service.delete(cedula)
        if eliminado:
            messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
            self._refresh_list()
        else:
            messagebox.showerror("Error", "No se pudo eliminar el cliente.")

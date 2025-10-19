import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sqlite3

class PagosUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.cliente_actual = None
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        titulo = ttk.Label(main_frame, text="💰 SISTEMA DE PAGOS", 
                          font=('Arial', 16, 'bold'))
        titulo.pack(pady=10)
        
        # Crear pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Pestaña 1: Registrar Pago
        self.tab_registrar = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_registrar, text="💳 Registrar Pago")
        
        # Pestaña 2: Historial de Pagos
        self.tab_historial = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_historial, text="📋 Historial")
        
        # Pestaña 3: Clientes Vencidos
        self.tab_vencidos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_vencidos, text="⚠️ Vencidos")
        
        self.setup_tab_registrar()
        self.setup_tab_historial()
        self.setup_tab_vencidos()
        
        # Cargar datos iniciales
        self.cargar_clientes_vencidos()
    
    def setup_tab_registrar(self):
        """Configura la pestaña de registro de pagos"""
        # Frame principal de la pestaña
        main_frame = ttk.Frame(self.tab_registrar)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sección de búsqueda de cliente
        busqueda_frame = ttk.LabelFrame(main_frame, text="🔍 Buscar Cliente")
        busqueda_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(busqueda_frame, text="Cédula:").grid(row=0, column=0, padx=5, pady=5)
        self.cedula_var = tk.StringVar()
        self.cedula_entry = ttk.Entry(busqueda_frame, textvariable=self.cedula_var, width=20)
        self.cedula_entry.grid(row=0, column=1, padx=5, pady=5)
        self.cedula_entry.bind('<Return>', self.buscar_cliente)
        
        ttk.Button(busqueda_frame, text="Buscar", 
                  command=self.buscar_cliente).grid(row=0, column=2, padx=5, pady=5)
        
        # Información del cliente
        self.info_cliente_frame = ttk.LabelFrame(main_frame, text="👤 Información del Cliente")
        self.info_cliente_frame.pack(fill=tk.X, pady=10)
        
        self.info_cliente_label = ttk.Label(self.info_cliente_frame, 
                                           text="Ingrese una cédula para buscar", 
                                           font=('Arial', 10))
        self.info_cliente_label.pack(padx=10, pady=10)
        
        # Información de membresía actual
        self.membresia_frame = ttk.LabelFrame(main_frame, text="💳 Membresía Actual")
        self.membresia_frame.pack(fill=tk.X, pady=10)
        
        self.membresia_label = ttk.Label(self.membresia_frame, 
                                        text="No hay información de membresía", 
                                        font=('Arial', 9))
        self.membresia_label.pack(padx=10, pady=10)
        
        # Formulario de pago
        pago_frame = ttk.LabelFrame(main_frame, text="💰 Registrar Nuevo Pago")
        pago_frame.pack(fill=tk.X, pady=10)
        
        # Monto
        ttk.Label(pago_frame, text="Monto ($):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.monto_var = tk.StringVar()
        self.monto_entry = ttk.Entry(pago_frame, textvariable=self.monto_var, width=15)
        self.monto_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Duración
        ttk.Label(pago_frame, text="Duración:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.duracion_var = tk.StringVar(value="1")
        duracion_frame = ttk.Frame(pago_frame)
        duracion_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        duraciones = [("1 Mes", "1"), ("3 Meses", "3"), ("6 Meses", "6"), ("1 Año", "12")]
        for text, value in duraciones:
            ttk.Radiobutton(duracion_frame, text=text, variable=self.duracion_var, 
                           value=value).pack(side=tk.LEFT, padx=5)
        
        # Método de pago
        ttk.Label(pago_frame, text="Método:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.metodo_var = tk.StringVar(value="Efectivo")
        metodo_combo = ttk.Combobox(pago_frame, textvariable=self.metodo_var,
                                   values=["Efectivo", "Tarjeta", "Transferencia", "Depósito"],
                                   state="readonly", width=15)
        metodo_combo.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Botón de registro
        btn_frame = ttk.Frame(pago_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="💾 Registrar Pago", 
                  command=self.registrar_pago).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="🧹 Limpiar", 
                  command=self.limpiar_formulario).pack(side=tk.LEFT, padx=5)
    
    def setup_tab_historial(self):
        """Configura la pestaña de historial de pagos"""
        main_frame = ttk.Frame(self.tab_historial)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Búsqueda por cédula
        busqueda_frame = ttk.Frame(main_frame)
        busqueda_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(busqueda_frame, text="Cédula:").pack(side=tk.LEFT, padx=5)
        self.hist_cedula_var = tk.StringVar()
        hist_cedula_entry = ttk.Entry(busqueda_frame, textvariable=self.hist_cedula_var, width=20)
        hist_cedula_entry.pack(side=tk.LEFT, padx=5)
        hist_cedula_entry.bind('<Return>', self.cargar_historial)
        
        ttk.Button(busqueda_frame, text="Buscar Historial", 
                  command=self.cargar_historial).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(busqueda_frame, text="Todos los Pagos", 
                  command=self.cargar_todos_pagos).pack(side=tk.LEFT, padx=5)
        
        # Treeview para historial
        tree_frame = ttk.LabelFrame(main_frame, text="📜 Historial de Pagos")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ('id', 'cedula', 'cliente', 'monto', 'duracion', 'fecha_pago', 'fecha_vencimiento', 'metodo', 'estado')
        self.historial_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        column_config = [
            ('id', 'ID', 50),
            ('cedula', 'Cédula', 100),
            ('cliente', 'Cliente', 150),
            ('monto', 'Monto', 80),
            ('duracion', 'Duración', 80),
            ('fecha_pago', 'Fecha Pago', 100),
            ('fecha_vencimiento', 'Vence', 100),
            ('metodo', 'Método', 100),
            ('estado', 'Estado', 80)
        ]
        
        for col, heading, width in column_config:
            self.historial_tree.heading(col, text=heading)
            self.historial_tree.column(col, width=width)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.historial_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.historial_tree.configure(yscrollcommand=scrollbar.set)
        self.historial_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Cargar todos los pagos inicialmente
        self.cargar_todos_pagos()
    
    def setup_tab_vencidos(self):
        """Configura la pestaña de clientes vencidos"""
        main_frame = ttk.Frame(self.tab_vencidos)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botones de acción
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="🔄 Actualizar", 
                  command=self.cargar_clientes_vencidos).pack(side=tk.LEFT, padx=5)
        
        self.contador_vencidos = ttk.Label(btn_frame, text="", font=('Arial', 10, 'bold'))
        self.contador_vencidos.pack(side=tk.RIGHT, padx=5)
        
        # Treeview para clientes vencidos
        tree_frame = ttk.LabelFrame(main_frame, text="⚠️ Clientes con Membresía Vencida")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ('cedula', 'cliente', 'telefono', 'fecha_vencimiento', 'dias_vencido')
        self.vencidos_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        column_config = [
            ('cedula', 'Cédula', 100),
            ('cliente', 'Cliente', 200),
            ('telefono', 'Teléfono', 100),
            ('fecha_vencimiento', 'Vencimiento', 120),
            ('dias_vencido', 'Días Vencido', 100)
        ]
        
        for col, heading, width in column_config:
            self.vencidos_tree.heading(col, text=heading)
            self.vencidos_tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.vencidos_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vencidos_tree.configure(yscrollcommand=scrollbar.set)
        self.vencidos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind para selección
        self.vencidos_tree.bind('<<TreeviewSelect>>', self.on_vencido_select)
    
    def buscar_cliente(self, event=None):
        """Busca un cliente por cédula"""
        cedula = self.cedula_var.get().strip()
        if not cedula:
            messagebox.showwarning("Advertencia", "Ingrese una cédula")
            return
        
        try:
            cliente = self.db.get_cliente_by_cedula(cedula)
            if cliente:
                self.cliente_actual = cliente
                self.mostrar_info_cliente(cliente)
                self.mostrar_membresia_actual(cedula)
            else:
                messagebox.showerror("Error", f"Cliente con cédula {cedula} no encontrado")
                self.limpiar_info_cliente()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo buscar el cliente: {e}")
    
    def mostrar_info_cliente(self, cliente):
        """Muestra la información del cliente"""
        nombre_completo = f"{cliente[1]} {cliente[2]}"
        telefono = cliente[3] or "No tiene"
        self.info_cliente_label.config(
            text=f"✅ {nombre_completo}\n📞 Teléfono: {telefono}\n🆔 Cédula: {cliente[0]}"
        )
    
    def mostrar_membresia_actual(self, cedula):
        """Muestra la información de membresía actual"""
        try:
            pago_activo = self.db.get_pago_activo(cedula)
            if pago_activo:
                fecha_vencimiento = pago_activo[5]
                hoy = datetime.now().date()
                vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date()
                
                if vencimiento >= hoy:
                    dias_restantes = (vencimiento - hoy).days
                    estado = f"🟢 ACTIVA - Vence en {dias_restantes} días"
                    color = 'green'
                else:
                    dias_vencido = (hoy - vencimiento).days
                    estado = f"🔴 VENCIDA - {dias_vencido} días de retraso"
                    color = 'red'
                
                info = f"""💰 Último pago: ${pago_activo[2]:.2f}
⏰ Vencimiento: {fecha_vencimiento}
📆 Duración: {pago_activo[3]} mes(es)
💳 Método: {pago_activo[6]}
{estado}"""
            else:
                info = "❌ No tiene membresía activa"
                color = 'orange'
            
            self.membresia_label.config(text=info, foreground=color)
            
        except Exception as e:
            print(f"Error mostrando membresía: {e}")
    
    def limpiar_info_cliente(self):
        """Limpia la información del cliente"""
        self.cliente_actual = None
        self.info_cliente_label.config(text="Ingrese una cédula para buscar")
        self.membresia_label.config(text="No hay información de membresía", foreground='black')
        self.monto_var.set("")
        self.duracion_var.set("1")
        self.metodo_var.set("Efectivo")
    
    def registrar_pago(self):
        """Registra un nuevo pago"""
        if not self.cliente_actual:
            messagebox.showwarning("Advertencia", "Primero busque un cliente")
            return
        
        try:
            monto = float(self.monto_var.get().strip())
            duracion = int(self.duracion_var.get())
            metodo = self.metodo_var.get()
            cedula = self.cliente_actual[0]
            
            if monto <= 0:
                messagebox.showwarning("Advertencia", "El monto debe ser mayor a 0")
                return
            
            # Confirmar registro
            nombre_cliente = f"{self.cliente_actual[1]} {self.cliente_actual[2]}"
            confirmacion = messagebox.askyesno(
                "Confirmar Pago",
                f"¿Registrar pago para {nombre_cliente}?\n\n"
                f"Monto: ${monto:.2f}\n"
                f"Duración: {duracion} mes(es)\n"
                f"Método: {metodo}"
            )
            
            if confirmacion:
                if self.db.insert_pago(cedula, monto, duracion, metodo):
                    messagebox.showinfo("Éxito", "Pago registrado correctamente")
                    self.limpiar_formulario()
                    self.mostrar_membresia_actual(cedula)
                    # Actualizar pestaña de vencidos
                    self.cargar_clientes_vencidos()
                else:
                    messagebox.showerror("Error", "No se pudo registrar el pago")
        
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido")
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar pago: {e}")
    
    def limpiar_formulario(self):
        """Limpia el formulario de pago"""
        self.cedula_var.set("")
        self.monto_var.set("")
        self.duracion_var.set("1")
        self.metodo_var.set("Efectivo")
        self.limpiar_info_cliente()
        self.cedula_entry.focus()
    
    def cargar_historial(self, event=None):
        """Carga el historial de pagos de un cliente específico"""
        cedula = self.hist_cedula_var.get().strip()
        if not cedula:
            messagebox.showwarning("Advertencia", "Ingrese una cédula")
            return
        
        try:
            # Limpiar treeview
            for item in self.historial_tree.get_children():
                self.historial_tree.delete(item)
            
            # Obtener pagos del cliente
            pagos = self.db.get_pagos_by_cliente(cedula)
            
            if not pagos:
                messagebox.showinfo("Info", "No se encontraron pagos para esta cédula")
                return
            
            # Obtener información del cliente
            cliente = self.db.get_cliente_by_cedula(cedula)
            nombre_cliente = f"{cliente[1]} {cliente[2]}" if cliente else "N/A"
            
            # Agregar pagos al treeview
            for pago in pagos:
                estado = "ACTIVO" if pago[7] == 1 else "INACTIVO"
                self.historial_tree.insert('', 'end', values=(
                    pago[0], cedula, nombre_cliente, f"${pago[2]:.2f}", 
                    f"{pago[3]} mes(es)", pago[4], pago[5], pago[6], estado
                ))
            
            messagebox.showinfo("Éxito", f"Se encontraron {len(pagos)} pagos")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial: {e}")
    
    def cargar_todos_pagos(self):
        """Carga todos los pagos del sistema"""
        try:
            # Limpiar treeview
            for item in self.historial_tree.get_children():
                self.historial_tree.delete(item)
            
            # Obtener todos los clientes y sus pagos
            clientes = self.db.get_all_clientes()
            total_pagos = 0
            
            for cliente in clientes:
                cedula = cliente[0]
                pagos = self.db.get_pagos_by_cliente(cedula)
                nombre_cliente = f"{cliente[1]} {cliente[2]}"
                
                for pago in pagos:
                    estado = "ACTIVO" if pago[7] == 1 else "INACTIVO"
                    self.historial_tree.insert('', 'end', values=(
                        pago[0], cedula, nombre_cliente, f"${pago[2]:.2f}", 
                        f"{pago[3]} mes(es)", pago[4], pago[5], pago[6], estado
                    ))
                    total_pagos += 1
            
            self.hist_cedula_var.set("")  # Limpiar búsqueda
            print(f"✅ Cargados {total_pagos} pagos en total")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los pagos: {e}")
    
    def cargar_clientes_vencidos(self):
        """Carga la lista de clientes vencidos"""
        try:
            # Limpiar treeview
            for item in self.vencidos_tree.get_children():
                self.vencidos_tree.delete(item)
            
            # Obtener clientes vencidos
            clientes_vencidos = self.db.get_clientes_vencidos()
            
            if not clientes_vencidos:
                self.contador_vencidos.config(text="✅ No hay clientes vencidos", foreground='green')
                return
            
            hoy = datetime.now().date()
            
            for cliente in clientes_vencidos:
                cedula = cliente[0]
                nombre_cliente = f"{cliente[1]} {cliente[2]}"
                telefono = cliente[3] or "N/A"
                fecha_vencimiento = cliente[4]
                
                # Calcular días vencidos
                vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date()
                dias_vencido = (hoy - vencimiento).days
                
                self.vencidos_tree.insert('', 'end', values=(
                    cedula, nombre_cliente, telefono, fecha_vencimiento, dias_vencido
                ))
            
            self.contador_vencidos.config(
                text=f"⚠️ {len(clientes_vencidos)} clientes vencidos", 
                foreground='red'
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar clientes vencidos: {e}")
    
    def on_vencido_select(self, event):
        """Cuando se selecciona un cliente vencido"""
        selection = self.vencidos_tree.selection()
        if selection:
            item = selection[0]
            cedula = self.vencidos_tree.item(item, 'values')[0]
            # Cambiar a pestaña de registro y buscar el cliente
            self.notebook.select(0)  # Ir a pestaña de registro
            self.cedula_var.set(cedula)
            self.buscar_cliente()
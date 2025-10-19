import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
from database import Database
from accesos_ui import AccesosUI
from clientes_ui import ClientesUI
from pagos_ui import PagosUI
from reportes_ui import ReportesUI
from configuracion_ui import ConfiguracionUI

class GimnasioApp:
    def __init__(self, root):
        self.root = root
        self.db = Database()
        self.configure_ventana()
        # self.main_frame ya no se crea aquí, se crea en cada vista
        self.crear_interfaz()

    def configure_ventana(self):
        self.root.title("Sistema de Gimnasio")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')

    def crear_interfaz(self):
        self.create_main_menu()

    def clear_window(self):
        """Limpia todos los widgets del frame principal para dibujar una nueva vista."""
        # Esta implementación destruye todo y lo reconstruye.
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_main_menu(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="GIMNASIO FITNESS", font=("Arial", 20, "bold"), bg='#f0f0f0', fg='#2c3e50').pack(pady=20)
        tk.Label(main_frame, text="SISTEMA DE CONTROL", font=("Arial", 14), bg='#f0f0f0', fg='#34495e').pack(pady=10)

        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=30)

        # --- BOTONES CORREGIDOS para llamar a las implementaciones correctas ---
        buttons = [
            ("🚪 Control de Accesos", self.show_accesos),
            ("👥 Gestión de Clientes", self.show_clientes),  # ← DEBE SER self.show_clientes
            ("💰 Gestión de Pagos", self.show_pagos),
            ("📊 Reportes y Estadísticas", self.show_reportes),
            ("⚙️ Configuración", self.show_configuracion),
            ("🚪 Salir", self.root.quit)
        ]

        for text, command in buttons:
            btn = tk.Button(button_frame, text=text, font=("Arial", 12), 
                            bg='#3498db', fg='white', padx=20, pady=10,
                            command=command, width=25)
            btn.pack(pady=8)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg='#2980b9'))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg='#3498db'))

    # --- MÉTODOS DEL NUEVO MENÚ ---

    def show_accesos(self):
        """Muestra la interfaz de control de accesos (Nueva Versión)"""
        self.clear_window()
        
        # Frame para botón de volver
        top_frame = tk.Frame(self.root, bg='#f0f0f0')
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(top_frame, text="← Volver al Menú Principal", 
                  font=("Arial", 10),
                  command=self.create_main_menu).pack(side=tk.LEFT)
        
        # Inicializar la interfaz de accesos (requiere accesos_ui.py)
        try:
            self.accesos_ui = AccesosUI(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de accesos: {e}")
            self.create_main_menu()

    def show_clientes(self):
        """Muestra la interfaz de gestión de clientes - VERSIÓN CORREGIDA"""
        print("🎯 Iniciando show_clientes...")
        
        # Limpiar ventana completamente
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal MUY SIMPLE
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Solo botón de volver arriba
        top_frame = tk.Frame(main_frame, bg='#f0f0f0')
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(top_frame, text="← Volver al Menú Principal", 
                font=("Arial", 10),
                command=self.create_main_menu).pack(side=tk.LEFT)
        
        # Frame contenedor para ClientesUI
        clientes_container = tk.Frame(main_frame)
        clientes_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Inicializar la interfaz de clientes
        try:
            print("🔧 Cargando ClientesUI...")
            self.clientes_ui = ClientesUI(clientes_container, self.db)
            print("✅ ClientesUI cargada exitosamente")
        except Exception as e:
            print(f"❌ Error cargando ClientesUI: {e}")
            # Mostrar error simple
            error_label = tk.Label(clientes_container, 
                                text=f"Error cargando interfaz: {e}", 
                                fg='red', font=("Arial", 12))
            error_label.pack(pady=50)

    def show_pagos(self):
        """Muestra la interfaz de gestión de pagos"""
        self.clear_window()
        
        # Frame para botón de volver
        top_frame = tk.Frame(self.root, bg='#f0f0f0')
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(top_frame, text="← Volver al Menú Principal", 
                font=("Arial", 10),
                command=self.create_main_menu).pack(side=tk.LEFT)
    
        # Inicializar la interfaz de pagos
        try:
            self.pagos_ui = PagosUI(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de pagos: {e}")
            self.create_main_menu()

    def show_reportes(self):
        """Muestra la interfaz de reportes y dashboard"""
        self.clear_window()
        
        # Frame para botón de volver
        top_frame = tk.Frame(self.root, bg='#f0f0f0')
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(top_frame, text="← Volver al Menú Principal", 
                font=("Arial", 10),
                command=self.create_main_menu).pack(side=tk.LEFT)
        
        # Inicializar la interfaz de reportes
        try:
            self.reportes_ui = ReportesUI(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de reportes: {e}")
            self.create_main_menu()

    def show_configuracion(self):
        """Muestra la interfaz de configuración"""
        self.clear_window()
        
        # Frame para botón de volver
        top_frame = tk.Frame(self.root, bg='#f0f0f0')
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(top_frame, text="← Volver al Menú Principal", 
                font=("Arial", 10),
                command=self.create_main_menu).pack(side=tk.LEFT)
        
        # Inicializar la interfaz de configuración
        try:
            self.configuracion_ui = ConfiguracionUI(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de configuración: {e}")
            self.create_main_menu()

    # --- MÉTODOS DE GESTIÓN (Implementaciones Antiguas) ---

    def gestion_clientes(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="Gestión de Clientes", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#2c3e50').pack(pady=20)

        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)

        buttons = [
            ("➕ Registrar Cliente", self.registrar_cliente_individual),
            ("📊 Carga Masiva (Excel)", self.carga_masiva_excel),
            ("📋 Lista General", self.lista_clientes),
            ("🔍 Búsqueda Avanzada", self.buscar_cliente)
        ]
        
        for text, command in buttons:
            tk.Button(button_frame, text=text, command=command, font=("Arial", 11), bg='#27ae60', fg='white', width=30, height=2, relief='flat').pack(pady=8)

        tk.Button(main_frame, text="← Volver al Menú Principal", command=self.create_main_menu, font=("Arial", 10), bg='#e74c3c', fg='white', relief='flat').pack(pady=20)

    def registrar_cliente_individual(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="Registro Individual - Cliente", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#2c3e50').pack(pady=20)

        form_frame = tk.Frame(main_frame, bg='#f0f0f0')
        form_frame.pack(pady=20)

        campos = [
            ("Cédula:", "cedula"), ("Nombre:", "nombre"),
            ("Apellido:", "apellido"), ("Teléfono:", "telefono"),
            ("Tel. Emergencia:", "telefono_emergencia"), ("Dirección:", "direccion")
        ]
        
        self.entries = {}
        for i, (label_text, field_name) in enumerate(campos):
            row, col = i // 2, (i % 2) * 2
            tk.Label(form_frame, text=label_text, font=("Arial", 10), bg='#f0f0f0').grid(row=row, column=col, padx=5, pady=8, sticky='e')
            entry = tk.Entry(form_frame, font=("Arial", 10), width=30)
            entry.grid(row=row, column=col + 1, padx=5, pady=8, sticky='w')
            self.entries[field_name] = entry

        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="💾 Guardar Cliente", command=self.guardar_cliente, font=("Arial", 11, "bold"), bg='#27ae60', fg='white', width=15, relief='flat').grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="❌ Cancelar", command=self.show_clientes, font=("Arial", 11), bg='#e74c3c', fg='white', width=15, relief='flat').grid(row=0, column=1, padx=10)

    def guardar_cliente(self):
        try:
            datos = {field: entry.get().strip() for field, entry in self.entries.items()}
            if not datos['cedula'] or not datos['nombre'] or not datos['apellido']:
                messagebox.showerror("Error", "Cédula, Nombre y Apellido son obligatorios.")
                return
            
            # Asumiendo que db.insert_cliente existe
            if self.db.insert_cliente(datos['cedula'], datos['nombre'], datos['apellido'], datos['telefono'], datos['telefono_emergencia'], datos['direccion'], ""):
                messagebox.showinfo("Éxito", "Cliente registrado correctamente.")
                self.show_clientes()
            else:
                messagebox.showerror("Error", "La cédula ya existe en el sistema.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar cliente: {str(e)}")

    def carga_masiva_excel(self):
        file_path = filedialog.askopenfilename(title="Seleccionar archivo Excel", filetypes=[("Excel files", "*.xlsx *.xls")])
        if not file_path:
            return
        
        try:
            df = pd.read_excel(file_path)
            required = ['cedula', 'nombre', 'apellido']
            if not all(col in df.columns for col in required):
                messagebox.showerror("Error", f"El archivo Excel debe contener las columnas: {', '.join(required)}.")
                return

            if not messagebox.askyesno("Confirmar Carga", f"Se encontraron {len(df)} registros.\n¿Deseas proceder con la carga masiva?"):
                return
            
            registrados, errores, repetidos = 0, 0, []
            for _, row in df.iterrows():
                try:
                    cedula = str(row['cedula']).strip()
                    if not cedula or not str(row['nombre']).strip() or not str(row['apellido']).strip():
                        errores += 1
                        continue
                    
                    # Asumiendo que db.insert_cliente existe
                    if self.db.insert_cliente(cedula, str(row['nombre']).strip(), str(row['apellido']).strip(), str(row.get('telefono', '')).strip(), str(row.get('telefono_emergencia', '')).strip(), str(row.get('direccion', '')).strip(), ""):
                        registrados += 1
                    else:
                        errores += 1
                        repetidos.append(cedula)
                except Exception:
                    errores += 1
            
            msg = f"✅ Registrados: {registrados}\n❌ Errores/Duplicados: {errores}"
            if repetidos:
                msg += f"\n\nCédulas duplicadas:\n{', '.join(repetidos[:5])}{'...' if len(repetidos) > 5 else ''}"
            messagebox.showinfo("Resultado de Carga", msg)
            # self.update_stats() # Este método fue eliminado, ya no es necesario
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar el archivo Excel.\n{str(e)}")

    def lista_clientes(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(main_frame, text="Lista General de Clientes", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#2c3e50').pack(pady=20)
        
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        try:
            # Asumiendo que db.get_all_clientes() existe
            clientes = self.db.get_all_clientes() 
            if not clientes:
                tk.Label(tree_frame, text="No hay clientes registrados.", font=("Arial", 12), bg='#f0f0f0').pack(pady=50)
            else:
                columns = ('Cédula', 'Nombre', 'Apellido', 'Teléfono')
                tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=150, anchor='center')
                
                for cliente in clientes:
                    tree.insert('', tk.END, values=(cliente[0], cliente[1], cliente[2], cliente[3]))
                
                scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscroll=scrollbar.set)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        except Exception as e:
            tk.Label(tree_frame, text=f"Error al cargar clientes: {e}", font=("Arial", 12), fg='red', bg='#f0f0f0').pack(pady=50)
            
        tk.Button(main_frame, text="← Volver", command=self.show_clientes, bg='#e74c3c', fg='white', relief='flat').pack(pady=10)

    def buscar_cliente(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="Búsqueda Avanzada de Clientes", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#2c3e50').pack(pady=20)

        search_frame = tk.LabelFrame(main_frame, text="Criterios de Búsqueda", bg='#f0f0f0', fg='#2c3e50', font=("Arial", 11, "bold"), padx=15, pady=15)
        search_frame.pack(pady=10, fill=tk.X)

        campos_busqueda = [
            ("Cédula:", "cedula"), ("Nombre:", "nombre"),
            ("Apellido:", "apellido"), ("Teléfono:", "telefono")
        ]
        self.busqueda_entries = {}
        for i, (label_text, field_name) in enumerate(campos_busqueda):
            row, col = i // 2, (i % 2) * 2
            tk.Label(search_frame, text=label_text, font=("Arial", 10), bg='#f0f0f0').grid(row=row, column=col, padx=5, pady=8, sticky='e')
            entry = tk.Entry(search_frame, font=("Arial", 10), width=25)
            entry.grid(row=row, column=col + 1, padx=5, pady=8, sticky='w')
            entry.bind('<Return>', lambda e: self.ejecutar_busqueda())
            self.busqueda_entries[field_name] = entry

        estado_frame = tk.Frame(search_frame, bg='#f0f0f0')
        estado_frame.grid(row=2, column=0, columnspan=4, pady=10, sticky='w')
        tk.Label(estado_frame, text="Estado:", font=("Arial", 10), bg='#f0f0f0').pack(side=tk.LEFT, padx=(5,10))
        self.estado_var = tk.StringVar(value="Todos")
        for text in ["Todos", "Activos", "Vencidos"]:
            tk.Radiobutton(estado_frame, text=text, variable=self.estado_var, value=text, font=("Arial", 9), bg='#f0f0f0', command=self.ejecutar_busqueda).pack(side=tk.LEFT)

        button_frame = tk.Frame(search_frame, bg='#f0f0f0')
        button_frame.grid(row=3, column=0, columnspan=4, pady=15)
        tk.Button(button_frame, text="🔍 Buscar", command=self.ejecutar_busqueda, font=("Arial", 10, "bold"), bg='#3498db', fg='white', width=15, relief='flat').pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="🗑️ Limpiar", command=self.limpiar_busqueda, font=("Arial", 10), bg='#95a5a6', fg='white', width=15, relief='flat').pack(side=tk.LEFT, padx=10)
        
        resultados_frame = tk.Frame(main_frame)
        resultados_frame.pack(fill=tk.BOTH, expand=True, pady=(5,0))
        columns = ('Cédula', 'Nombre', 'Apellido', 'Teléfono', 'Estado', 'Vence')
        self.tree_resultados = ttk.Treeview(resultados_frame, columns=columns, show='headings', height=8)
        column_config = [('Cédula', 100), ('Nombre', 150), ('Apellido', 150), ('Teléfono', 100), ('Estado', 80), ('Vence', 100)]
        for col, width in column_config:
            self.tree_resultados.heading(col, text=col)
            self.tree_resultados.column(col, width=width, anchor='center')
        scrollbar = ttk.Scrollbar(resultados_frame, orient=tk.VERTICAL, command=self.tree_resultados.yview)
        self.tree_resultados.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_resultados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.contador_label = tk.Label(main_frame, text="", font=("Arial", 9), bg='#f0f0f0', fg='#34495e')
        self.contador_label.pack(pady=5)
        
        acciones_frame = tk.Frame(main_frame, bg='#f0f0f0')
        acciones_frame.pack(pady=5)
        tk.Button(acciones_frame, text="💰 Ver Pagos", command=self.ver_pagos_cliente, font=("Arial", 9), bg='#9b59b6', fg='white', width=12, relief='flat').pack(side=tk.LEFT, padx=5)
        tk.Button(acciones_frame, text="🗑️ Eliminar", command=self.eliminar_cliente_seleccionado, font=("Arial", 9), bg='#e74c3c', fg='white', width=12, relief='flat').pack(side=tk.LEFT, padx=5)
        
        tk.Button(main_frame, text="← Volver a Gestión de Clientes", command=self.show_clientes, bg='#2c3e50', fg='white', relief='flat').pack(pady=(10,0))
        self.ejecutar_busqueda()

    def ejecutar_busqueda(self):
        try:
            criterios = {field: entry.get().strip() for field, entry in self.busqueda_entries.items() if entry.get().strip()}
            estado = self.estado_var.get()
            
            # Asumiendo que db.buscar_clientes existe
            resultados = self.db.buscar_clientes(criterios, estado)
            
            self.tree_resultados.delete(*self.tree_resultados.get_children())
            
            for cliente in resultados:
                # La data del cliente viene de db.buscar_clientes
                # (cedula, nombre, apellido, telefono, ..., fecha_vencimiento, estado_pago)
                # Indices: 0-cedula, 1-nombre, 2-apellido, 3-telefono, 8-fecha_vencimiento, 9-estado_pago
                cedula = cliente[0]
                nombre = cliente[1]
                apellido = cliente[2]
                telefono = cliente[3]
                fecha_venc = cliente[8] if len(cliente) > 8 and cliente[8] else "N/A"
                estado_pago = cliente[9] if len(cliente) > 9 and cliente[9] else "Sin pago"

                if estado_pago == "Activo" and fecha_venc != "N/A":
                    venc_dt = datetime.strptime(fecha_venc, '%Y-%m-%d').strftime('%d/%m/%Y')
                else:
                    venc_dt = "N/A"
                    
                self.tree_resultados.insert('', tk.END, values=(cedula, nombre, apellido, telefono, estado_pago, venc_dt))
            
            self.contador_label.config(text=f"Se encontraron {len(resultados)} cliente(s)")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")

    def limpiar_busqueda(self):
        for entry in self.busqueda_entries.values():
            entry.delete(0, tk.END)
        self.estado_var.set("Todos")
        self.ejecutar_busqueda()

    def ver_pagos_cliente(self):
        seleccion = self.tree_resultados.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un cliente de la tabla.")
            return
        self.historial_pagos_cedula(self.tree_resultados.item(seleccion[0])['values'][0])

    def eliminar_cliente_seleccionado(self):
        seleccion = self.tree_resultados.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un cliente de la tabla.")
            return
        
        values = self.tree_resultados.item(seleccion[0])['values']
        if messagebox.askyesno("Confirmar", f"¿Eliminar a {values[1]} {values[2]}?\nEsta acción es irreversible."):
            try:
                # Asumiendo que db.eliminar_cliente existe
                if self.db.eliminar_cliente(values[0]):
                    messagebox.showinfo("Éxito", "Cliente eliminado.")
                    self.ejecutar_busqueda()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el cliente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")

    def historial_pagos_cedula(self, cedula):
        # Esta es una vista, no solo una función de datos
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        try:
            # Asumiendo que db.get_cliente_by_cedula existe
            cliente = self.db.get_cliente_by_cedula(cedula)
            if not cliente:
                 tk.Label(main_frame, text=f"Cliente {cedula} no encontrado", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='red').pack(pady=10)
                 tk.Button(main_frame, text="← Volver a Búsqueda", command=self.buscar_cliente, font=("Arial", 10), bg='#3498db', fg='white', relief='flat').pack(pady=10)
                 return
                 
            tk.Label(main_frame, text=f"Historial de Pagos: {cliente[1]} {cliente[2]}", font=("Arial", 16, "bold"), bg='#f0f0f0').pack(pady=10)
            
            tree_frame = tk.Frame(main_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Asumiendo que db.get_pagos_by_cliente existe
            pagos = self.db.get_pagos_by_cliente(cedula)
            if not pagos:
                tk.Label(tree_frame, text="No hay pagos registrados.", font=("Arial", 12), bg='#f0f0f0').pack(pady=50)
            else:
                columns = ('Fecha Pago', 'Monto', 'Duración', 'Vence', 'Método', 'Estado')
                tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
                col_config = [('Fecha Pago', 100), ('Monto', 80), ('Duración', 100), ('Vence', 100), ('Método', 100), ('Estado', 80)]
                for col, width in col_config:
                    tree.heading(col, text=col)
                    tree.column(col, width=width, anchor='center')
                
                for pago in pagos:
                    estado = "VENCIDO"
                    # pago[7] = activo, pago[5] = fecha_vencimiento
                    if pago[7] == 1 and datetime.strptime(pago[5], '%Y-%m-%d').date() >= datetime.now().date():
                        estado = "ACTIVO"
                    
                    tree.insert('', tk.END, values=(
                        datetime.strptime(pago[4], '%Y-%m-%d').strftime('%d/%m/%Y'), 
                        f"${pago[2]:,.2f}", 
                        f"{pago[3]} mes(es)", 
                        datetime.strptime(pago[5], '%Y-%m-%d').strftime('%d/%m/%Y'), 
                        pago[6], 
                        estado
                    ))
                
                scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscroll=scrollbar.set)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            tk.Button(main_frame, text="← Volver a Búsqueda", command=self.buscar_cliente, font=("Arial", 10), bg='#3498db', fg='white', relief='flat').pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial: {e}")
            self.buscar_cliente()

    def gestion_pagos(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Gestión de Pagos", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#2c3e50').pack(pady=20)
        
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        buttons = [
            ("💰 Registrar Pago", self.registrar_pago),
            ("📋 Historial de Pagos", self.historial_pagos),
            ("⚠️ Clientes Vencidos", self.clientes_vencidos)
        ]
        
        for i, (text, command) in enumerate(buttons):
            tk.Button(button_frame, text=text, command=command, font=("Arial", 11), bg='#9b59b6', fg='white', width=25, height=2, relief='flat').pack(pady=10)
        
        tk.Button(main_frame, text="← Volver al Menú Principal", command=self.create_main_menu, font=("Arial", 10), bg='#e74c3c', fg='white', relief='flat').pack(pady=20)

    def registrar_pago(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="Registro de Pago", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#2c3e50').pack(pady=20)

        form_frame = tk.Frame(main_frame, bg='#f0f0f0')
        form_frame.pack(pady=20)

        tk.Label(form_frame, text="Cédula del Cliente:", font=("Arial", 10), bg='#f0f0f0').grid(row=0, column=0, padx=5, pady=8, sticky='e')
        self.pago_cedula_entry = tk.Entry(form_frame, font=("Arial", 10), width=30)
        self.pago_cedula_entry.grid(row=0, column=1, padx=5, pady=8, sticky='w')
        tk.Button(form_frame, text="Buscar", command=self.buscar_cliente_pago, font=("Arial", 9), bg='#3498db', fg='white', relief='flat').grid(row=0, column=2, padx=5)

        self.info_cliente_label = tk.Label(form_frame, text="Ingrese una cédula y presione 'Buscar'", font=("Arial", 9, "italic"), bg='#f0f0f0', fg='#7f8c8d')
        self.info_cliente_label.grid(row=1, column=0, columnspan=3, pady=5)
        
        tk.Label(form_frame, text="Monto ($):", font=("Arial", 10), bg='#f0f0f0').grid(row=2, column=0, padx=5, pady=8, sticky='e')
        self.pago_monto_entry = tk.Entry(form_frame, font=("Arial", 10), width=30)
        self.pago_monto_entry.grid(row=2, column=1, padx=5, pady=8, sticky='w')
        
        tk.Label(form_frame, text="Duración:", font=("Arial", 10), bg='#f0f0f0').grid(row=3, column=0, sticky='e')
        self.duracion_var = tk.StringVar(value="1")
        duracion_frame = tk.Frame(form_frame, bg='#f0f0f0')
        duracion_frame.grid(row=3, column=1, sticky='w')
        for val, txt in [("1", "1 Mes"), ("3", "3 Meses"), ("6", "6 Meses"), ("12", "1 Año")]:
            tk.Radiobutton(duracion_frame, text=txt, variable=self.duracion_var, value=val, bg='#f0f0f0').pack(side=tk.LEFT)

        tk.Label(form_frame, text="Método de Pago:", font=("Arial", 10), bg='#f0f0f0').grid(row=4, column=0, padx=5, pady=8, sticky='e')
        self.metodo_var = tk.StringVar(value="Efectivo")
        ttk.Combobox(form_frame, textvariable=self.metodo_var, values=["Efectivo", "Tarjeta", "Transferencia"], state="readonly", width=27).grid(row=4, column=1, sticky='w')

        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="💾 Registrar Pago", command=self.guardar_pago, font=("Arial", 10, "bold"), bg='#27ae60', fg='white', relief='flat').pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="❌ Cancelar", command=self.gestion_pagos, font=("Arial", 10), bg='#e74c3c', fg='white', relief='flat').pack(side=tk.LEFT, padx=10)
        
        self.cliente_actual_pago = None # Para verificar en guardar_pago

    def buscar_cliente_pago(self):
        cedula = self.pago_cedula_entry.get().strip()
        if not cedula:
            self.info_cliente_label.config(text="Por favor, ingrese una cédula.", fg='red')
            return
        
        try:
            # Asumiendo que db.get_cliente_by_cedula existe
            cliente = self.db.get_cliente_by_cedula(cedula)
            if cliente:
                self.cliente_actual_pago = cliente # Guardar para usarlo en guardar_pago
                # Asumiendo que db.get_pago_activo existe
                pago_activo = self.db.get_pago_activo(cedula)
                estado = "SIN MEMBRESÍA ACTIVA"
                color = 'orange'
                if pago_activo and datetime.strptime(pago_activo[5], '%Y-%m-%d').date() >= datetime.now().date():
                    estado = f"Activo hasta {datetime.strptime(pago_activo[5], '%Y-%m-%d').strftime('%d/%m/%Y')}"
                    color = 'green'
                self.info_cliente_label.config(text=f"{cliente[1]} {cliente[2]} - {estado}", fg=color)
            else:
                self.cliente_actual_pago = None
                self.info_cliente_label.config(text="Cliente no encontrado.", fg='red')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo buscar cliente: {e}")
            self.cliente_actual_pago = None


    def guardar_pago(self):
        try:
            cedula = self.pago_cedula_entry.get().strip()
            monto_str = self.pago_monto_entry.get().strip()

            if not hasattr(self, 'cliente_actual_pago') or self.cliente_actual_pago is None or self.cliente_actual_pago[0] != cedula:
                messagebox.showwarning("Advertencia", "Debe buscar y confirmar un cliente válido primero.")
                return

            if not monto_str:
                messagebox.showerror("Error", "El campo Monto es obligatorio.")
                return
            
            monto = float(monto_str)
            duracion = int(self.duracion_var.get())
            metodo = self.metodo_var.get()
            
            # Asumiendo que db.insert_pago existe
            if self.db.insert_pago(cedula, monto, duracion, metodo):
                messagebox.showinfo("Éxito", "Pago registrado correctamente.")
                self.gestion_pagos()
            else:
                messagebox.showerror("Error", "No se pudo registrar el pago.")
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

    def historial_pagos(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(main_frame, text="Historial de Pagos", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#2c3e50').pack(pady=10)

        search_frame = tk.Frame(main_frame, bg='#f0f0f0')
        search_frame.pack(pady=10, fill=tk.X, justify=tk.CENTER)
        tk.Label(search_frame, text="Cédula:", bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        self.historial_cedula_entry = tk.Entry(search_frame)
        self.historial_cedula_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Buscar", command=self.mostrar_historial_pagos, bg='#3498db', fg='white').pack(side=tk.LEFT, padx=5)
        
        self.historial_frame = tk.Frame(main_frame, bg='#f0f0f0') # Frame para mostrar la tabla
        self.historial_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(self.historial_frame, text="Ingrese una cédula para ver el historial.", bg='#f0f0f0').pack(pady=20)
        
        tk.Button(main_frame, text="← Volver", command=self.gestion_pagos, font=("Arial", 10), bg='#e74c3c', fg='white', relief='flat').pack(pady=10)

    def mostrar_historial_pagos(self):
        cedula = self.historial_cedula_entry.get().strip()
        if not cedula:
            messagebox.showwarning("Aviso", "Debe ingresar una cédula.")
            return

        # Limpiar el frame de historial anterior
        for widget in self.historial_frame.winfo_children():
            widget.destroy()
        
        # Reutilizamos la función de vista de historial
        # Pero la función historial_pagos_cedula limpia *toda* la ventana
        # Así que la llamaremos directamente.
        self.historial_pagos_cedula(cedula)
        # Necesitamos cambiar el botón "Volver" de esa vista
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                for w_child in widget.winfo_children():
                    if isinstance(w_child, tk.Button) and "Volver" in w_child.cget("text"):
                        w_child.config(text="← Volver a Gestión de Pagos", command=self.gestion_pagos)
                        break


    def clientes_vencidos(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Clientes con Membresías Vencidas", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#e74c3c').pack(pady=20)
        
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        try:
            # Asumiendo que db.get_clientes_vencidos() existe
            clientes = self.db.get_clientes_vencidos() 
            if not clientes:
                tk.Label(tree_frame, text="¡No hay clientes con membresías vencidas!", font=("Arial", 12), fg='green', bg='#f0f0f0').pack(pady=50)
            else:
                columns = ('Cédula', 'Nombre', 'Apellido', 'Vencimiento')
                tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, anchor='center', width=150)
                
                for cliente in clientes:
                    # Asumiendo que cliente[3] es la fecha de vencimiento
                    vencimiento = datetime.strptime(cliente[3], '%Y-%m-%d').strftime('%d/%m/%Y')
                    tree.insert('', tk.END, values=(cliente[0], cliente[1], cliente[2], vencimiento))
                
                scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscroll=scrollbar.set)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        except Exception as e:
            tk.Label(tree_frame, text=f"Error al cargar clientes vencidos: {e}", font=("Arial", 12), fg='red', bg='#f0f0f0').pack(pady=50)
        
        tk.Button(main_frame, text="← Volver", command=self.gestion_pagos, font=("Arial", 10), bg='#e74c3c', fg='white', relief='flat').pack(pady=10)

    def reportes(self):
        messagebox.showinfo("Próximamente", "Módulo de Reportes General - En desarrollo")
        # Esta es la implementación de la parte inferior
        # self.show_reportes() # Este era el placeholder


if __name__ == "__main__":
    root = tk.Tk()
    app = GimnasioApp(root)
    root.mainloop()
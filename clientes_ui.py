import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
from PIL import Image, ImageTk
import pandas as pd

class ClientesUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.cliente_actual = None
        self.foto_path_actual = None
        self.setup_ui()

    # En tu clientes_ui.py existente, busca el método registrar_cliente y reemplázalo con:

    def registrar_cliente(self):
        """Muestra el formulario de registro individual de cliente"""
        # Limpiar el frame principal
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Título
        ttk.Label(self.parent, text="REGISTRO DE CLIENTE", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Frame del formulario
        form_frame = ttk.Frame(self.parent)
        form_frame.pack(pady=20, padx=30, fill=tk.BOTH, expand=True)
        
        # Diccionario para almacenar los entries
        self.entries = {}
        
        # Campos del formulario
        campos = [
            ("Cédula:", "cedula", True),
            ("Nombre:", "nombre", True),
            ("Apellido:", "apellido", True),
            ("Teléfono:", "telefono", False),
            ("Teléfono de Emergencia:", "telefono_emergencia", False),
            ("Dirección:", "direccion", False),
            ("Email:", "email", False)
        ]
        
        # Crear campos del formulario
        for i, (label_text, field_name, obligatorio) in enumerate(campos):
            row_frame = ttk.Frame(form_frame)
            row_frame.pack(fill=tk.X, pady=8)
            
            # Label
            label_text_display = label_text + " *" if obligatorio else label_text
            label = ttk.Label(row_frame, text=label_text_display, width=20, anchor="e")
            label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Entry
            entry = ttk.Entry(row_frame, width=30, font=("Arial", 10))
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            if obligatorio:
                # Marcar visualmente campos obligatorios
                entry.configure(style="Obligatorio.TEntry")
            
            self.entries[field_name] = entry
        
        # Frame de botones del formulario
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(pady=20)
        
        # Botones
        ttk.Button(button_frame, text="💾 Guardar Cliente", 
                command=self.guardar_cliente_formulario,
                style='Success.TButton').pack(side=tk.LEFT, padx=10)
        
        ttk.Button(button_frame, text="🗑️ Limpiar Formulario", 
                command=self.limpiar_formulario).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(button_frame, text="← Volver al Menú", 
                command=self.crear_interfaz_principal).pack(side=tk.LEFT, padx=10)
        
        # Configurar estilos
        self.configurar_estilos()

    def configurar_estilos(self):
        """Configura los estilos visuales para la interfaz"""
        style = ttk.Style()
        style.configure("Obligatorio.TEntry", foreground="black")
        style.configure("Success.TButton", background="#27ae60", foreground="white")
        style.map("Success.TButton",
                background=[('active', '#219955'), ('pressed', '#1e8449')])

    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def guardar_cliente_formulario(self):
        """Guarda el cliente desde el formulario"""
        try:
            # Recoger datos del formulario
            datos = {}
            for field_name, entry in self.entries.items():
                datos[field_name] = entry.get().strip()
            
            # Validar campos obligatorios
            if not datos['cedula']:
                messagebox.showerror("Error", "La cédula es obligatoria.")
                self.entries['cedula'].focus()
                return
            
            if not datos['nombre']:
                messagebox.showerror("Error", "El nombre es obligatorio.")
                self.entries['nombre'].focus()
                return
            
            if not datos['apellido']:
                messagebox.showerror("Error", "El apellido es obligatorio.")
                self.entries['apellido'].focus()
                return
            
            # Validar que la cédula sea numérica
            if not datos['cedula'].isdigit():
                messagebox.showerror("Error", "La cédula debe contener solo números.")
                self.entries['cedula'].focus()
                return
            
            # Insertar en la base de datos usando tu método existente
            resultado = self.db.insert_cliente(
                datos['cedula'], 
                datos['nombre'], 
                datos['apellido'], 
                datos.get('telefono', ''), 
                datos.get('telefono_emergencia', ''), 
                datos.get('direccion', ''), 
                datos.get('email', '')
            )
            
            if resultado:
                messagebox.showinfo("Éxito", "Cliente registrado correctamente.")
                self.limpiar_formulario()
            else:
                messagebox.showerror("Error", "La cédula ya existe en el sistema.")
                self.entries['cedula'].focus()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el cliente: {str(e)}")

    def lista_general(self):
        """Muestra la lista general de todos los clientes"""
        # Limpiar el frame principal
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Título
        ttk.Label(self.parent, text="LISTA GENERAL DE CLIENTES", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Frame de controles (búsqueda rápida y botones)
        controls_frame = ttk.Frame(self.parent)
        controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Búsqueda rápida
        ttk.Label(controls_frame, text="Búsqueda rápida:").pack(side=tk.LEFT, padx=(0, 10))
        self.busqueda_rapida_entry = ttk.Entry(controls_frame, width=30)
        self.busqueda_rapida_entry.pack(side=tk.LEFT, padx=(0, 20))
        self.busqueda_rapida_entry.bind('<KeyRelease>', self.filtrar_lista)
        
        # Botones de acción
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="🔄 Actualizar", 
                command=self.actualizar_lista).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📋 Exportar Excel", 
                command=self.exportar_excel).pack(side=tk.LEFT, padx=5)
        
        # Frame para la tabla
        table_frame = ttk.Frame(self.parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Crear Treeview
        columns = ('Cédula', 'Nombre', 'Apellido', 'Teléfono', 'Email', 'Estado')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        column_widths = {
            'Cédula': 100,
            'Nombre': 150,
            'Apellido': 150,
            'Teléfono': 120,
            'Email': 200,
            'Estado': 80
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[col], anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de acciones para cliente seleccionado
        actions_frame = ttk.Frame(self.parent)
        actions_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(actions_frame, text="👁️ Ver Detalles", 
                command=self.ver_detalles_cliente).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(actions_frame, text="✏️ Editar", 
                command=self.editar_cliente).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(actions_frame, text="💰 Registrar Pago", 
                command=self.registrar_pago_cliente).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(actions_frame, text="🗑️ Eliminar", 
                command=self.eliminar_cliente,
                style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        
        # Contador de registros
        self.contador_label = ttk.Label(self.parent, text="", font=("Arial", 10))
        self.contador_label.pack(pady=5)
        
        # Botón volver
        ttk.Button(self.parent, text="← Volver al Menú", 
                command=self.crear_interfaz_principal).pack(pady=10)
        
        # Cargar datos
        self.actualizar_lista()
        
        # Configurar doble click para ver detalles
        self.tree.bind('<Double-1>', lambda e: self.ver_detalles_cliente())

    def actualizar_lista(self):
        """Actualiza la lista de clientes desde la base de datos"""
        try:
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Obtener clientes de la base de datos
            clientes = self.db.get_all_clientes()
            
            # Insertar clientes en la tabla
            for cliente in clientes:
                # Asumiendo que la estructura es: (cedula, nombre, apellido, telefono, email, estado)
                estado = "Activo"  # Puedes ajustar esto según tu lógica de negocio
                if len(cliente) > 5 and cliente[5]:  # Si hay campo de estado
                    estado = cliente[5]
                
                self.tree.insert('', tk.END, values=(
                    cliente[0],  # cédula
                    cliente[1],  # nombre
                    cliente[2],  # apellido
                    cliente[3] if len(cliente) > 3 else '',  # teléfono
                    cliente[4] if len(cliente) > 4 else '',  # email
                    estado
                ))
            
            # Actualizar contador
            self.contador_label.config(text=f"Total de clientes: {len(clientes)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la lista de clientes: {str(e)}")

    def filtrar_lista(self, event=None):
        """Filtra la lista según el texto de búsqueda"""
        search_term = self.busqueda_rapida_entry.get().lower()
        
        # Mostrar todos los items primero
        for item in self.tree.get_children():
            self.tree.item(item, tags=())
        
        if search_term:
            # Ocultar items que no coincidan
            for item in self.tree.get_children():
                values = [str(value).lower() for value in self.tree.item(item)['values']]
                if not any(search_term in value for value in values):
                    self.tree.item(item, tags=('hidden',))
            
            self.tree.configure(displaycolumns='#all')
        
        # Configurar tag para ocultar
        self.tree.tag_configure('hidden', display='')

    def exportar_excel(self):
        """Exporta la lista de clientes a Excel"""
        try:
            clientes = self.db.get_all_clientes()
            if not clientes:
                messagebox.showinfo("Info", "No hay clientes para exportar.")
                return
            
            # Crear DataFrame
            df = pd.DataFrame(clientes, columns=['Cédula', 'Nombre', 'Apellido', 'Teléfono', 'Email', 'Estado'])
            
            # Guardar archivo
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Guardar lista de clientes como"
            )
            
            if file_path:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Éxito", f"Lista exportada correctamente a:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar la lista: {str(e)}")

    def ver_detalles_cliente(self):
        """Muestra los detalles del cliente seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un cliente.")
            return
        
        item = seleccion[0]
        valores = self.tree.item(item)['values']
        cedula = valores[0]
        
        try:
            # Obtener datos completos del cliente
            cliente = self.db.get_cliente_by_cedula(cedula)
            if cliente:
                # Crear ventana de detalles
                detalles_window = tk.Toplevel(self.parent)
                detalles_window.title(f"Detalles - {cliente[1]} {cliente[2]}")
                detalles_window.geometry("400x300")
                detalles_window.transient(self.parent)
                detalles_window.grab_set()
                
                # Mostrar información del cliente
                info_frame = ttk.Frame(detalles_window, padding="20")
                info_frame.pack(fill=tk.BOTH, expand=True)
                
                campos = [
                    ("Cédula:", cliente[0]),
                    ("Nombre:", cliente[1]),
                    ("Apellido:", cliente[2]),
                    ("Teléfono:", cliente[3] if len(cliente) > 3 else 'N/A'),
                    ("Teléfono Emergencia:", cliente[4] if len(cliente) > 4 else 'N/A'),
                    ("Dirección:", cliente[5] if len(cliente) > 5 else 'N/A'),
                    ("Email:", cliente[6] if len(cliente) > 6 else 'N/A')
                ]
                
                for i, (label, valor) in enumerate(campos):
                    ttk.Label(info_frame, text=label, font=("Arial", 10, "bold")).grid(row=i, column=0, sticky='w', pady=5, padx=(0, 10))
                    ttk.Label(info_frame, text=valor or 'N/A').grid(row=i, column=1, sticky='w', pady=5)
                
                # Botón cerrar
                ttk.Button(detalles_window, text="Cerrar", 
                        command=detalles_window.destroy).pack(pady=10)
                
            else:
                messagebox.showerror("Error", "No se pudo obtener la información del cliente.")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los detalles: {str(e)}")

    def editar_cliente(self):
        """Abre el formulario para editar cliente seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un cliente.")
            return
        
        messagebox.showinfo("Editar", "Función de edición - Próximamente")
        # Aquí puedes implementar la edición similar al registro pero cargando datos existentes

    def registrar_pago_cliente(self):
        """Registra un pago para el cliente seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un cliente.")
            return
        
        item = seleccion[0]
        valores = self.tree.item(item)['values']
        cedula = valores[0]
        nombre_completo = f"{valores[1]} {valores[2]}"
        
        messagebox.showinfo("Registrar Pago", 
                        f"Registrar pago para:\n{nombre_completo}\nCédula: {cedula}")

    def eliminar_cliente(self):
        """Elimina el cliente seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un cliente.")
            return
        
        item = seleccion[0]
        valores = self.tree.item(item)['values']
        cedula = valores[0]
        nombre_completo = f"{valores[1]} {valores[2]}"
        
        if messagebox.askyesno("Confirmar Eliminación", 
                            f"¿Está seguro de eliminar al cliente?\n\n{nombre_completo}\nCédula: {cedula}\n\nEsta acción no se puede deshacer."):
            try:
                if self.db.eliminar_cliente(cedula):
                    messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
                    self.actualizar_lista()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el cliente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar cliente: {str(e)}")

    # También necesitas agregar este estilo en configurar_estilos():
    def configurar_estilos(self):
        """Configura los estilos visuales para la interfaz"""
        style = ttk.Style()
        
        # Estilos existentes...
        style.configure("Obligatorio.TEntry", foreground="black")
        style.configure("Success.TButton", background="#27ae60", foreground="white")
        style.configure("Accent.TButton", background="#3498db", foreground="white")
        
        # Nuevo estilo para botones peligrosos
        style.configure("Danger.TButton", background="#e74c3c", foreground="white")
        style.map("Danger.TButton",
                background=[('active', '#c0392b'), ('pressed', '#a93226')])
        
        # Mapeos existentes...
        style.map("Success.TButton",
                background=[('active', '#219955'), ('pressed', '#1e8449')])
        style.map("Accent.TButton",
                background=[('active', '#2980b9'), ('pressed', '#2471a3')])
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo - Lista
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Panel derecho - Formulario
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.setup_lista_clientes(left_frame)
        self.setup_formulario_cliente(right_frame)
        
        self.cargar_clientes()
    
    def setup_lista_clientes(self, parent):
        """Configura la lista de clientes"""
        # Búsqueda
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', self.buscar_clientes)
        
        # Botones
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Nuevo Cliente", 
                  command=self.nuevo_cliente).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Refrescar", 
                  command=self.cargar_clientes).pack(side=tk.LEFT, padx=2)
        
        # Lista
        list_frame = ttk.LabelFrame(parent, text="Clientes")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('cedula', 'nombre', 'apellido', 'telefono')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('cedula', text='Cédula')
        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('apellido', text='Apellido')
        self.tree.heading('telefono', text='Teléfono')
        
        self.tree.column('cedula', width=100)
        self.tree.column('nombre', width=120)
        self.tree.column('apellido', width=120)
        self.tree.column('telefono', width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_cliente_select)
    
    def setup_formulario_cliente(self, parent):
        """Configura el formulario de cliente"""
        self.form_frame = ttk.LabelFrame(parent, text="Datos del Cliente")
        self.form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Foto
        foto_frame = ttk.LabelFrame(self.form_frame, text="Foto")
        foto_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.foto_label = tk.Label(foto_frame, text="Sin foto", 
                                  bg='white', width=30, height=8,
                                  relief='solid', bd=1)
        self.foto_label.pack(padx=10, pady=10)
        
        ttk.Button(foto_frame, text="Seleccionar Foto", 
                  command=self.seleccionar_foto).pack(pady=5)
        
        # Campos
        campos_frame = ttk.Frame(self.form_frame)
        campos_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.campos = {}
        campos_config = [
            ("Cédula:", "cedula"),
            ("Nombre:", "nombre"),
            ("Apellido:", "apellido"), 
            ("Teléfono:", "telefono"),
            ("Teléfono Emergencia:", "telefono_emergencia"),
            ("Dirección:", "direccion")
        ]
        
        for i, (label, key) in enumerate(campos_config):
            ttk.Label(campos_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            entry = ttk.Entry(campos_frame, width=25)
            entry.grid(row=i, column=1, padx=5, pady=2, sticky=tk.W)
            self.campos[key] = entry
        
        # Botones de acción
        botones_frame = ttk.Frame(self.form_frame)
        botones_frame.pack(pady=10)
        
        self.btn_guardar = ttk.Button(botones_frame, text="Guardar", 
                                     command=self.guardar_cliente)
        self.btn_guardar.pack(side=tk.LEFT, padx=5)
        
        self.btn_editar = ttk.Button(botones_frame, text="Editar", 
                                    command=self.habilitar_edicion)
        self.btn_editar.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(botones_frame, text="Eliminar", 
                  command=self.eliminar_cliente).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(botones_frame, text="Limpiar", 
                  command=self.limpiar_formulario).pack(side=tk.LEFT, padx=5)
        
        # Estado inicial - todos los campos habilitados para nuevo cliente
        for entry in self.campos.values():
            entry.config(state='normal')
        self.btn_guardar.config(state='normal')
        self.btn_editar.config(state='disabled')
    
    def cargar_clientes(self):
        """Carga la lista de clientes"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            clientes = self.db.get_all_clientes()
            for cliente in clientes:
                self.tree.insert('', 'end', values=(
                    cliente[0], cliente[1], cliente[2], cliente[3]
                ))
        except Exception as e:
            print(f"Error cargando clientes: {e}")
    
    def buscar_clientes(self, event=None):
        """Busca clientes"""
        try:
            criterio = self.search_var.get()
            clientes = self.db.buscar_clientes({
                'cedula': criterio,
                'nombre': criterio,
                'apellido': criterio
            }, "Todos")
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            for cliente in clientes:
                self.tree.insert('', 'end', values=(
                    cliente[0], cliente[1], cliente[2], cliente[3]
                ))
        except Exception as e:
            print(f"Error buscando: {e}")
    
    def on_cliente_select(self, event):
        """Cuando se selecciona un cliente"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            cedula = self.tree.item(item, 'values')[0]
            self.cargar_cliente(cedula)
    
    def cargar_cliente(self, cedula):
        """Carga un cliente específico"""
        try:
            cliente = self.db.get_cliente_by_cedula(cedula)
            if cliente:
                self.cliente_actual = cliente
                self.mostrar_datos_cliente(cliente)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el cliente: {e}")
    
    def mostrar_datos_cliente(self, cliente):
        """Muestra los datos del cliente en el formulario"""
        # Limpiar campos
        for entry in self.campos.values():
            entry.delete(0, tk.END)
        
        # Llenar datos
        self.campos['cedula'].insert(0, cliente[0])
        self.campos['nombre'].insert(0, cliente[1])
        self.campos['apellido'].insert(0, cliente[2])
        self.campos['telefono'].insert(0, cliente[3] or "")
        self.campos['telefono_emergencia'].insert(0, cliente[4] or "")
        self.campos['direccion'].insert(0, cliente[5] or "")
        
        # Foto
        if cliente[6]:
            self.mostrar_foto(cliente[6])
        else:
            self.foto_label.config(text="Sin foto", image='')
        
        # Poner en modo lectura
        self.modo_lectura()
    
    def mostrar_foto(self, ruta_foto):
        """Muestra la foto del cliente"""
        try:
            if os.path.exists(ruta_foto):
                image = Image.open(ruta_foto)
                image.thumbnail((150, 150))
                photo = ImageTk.PhotoImage(image)
                self.foto_label.config(image=photo, text='')
                self.foto_label.image = photo
                self.foto_path_actual = ruta_foto
            else:
                self.foto_label.config(text="Foto no encontrada", image='')
                self.foto_path_actual = None
        except Exception as e:
            self.foto_label.config(text="Error cargando foto", image='')
            self.foto_path_actual = None
    
    def seleccionar_foto(self):
        """Selecciona una foto"""
        ruta = filedialog.askopenfilename(
            title="Seleccionar foto",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.gif")]
        )
        
        if ruta:
            self.mostrar_foto(ruta)
            messagebox.showinfo("Foto", "Foto seleccionada correctamente")
    
    def nuevo_cliente(self):
        """Prepara el formulario para nuevo cliente"""
        self.limpiar_formulario()
        self.modo_edicion()
        self.cliente_actual = None
        self.campos['cedula'].focus()
    
    def habilitar_edicion(self):
        """Habilita la edición del cliente actual"""
        if not self.cliente_actual:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para editar")
            return
        
        self.modo_edicion()
    
    def modo_lectura(self):
        """Pone el formulario en modo lectura"""
        for entry in self.campos.values():
            entry.config(state='readonly')
        self.btn_guardar.config(state='disabled')
        self.btn_editar.config(state='normal')
    
    def modo_edicion(self):
        """Pone el formulario en modo edición"""
        for entry in self.campos.values():
            entry.config(state='normal')
        self.btn_guardar.config(state='normal')
        self.btn_editar.config(state='disabled')
    
    def guardar_cliente(self):
        """Guarda los datos del cliente"""
        try:
            datos = {
                'cedula': self.campos['cedula'].get().strip(),
                'nombre': self.campos['nombre'].get().strip(),
                'apellido': self.campos['apellido'].get().strip(),
                'telefono': self.campos['telefono'].get().strip(),
                'telefono_emergencia': self.campos['telefono_emergencia'].get().strip(),
                'direccion': self.campos['direccion'].get().strip(),
                'foto_path': self.foto_path_actual or ''
            }
            
            # Validar
            if not datos['cedula'] or not datos['nombre'] or not datos['apellido']:
                messagebox.showwarning("Error", "Cédula, nombre y apellido son obligatorios")
                return
            
            if self.cliente_actual:
                # Actualizar
                if self.db.actualizar_cliente(**datos):
                    messagebox.showinfo("Éxito", "Cliente actualizado")
                    self.cargar_clientes()
                    self.modo_lectura()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar")
            else:
                # Nuevo
                if self.db.insert_cliente(**datos):
                    messagebox.showinfo("Éxito", "Cliente creado")
                    self.cargar_clientes()
                    self.limpiar_formulario()
                else:
                    messagebox.showerror("Error", "No se pudo crear (¿cédula duplicada?)")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando: {e}")
    
    def eliminar_cliente(self):
        """Elimina el cliente actual"""
        if not self.cliente_actual:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para eliminar")
            return
        
        cedula = self.cliente_actual[0]
        nombre = f"{self.cliente_actual[1]} {self.cliente_actual[2]}"
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar a {nombre}?"):
            if self.db.eliminar_cliente(cedula):
                messagebox.showinfo("Éxito", "Cliente eliminado")
                self.cargar_clientes()
                self.limpiar_formulario()
            else:
                messagebox.showerror("Error", "No se pudo eliminar")
    
    def limpiar_formulario(self):
        """Limpia el formulario"""
        self.cliente_actual = None
        self.foto_path_actual = None
        
        for entry in self.campos.values():
            entry.config(state='normal')
            entry.delete(0, tk.END)
        
        self.foto_label.config(text="Sin foto", image='')
        self.modo_lectura()

    def crear_interfaz_principal(self):
        """Vuelve a la interfaz principal dividida"""
        # Limpiar el frame principal
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Recrear la interfaz dividida
        self.setup_ui()
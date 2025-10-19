import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class AccesosUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        titulo = ttk.Label(self.frame, text="🚪 CONTROL DE ACCESOS AL GIMNASIO", 
                          font=('Arial', 16, 'bold'))
        titulo.pack(pady=10)
        
        # Frame de control rápido
        control_frame = ttk.LabelFrame(self.frame, text="Registro Rápido de Acceso")
        control_frame.pack(fill=tk.X, pady=10)
        
        # Entrada de cédula
        ttk.Label(control_frame, text="Cédula del cliente:", 
                 font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, pady=10, padx=5)
        
        self.cedula_var = tk.StringVar()
        self.entry_cedula = ttk.Entry(control_frame, textvariable=self.cedula_var, 
                                     width=20, font=('Arial', 12))
        self.entry_cedula.grid(row=0, column=1, padx=5, pady=10)
        self.entry_cedula.bind('<Return>', self.registrar_entrada)
        self.entry_cedula.focus()
        
        # Botones de acceso
        ttk.Button(control_frame, text="✅ REGISTRAR ENTRADA", 
                  command=self.registrar_entrada,
                  style="Acceso.TButton").grid(row=0, column=2, padx=5, pady=10)
        
        ttk.Button(control_frame, text="❌ REGISTRAR SALIDA", 
                  command=self.registrar_salida,
                  style="Acceso.TButton").grid(row=0, column=3, padx=5, pady=10)
        
        # Info del cliente
        self.info_frame = ttk.LabelFrame(self.frame, text="Información del Cliente")
        self.info_frame.pack(fill=tk.X, pady=10)
        
        self.info_label = ttk.Label(self.info_frame, text="Ingrese una cédula para verificar", 
                                   font=('Arial', 10), foreground='gray')
        self.info_label.pack(padx=10, pady=10)
        
        # Estadísticas rápidas
        stats_frame = ttk.LabelFrame(self.frame, text="Estadísticas de Hoy")
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_label = ttk.Label(stats_frame, text="", font=('Arial', 9))
        self.stats_label.pack(padx=10, pady=5)
        
        # Lista de accesos recientes
        accesos_frame = ttk.LabelFrame(self.frame, text="Accesos Recientes (Últimos 20)")
        accesos_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview para accesos
        columns = ('cedula', 'nombre', 'tipo', 'fecha')
        self.tree = ttk.Treeview(accesos_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.tree.heading('cedula', text='Cédula')
        self.tree.heading('nombre', text='Nombre Completo')
        self.tree.heading('tipo', text='Tipo')
        self.tree.heading('fecha', text='Fecha y Hora')
        
        self.tree.column('cedula', width=100, anchor=tk.CENTER)
        self.tree.column('nombre', width=200, anchor=tk.W)
        self.tree.column('tipo', width=80, anchor=tk.CENTER)
        self.tree.column('fecha', width=150, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(accesos_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configurar estilos
        self.configurar_estilos()
        
        # Actualizar datos iniciales
        self.actualizar_lista_accesos()
        self.actualizar_estadisticas()
    
    def configurar_estilos(self):
        style = ttk.Style()
        style.configure("Acceso.TButton", font=('Arial', 10, 'bold'), padding=5)
    
    def registrar_entrada(self, event=None):
        self.registrar_acceso('Entrada')
    
    def registrar_salida(self, event=None):
        self.registrar_acceso('Salida')
    
    def registrar_acceso(self, tipo_movimiento):
        cedula = self.cedula_var.get().strip()
        if not cedula:
            messagebox.showwarning("Advertencia", "Por favor ingrese una cédula")
            return
        
        # Verificar cliente primero
        cliente = self.db.get_cliente_by_cedula(cedula)
        if not cliente:
            messagebox.showerror("Error", f"Cliente con cédula {cedula} no encontrado")
            return
        
        # Mostrar información del cliente
        nombre_completo = f"{cliente[1]} {cliente[2]}"
        self.info_label.config(text=f"Cliente: {nombre_completo}", foreground='black')
        
        # Registrar acceso
        success, mensaje = self.db.registrar_acceso(cedula, tipo_movimiento)
        
        if success:
            messagebox.showinfo("Éxito", f"{mensaje}\nCliente: {nombre_completo}")
            self.cedula_var.set("")
            self.entry_cedula.focus()
            self.info_label.config(text="Ingrese una cédula para verificar", foreground='gray')
        else:
            messagebox.showerror("Error", mensaje)
        
        self.actualizar_lista_accesos()
        self.actualizar_estadisticas()
    
    def actualizar_lista_accesos(self):
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener accesos recientes
        accesos = self.db.get_accesos_recientes(20)
        
        # Agregar a la lista
        for acceso in accesos:
            nombre_completo = f"{acceso[4]} {acceso[5]}"
            fecha_formateada = acceso[3]
            
            self.tree.insert('', 0, values=(
                acceso[1],  # cedula
                nombre_completo,
                acceso[2],  # tipo
                fecha_formateada
            ))
    
    def actualizar_estadisticas(self):
        try:
            stats = self.db.get_estadisticas_accesos()
            texto = f"✅ Entradas hoy: {stats['accesos_hoy']} | "
            texto += f"📅 Entradas esta semana: {stats['accesos_semana']} | "
            texto += f"🕐 Hora pico: {stats['hora_pico']}:00"
            self.stats_label.config(text=texto)
        except Exception as e:
            print(f"Error actualizando estadísticas: {e}")
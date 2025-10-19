# clientes_ui_simple.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from PIL import Image, ImageTk

class ClientesUISimple:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        print("🔧 Inicializando interfaz de clientes...")
        
        # Frame principal muy simple
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        ttk.Label(main_frame, text="GESTIÓN DE CLIENTES - MODO PRUEBA", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Frame para botones de prueba
        botones_frame = ttk.LabelFrame(main_frame, text="Botones de Prueba")
        botones_frame.pack(pady=20)
        
        # Botón EDITAR de prueba
        self.btn_editar = ttk.Button(botones_frame, text="✏️ EDITAR CLIENTE", 
                                    command=self.probar_editar)
        self.btn_editar.pack(pady=10)
        
        # Botón FOTO de prueba  
        self.btn_foto = ttk.Button(botones_frame, text="📷 SELECCIONAR FOTO", 
                                  command=self.probar_foto)
        self.btn_foto.pack(pady=10)
        
        # Estado del botón editar
        self.btn_editar.config(state='normal')  # Siempre habilitado para prueba
        
        # Área de mensajes
        self.texto_estado = tk.Text(main_frame, height=8, width=60)
        self.texto_estado.pack(pady=10, fill=tk.BOTH, expand=True)
        self.agregar_mensaje("Interfaz cargada. Prueba los botones.")
    
    def agregar_mensaje(self, mensaje):
        self.texto_estado.insert(tk.END, f"{mensaje}\n")
        self.texto_estado.see(tk.END)
    
    def probar_editar(self):
        print("🎯 Botón EDITAR presionado")
        self.agregar_mensaje("✅ Botón EDITAR funcionando correctamente")
        messagebox.showinfo("Éxito", "¡Botón EDITAR funciona!")
    
    def probar_foto(self):
        print("🎯 Botón FOTO presionado")
        self.agregar_mensaje("✅ Botón FOTO funcionando correctamente")
        
        # Probar diálogo de archivos
        ruta = filedialog.askopenfilename(
            title="Seleccionar foto - PRUEBA",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png")]
        )
        
        if ruta:
            self.agregar_mensaje(f"✅ Foto seleccionada: {os.path.basename(ruta)}")
            messagebox.showinfo("Éxito", f"Foto seleccionada: {os.path.basename(ruta)}")
        else:
            self.agregar_mensaje("❌ No se seleccionó foto")
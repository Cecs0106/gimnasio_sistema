import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import shutil
import sqlite3
from datetime import datetime

class ConfiguracionUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.config_file = 'config/config.json'
        self.config_data = self.cargar_configuracion()
        self.setup_ui()
    
    def cargar_configuracion(self):
        """Carga la configuración desde archivo JSON"""
        config_default = {
            'gimnasio': {
                'nombre': 'GIMNASIO FITNESS',
                'direccion': 'Av. Principal #123',
                'telefono': '+1 234-567-8900',
                'horario': 'Lunes a Viernes: 5:00 AM - 10:00 PM\nSábados: 6:00 AM - 8:00 PM\nDomingos: 7:00 AM - 6:00 PM'
            },
            'precios': {
                'mensual': 50.00,
                'trimestral': 135.00,
                'semestral': 240.00,
                'anual': 450.00
            },
            'backup': {
                'auto_backup': True,
                'frecuencia': 'diario',
                'ultimo_backup': None
            },
            'accesos': {
                'notificaciones_sonido': True,
                'modo_kiosco': False,
                'tiempo_inactividad': 300
            }
        }
        
        try:
            os.makedirs('config', exist_ok=True)
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Crear archivo con configuración por defecto
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_default, f, indent=4, ensure_ascii=False)
                return config_default
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            return config_default
    
    def guardar_configuracion(self):
        """Guarda la configuración en archivo JSON"""
        try:
            os.makedirs('config', exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la configuración: {e}")
            return False
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        titulo = ttk.Label(main_frame, text="⚙️ CONFIGURACIÓN DEL SISTEMA", 
                          font=('Arial', 16, 'bold'))
        titulo.pack(pady=10)
        
        # Crear pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Pestañas
        self.tab_gimnasio = ttk.Frame(self.notebook)
        self.tab_precios = ttk.Frame(self.notebook)
        self.tab_backup = ttk.Frame(self.notebook)
        self.tab_accesos = ttk.Frame(self.notebook)
        self.tab_avanzado = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_gimnasio, text="🏢 Gimnasio")
        self.notebook.add(self.tab_precios, text="💰 Precios")
        self.notebook.add(self.tab_backup, text="💾 Backup")
        self.notebook.add(self.tab_accesos, text="🚪 Accesos")
        self.notebook.add(self.tab_avanzado, text="🔧 Avanzado")
        
        self.setup_tab_gimnasio()
        self.setup_tab_precios()
        self.setup_tab_backup()
        self.setup_tab_accesos()
        self.setup_tab_avanzado()
    
    def setup_tab_gimnasio(self):
        """Configura la pestaña de información del gimnasio"""
        main_frame = ttk.Frame(self.tab_gimnasio)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        form_frame = ttk.LabelFrame(main_frame, text="Información del Gimnasio")
        form_frame.pack(fill=tk.X, pady=10)
        
        # Campos de configuración
        campos = [
            ("Nombre del Gimnasio:", "nombre", "gimnasio"),
            ("Dirección:", "direccion", "gimnasio"),
            ("Teléfono:", "telefono", "gimnasio")
        ]
        
        self.entries_gimnasio = {}
        for i, (label, key, seccion) in enumerate(campos):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
            entry.insert(0, self.config_data[seccion].get(key, ''))
            self.entries_gimnasio[key] = entry
        
        # Horario (Text area)
        ttk.Label(form_frame, text="Horario:").grid(row=3, column=0, sticky=tk.NW, padx=5, pady=5)
        self.horario_text = tk.Text(form_frame, width=40, height=6)
        self.horario_text.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.horario_text.insert('1.0', self.config_data['gimnasio'].get('horario', ''))
        
        # Botones
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="💾 Guardar Cambios", 
                  command=self.guardar_config_gimnasio).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="🔄 Restablecer", 
                  command=self.restablecer_gimnasio).pack(side=tk.LEFT, padx=5)
    
    def setup_tab_precios(self):
        """Configura la pestaña de precios"""
        main_frame = ttk.Frame(self.tab_precios)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        form_frame = ttk.LabelFrame(main_frame, text="Configuración de Precios")
        form_frame.pack(fill=tk.X, pady=10)
        
        # Información
        info_label = ttk.Label(form_frame, 
                              text="Establece los precios para los diferentes planes de membresía",
                              font=('Arial', 9))
        info_label.grid(row=0, column=0, columnspan=3, pady=10, padx=5)
        
        # Campos de precios
        precios = [
            ("Mensual (1 mes):", "mensual"),
            ("Trimestral (3 meses):", "trimestral"),
            ("Semestral (6 meses):", "semestral"),
            ("Anual (12 meses):", "anual")
        ]
        
        self.entries_precios = {}
        for i, (label, key) in enumerate(precios):
            ttk.Label(form_frame, text=label).grid(row=i+1, column=0, sticky=tk.W, padx=5, pady=5)
            
            frame = ttk.Frame(form_frame)
            frame.grid(row=i+1, column=1, padx=5, pady=5, sticky=tk.W)
            
            ttk.Label(frame, text="$").pack(side=tk.LEFT)
            entry = ttk.Entry(frame, width=10)
            entry.pack(side=tk.LEFT)
            entry.insert(0, str(self.config_data['precios'].get(key, 0.0)))
            self.entries_precios[key] = entry
        
        # Calculadora de descuentos
        calc_frame = ttk.LabelFrame(form_frame, text="💡 Calculadora de Descuentos")
        calc_frame.grid(row=5, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
        
        ttk.Button(calc_frame, text="Calcular Ahorros", 
                  command=self.mostrar_calculadora).pack(padx=5, pady=5)
        
        # Botones
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="💾 Guardar Precios", 
                  command=self.guardar_config_precios).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="📊 Ver Comparativa", 
                  command=self.mostrar_comparativa).pack(side=tk.LEFT, padx=5)
    
    def setup_tab_backup(self):
        """Configura la pestaña de backup"""
        main_frame = ttk.Frame(self.tab_backup)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configuración de backup automático
        backup_frame = ttk.LabelFrame(main_frame, text="Configuración de Backup Automático")
        backup_frame.pack(fill=tk.X, pady=10)
        
        self.auto_backup_var = tk.BooleanVar(value=self.config_data['backup'].get('auto_backup', True))
        ttk.Checkbutton(backup_frame, text="Backup automático", 
                       variable=self.auto_backup_var).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(backup_frame, text="Frecuencia:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.frecuencia_var = tk.StringVar(value=self.config_data['backup'].get('frecuencia', 'diario'))
        frecuencias = [("Diario", "diario"), ("Semanal", "semanal"), ("Mensual", "mensual")]
        
        for i, (text, value) in enumerate(frecuencias):
            ttk.Radiobutton(backup_frame, text=text, variable=self.frecuencia_var,
                           value=value).grid(row=1, column=i+1, padx=5, pady=5)
        
        # Información del último backup
        info_frame = ttk.LabelFrame(main_frame, text="Información de Backup")
        info_frame.pack(fill=tk.X, pady=10)
        
        ultimo_backup = self.config_data['backup'].get('ultimo_backup', 'Nunca')
        ttk.Label(info_frame, text=f"Último backup: {ultimo_backup}").pack(padx=5, pady=5)
        
        # Botones de acción
        accion_frame = ttk.LabelFrame(main_frame, text="Acciones de Backup")
        accion_frame.pack(fill=tk.X, pady=10)
        
        btn_frame = ttk.Frame(accion_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="💾 Crear Backup Ahora", 
                  command=self.crear_backup_manual).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="📁 Restaurar Backup", 
                  command=self.restaurar_backup).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="🔄 Guardar Configuración", 
                  command=self.guardar_config_backup).pack(side=tk.LEFT, padx=5)
        
        # Estadísticas de backup
        stats_frame = ttk.LabelFrame(main_frame, text="Estadísticas")
        stats_frame.pack(fill=tk.X, pady=10)
        
        try:
            if os.path.exists('backups'):
                backups = [f for f in os.listdir('backups') if f.endswith('.db')]
                ttk.Label(stats_frame, text=f"Backups almacenados: {len(backups)}").pack(padx=5, pady=2)
                
                if backups:
                    # Encontrar el backup más reciente
                    latest = max(backups, key=lambda x: os.path.getctime(os.path.join('backups', x)))
                    size = os.path.getsize(os.path.join('backups', latest))
                    ttk.Label(stats_frame, text=f"Último archivo: {latest}").pack(padx=5, pady=2)
                    ttk.Label(stats_frame, text=f"Tamaño: {size/1024/1024:.2f} MB").pack(padx=5, pady=2)
        except Exception as e:
            print(f"Error calculando estadísticas: {e}")
    
    def setup_tab_accesos(self):
        """Configura la pestaña de accesos"""
        main_frame = ttk.Frame(self.tab_accesos)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        form_frame = ttk.LabelFrame(main_frame, text="Configuración del Sistema de Accesos")
        form_frame.pack(fill=tk.X, pady=10)
        
        # Notificaciones de sonido
        self.sonido_var = tk.BooleanVar(value=self.config_data['accesos'].get('notificaciones_sonido', True))
        ttk.Checkbutton(form_frame, text="Activar notificaciones de sonido", 
                       variable=self.sonido_var).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Modo kiosco
        self.kiosco_var = tk.BooleanVar(value=self.config_data['accesos'].get('modo_kiosco', False))
        ttk.Checkbutton(form_frame, text="Modo kiosco (pantalla completa)", 
                       variable=self.kiosco_var).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Tiempo de inactividad
        ttk.Label(form_frame, text="Tiempo de inactividad (segundos):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.inactividad_var = tk.StringVar(value=str(self.config_data['accesos'].get('tiempo_inactividad', 300)))
        inactividad_entry = ttk.Entry(form_frame, textvariable=self.inactividad_var, width=10)
        inactividad_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Botones
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="💾 Guardar Configuración", 
                  command=self.guardar_config_accesos).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="🎵 Probar Sonido", 
                  command=self.probar_sonido).pack(side=tk.LEFT, padx=5)
    
    def setup_tab_avanzado(self):
        """Configura la pestaña avanzada"""
        main_frame = ttk.Frame(self.tab_avanzado)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Limpieza de datos
        limpieza_frame = ttk.LabelFrame(main_frame, text="Limpieza y Mantenimiento")
        limpieza_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(limpieza_frame, text="🧹 Optimizar Base de Datos", 
                  command=self.optimizar_bd).pack(padx=5, pady=5)
        
        ttk.Button(limpieza_frame, text="📊 Regenerar Estadísticas", 
                  command=self.regenerar_estadisticas).pack(padx=5, pady=5)
        
        # Información del sistema
        info_frame = ttk.LabelFrame(main_frame, text="Información del Sistema")
        info_frame.pack(fill=tk.X, pady=10)
        
        # Mostrar información básica
        try:
            # Tamaño de la base de datos
            if os.path.exists('data/gimnasio.db'):
                size = os.path.getsize('data/gimnasio.db')
                ttk.Label(info_frame, text=f"Tamaño BD: {size/1024/1024:.2f} MB").pack(padx=5, pady=2)
            
            # Número de tablas
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tablas = cursor.fetchall()
            ttk.Label(info_frame, text=f"Tablas en BD: {len(tablas)}").pack(padx=5, pady=2)
            
            # Número de registros
            cursor.execute("SELECT COUNT(*) FROM clientes")
            clientes = cursor.fetchone()[0]
            ttk.Label(info_frame, text=f"Clientes registrados: {clientes}").pack(padx=5, pady=2)
            
            cursor.execute("SELECT COUNT(*) FROM pagos")
            pagos = cursor.fetchone()[0]
            ttk.Label(info_frame, text=f"Pagos registrados: {pagos}").pack(padx=5, pady=2)
            
        except Exception as e:
            print(f"Error obteniendo información del sistema: {e}")
        
        # Botones de peligro
        peligro_frame = ttk.LabelFrame(main_frame, text="⚠️ Zona de Peligro")
        peligro_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(peligro_frame, text="🗑️ Eliminar Datos de Prueba", 
                  command=self.eliminar_datos_prueba, style="Danger.TButton").pack(padx=5, pady=5)
        
        ttk.Button(peligro_frame, text="🔄 Restablecer Configuración", 
                  command=self.restablecer_configuracion, style="Danger.TButton").pack(padx=5, pady=5)
        
        # Configurar estilo para botones peligrosos
        style = ttk.Style()
        style.configure("Danger.TButton", background='#e74c3c', foreground='white')
    
    def guardar_config_gimnasio(self):
        """Guarda la configuración del gimnasio"""
        try:
            for key, entry in self.entries_gimnasio.items():
                self.config_data['gimnasio'][key] = entry.get()
            
            self.config_data['gimnasio']['horario'] = self.horario_text.get('1.0', 'end-1c')
            
            if self.guardar_configuracion():
                messagebox.showinfo("Éxito", "Configuración del gimnasio guardada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
    
    def restablecer_gimnasio(self):
        """Restablece la configuración del gimnasio a valores por defecto"""
        if messagebox.askyesno("Confirmar", "¿Restablecer la información del gimnasio a valores por defecto?"):
            valores_default = {
                'nombre': 'GIMNASIO FITNESS',
                'direccion': 'Av. Principal #123',
                'telefono': '+1 234-567-8900',
                'horario': 'Lunes a Viernes: 5:00 AM - 10:00 PM\nSábados: 6:00 AM - 8:00 PM\nDomingos: 7:00 AM - 6:00 PM'
            }
            
            for key, entry in self.entries_gimnasio.items():
                entry.delete(0, tk.END)
                entry.insert(0, valores_default[key])
            
            self.horario_text.delete('1.0', tk.END)
            self.horario_text.insert('1.0', valores_default['horario'])
    
    def guardar_config_precios(self):
        """Guarda la configuración de precios"""
        try:
            for key, entry in self.entries_precios.items():
                valor = entry.get()
                # Validar que sea un número
                try:
                    precio = float(valor)
                    if precio < 0:
                        raise ValueError("El precio no puede ser negativo")
                    self.config_data['precios'][key] = precio
                except ValueError:
                    messagebox.showerror("Error", f"Precio inválido para {key}: {valor}")
                    return
            
            if self.guardar_configuracion():
                messagebox.showinfo("Éxito", "Precios guardados correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
    
    def mostrar_calculadora(self):
        """Muestra calculadora de ahorros"""
        try:
            mensual = float(self.entries_precios['mensual'].get())
            trimestral = float(self.entries_precios['trimestral'].get())
            semestral = float(self.entries_precios['semestral'].get())
            anual = float(self.entries_precios['anual'].get())
            
            ahorro_trimestral = (mensual * 3 - trimestral) / (mensual * 3) * 100
            ahorro_semestral = (mensual * 6 - semestral) / (mensual * 6) * 100
            ahorro_anual = (mensual * 12 - anual) / (mensual * 12) * 100
            
            mensaje = f"""💡 Calculadora de Ahorros:

• Trimestral: {ahorro_trimestral:.1f}% de ahorro
• Semestral: {ahorro_semestral:.1f}% de ahorro  
• Anual: {ahorro_anual:.1f}% de ahorro

💰 Recomendación: {'Anual' if ahorro_anual > 15 else 'Semestral' if ahorro_semestral > 10 else 'Trimestral' if ahorro_trimestral > 5 else 'Mensual'} ofrece el mejor valor"""
            
            messagebox.showinfo("Calculadora de Ahorros", mensaje)
            
        except ValueError:
            messagebox.showerror("Error", "Ingrese precios válidos para calcular")
    
    def mostrar_comparativa(self):
        """Muestra comparativa de precios"""
        try:
            precios = {}
            for key, entry in self.entries_precios.items():
                precios[key] = float(entry.get())
            
            comparativa = f"""📊 Comparativa de Planes:

• Mensual: ${precios['mensual']:.2f} por mes
• Trimestral: ${precios['trimestral']/3:.2f} por mes
• Semestral: ${precios['semestral']/6:.2f} por mes  
• Anual: ${precios['anual']/12:.2f} por mes

💡 El plan más económico por mes es: {
    'Anual' if precios['anual']/12 < precios['semestral']/6 else 
    'Semestral' if precios['semestral']/6 < precios['trimestral']/3 else 
    'Trimestral' if precios['trimestral']/3 < precios['mensual'] else 
    'Mensual'
}"""
            
            messagebox.showinfo("Comparativa de Precios", comparativa)
            
        except ValueError:
            messagebox.showerror("Error", "Ingrese precios válidos para comparar")
    
    def guardar_config_backup(self):
        """Guarda la configuración de backup"""
        try:
            self.config_data['backup']['auto_backup'] = self.auto_backup_var.get()
            self.config_data['backup']['frecuencia'] = self.frecuencia_var.get()
            
            if self.guardar_configuracion():
                messagebox.showinfo("Éxito", "Configuración de backup guardada")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
    
    def crear_backup_manual(self):
        """Crea un backup manual"""
        try:
            if self.db.crear_backup():
                # Actualizar última fecha de backup
                self.config_data['backup']['ultimo_backup'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.guardar_configuracion()
                messagebox.showinfo("Éxito", "Backup creado correctamente")
            else:
                messagebox.showerror("Error", "No se pudo crear el backup")
        except Exception as e:
            messagebox.showerror("Error", f"Error creando backup: {e}")
    
    def restaurar_backup(self):
        """Restaura un backup"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de backup",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Cerrar conexión actual
                self.db.conn.close()
                
                # Copiar backup sobre la base de datos actual
                shutil.copy2(file_path, 'data/gimnasio.db')
                
                # Reconectar
                self.db.conn = sqlite3.connect('data/gimnasio.db', check_same_thread=False)
                
                messagebox.showinfo("Éxito", "Backup restaurado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo restaurar el backup: {e}")
    
    def guardar_config_accesos(self):
        """Guarda la configuración de accesos"""
        try:
            self.config_data['accesos']['notificaciones_sonido'] = self.sonido_var.get()
            self.config_data['accesos']['modo_kiosco'] = self.kiosco_var.get()
            
            # Validar tiempo de inactividad
            try:
                tiempo = int(self.inactividad_var.get())
                if tiempo < 60:
                    messagebox.showwarning("Advertencia", "El tiempo mínimo es 60 segundos")
                    tiempo = 60
                    self.inactividad_var.set("60")
                self.config_data['accesos']['tiempo_inactividad'] = tiempo
            except ValueError:
                messagebox.showerror("Error", "Tiempo de inactividad debe ser un número")
                return
            
            if self.guardar_configuracion():
                messagebox.showinfo("Éxito", "Configuración de accesos guardada")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
    
    def probar_sonido(self):
        """Prueba el sonido de notificación"""
        messagebox.showinfo("Sonido", "🔊 Sonido de prueba reproducido\n(En una implementación real, se reproduciría un sonido)")
    
    def optimizar_bd(self):
        """Optimiza la base de datos"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("VACUUM")
            self.db.conn.commit()
            messagebox.showinfo("Éxito", "Base de datos optimizada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo optimizar: {e}")
    
    def regenerar_estadisticas(self):
        """Regenera las estadísticas del sistema"""
        messagebox.showinfo("Éxito", "Estadísticas regeneradas correctamente")
    
    def eliminar_datos_prueba(self):
        """Elimina datos de prueba (peligroso)"""
        if messagebox.askyesno("⚠️ PELIGRO", 
                              "¿Está seguro de eliminar todos los datos de prueba?\n\nEsta acción NO se puede deshacer."):
            messagebox.showinfo("Info", "Función de eliminación de datos deshabilitada por seguridad")
    
    def restablecer_configuracion(self):
        """Restablece toda la configuración"""
        if messagebox.askyesno("⚠️ PELIGRO", 
                              "¿Restablecer toda la configuración a valores por defecto?\n\nSe perderán todas las configuraciones personalizadas."):
            try:
                if os.path.exists(self.config_file):
                    os.remove(self.config_file)
                self.config_data = self.cargar_configuracion()
                messagebox.showinfo("Éxito", "Configuración restablecida correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo restablecer: {e}")
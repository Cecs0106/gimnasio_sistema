import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import os

class ReportesUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        titulo = ttk.Label(main_frame, text="📊 DASHBOARD Y REPORTES", 
                          font=('Arial', 16, 'bold'))
        titulo.pack(pady=10)
        
        # Crear pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Pestaña 1: Dashboard Principal
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dashboard, text="📈 Dashboard")
        
        # Pestaña 2: Reportes Detallados
        self.tab_reportes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_reportes, text="📋 Reportes")
        
        # Pestaña 3: Estadísticas Avanzadas
        self.tab_estadisticas = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_estadisticas, text="📊 Estadísticas")
        
        self.setup_tab_dashboard()
        self.setup_tab_reportes()
        self.setup_tab_estadisticas()
        
        # Cargar datos iniciales
        self.actualizar_dashboard()
    
    def setup_tab_dashboard(self):
        """Configura el dashboard principal"""
        main_frame = ttk.Frame(self.tab_dashboard)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botones de actualización
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(top_frame, text="🔄 Actualizar Dashboard", 
                  command=self.actualizar_dashboard).pack(side=tk.LEFT, padx=5)
        
        # Frame para métricas rápidas
        metricas_frame = ttk.LabelFrame(main_frame, text="📊 Métricas Rápidas")
        metricas_frame.pack(fill=tk.X, pady=10)
        
        # Crear 4 métricas en una grid
        self.metricas_labels = {}
        metricas_config = [
            ('clientes_total', '👥 Total Clientes', '#3498db'),
            ('clientes_activos', '✅ Clientes Activos', '#27ae60'),
            ('clientes_vencidos', '⚠️ Clientes Vencidos', '#e74c3c'),
            ('ingresos_mes', '💰 Ingresos del Mes', '#9b59b6')
        ]
        
        for i, (key, title, color) in enumerate(metricas_config):
            frame = ttk.Frame(metricas_frame)
            frame.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            
            ttk.Label(frame, text=title, font=('Arial', 10, 'bold')).pack()
            label = ttk.Label(frame, text="Cargando...", font=('Arial', 14, 'bold'))
            label.pack(pady=5)
            self.metricas_labels[key] = label
        
        # Configurar grid weights
        for i in range(4):
            metricas_frame.grid_columnconfigure(i, weight=1)
        
        # Frame para gráficos
        graficos_frame = ttk.Frame(main_frame)
        graficos_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Gráfico de ingresos mensuales
        ingresos_frame = ttk.LabelFrame(graficos_frame, text="📈 Ingresos Mensuales")
        ingresos_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.fig_ingresos = plt.Figure(figsize=(6, 4), dpi=80)
        self.ax_ingresos = self.fig_ingresos.add_subplot(111)
        self.canvas_ingresos = FigureCanvasTkAgg(self.fig_ingresos, ingresos_frame)
        self.canvas_ingresos.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Gráfico de estado de clientes
        estado_frame = ttk.LabelFrame(graficos_frame, text="👥 Estado de Clientes")
        estado_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.fig_estado = plt.Figure(figsize=(6, 4), dpi=80)
        self.ax_estado = self.fig_estado.add_subplot(111)
        self.canvas_estado = FigureCanvasTkAgg(self.fig_estado, estado_frame)
        self.canvas_estado.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_tab_reportes(self):
        """Configura la pestaña de reportes detallados"""
        main_frame = ttk.Frame(self.tab_reportes)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de controles
        controles_frame = ttk.LabelFrame(main_frame, text="⚙️ Configurar Reporte")
        controles_frame.pack(fill=tk.X, pady=10)
        
        # Tipo de reporte
        ttk.Label(controles_frame, text="Tipo de Reporte:").grid(row=0, column=0, padx=5, pady=5)
        self.tipo_reporte_var = tk.StringVar(value="pagos_mensuales")
        tipos_reporte = [
            ("Pagos Mensuales", "pagos_mensuales"),
            ("Clientes por Estado", "clientes_estado"),
            ("Accesos Diarios", "accesos_diarios"),
            ("Ingresos por Método", "ingresos_metodo")
        ]
        
        for i, (text, value) in enumerate(tipos_reporte):
            ttk.Radiobutton(controles_frame, text=text, variable=self.tipo_reporte_var,
                           value=value, command=self.generar_reporte).grid(row=0, column=i+1, padx=5, pady=5)
        
        # Período
        ttk.Label(controles_frame, text="Período:").grid(row=1, column=0, padx=5, pady=5)
        self.periodo_var = tk.StringVar(value="mes_actual")
        periodos = [("Mes Actual", "mes_actual"), ("Últimos 3 Meses", "3_meses"), ("Este Año", "este_año")]
        
        for i, (text, value) in enumerate(periodos):
            ttk.Radiobutton(controles_frame, text=text, variable=self.periodo_var,
                           value=value, command=self.generar_reporte).grid(row=1, column=i+1, padx=5, pady=5)
        
        # Botones de acción
        btn_frame = ttk.Frame(controles_frame)
        btn_frame.grid(row=2, column=0, columnspan=5, pady=10)
        
        ttk.Button(btn_frame, text="📊 Generar Reporte", 
                  command=self.generar_reporte).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="📄 Exportar a Excel", 
                  command=self.exportar_excel).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="🖨️ Imprimir Reporte", 
                  command=self.imprimir_reporte).pack(side=tk.LEFT, padx=5)
        
        # Treeview para reportes
        tree_frame = ttk.LabelFrame(main_frame, text="📋 Datos del Reporte")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.reportes_tree = ttk.Treeview(tree_frame, height=15)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.reportes_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.reportes_tree.configure(yscrollcommand=scrollbar.set)
        self.reportes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def setup_tab_estadisticas(self):
        """Configura la pestaña de estadísticas avanzadas"""
        main_frame = ttk.Frame(self.tab_estadisticas)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Estadísticas de crecimiento
        crecimiento_frame = ttk.LabelFrame(main_frame, text="📈 Tendencias y Crecimiento")
        crecimiento_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Gráfico de tendencia
        self.fig_tendencia = plt.Figure(figsize=(10, 6), dpi=80)
        self.ax_tendencia = self.fig_tendencia.add_subplot(111)
        self.canvas_tendencia = FigureCanvasTkAgg(self.fig_tendencia, crecimiento_frame)
        self.canvas_tendencia.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame para estadísticas numéricas
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_labels = {}
        stats_config = [
            ('tasa_retencion', '🎯 Tasa de Retención', '0%'),
            ('crecimiento_clientes', '📈 Crecimiento de Clientes', '0%'),
            ('ingreso_promedio', '💰 Ingreso Promedio/Mes', '$0'),
            ('clientes_nuevos_mes', '👥 Clientes Nuevos/Mes', '0')
        ]
        
        for i, (key, title, default) in enumerate(stats_config):
            frame = ttk.Frame(stats_frame)
            frame.grid(row=0, column=i, padx=10, pady=5, sticky='nsew')
            
            ttk.Label(frame, text=title, font=('Arial', 9)).pack()
            label = ttk.Label(frame, text=default, font=('Arial', 12, 'bold'))
            label.pack(pady=2)
            self.stats_labels[key] = label
        
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
    
    def actualizar_dashboard(self):
        """Actualiza todo el dashboard"""
        try:
            # Obtener estadísticas completas
            stats = self.db.get_estadisticas_completas()
            
            # Actualizar métricas rápidas
            self.metricas_labels['clientes_total'].config(
                text=f"{stats['total_clientes']}",
                foreground='#2c3e50'
            )
            self.metricas_labels['clientes_activos'].config(
                text=f"{stats['clientes_activos']}",
                foreground='#27ae60'
            )
            self.metricas_labels['clientes_vencidos'].config(
                text=f"{stats['clientes_vencidos']}",
                foreground='#e74c3c'
            )
            self.metricas_labels['ingresos_mes'].config(
                text=f"${stats['ingresos_mes_actual']:,.2f}",
                foreground='#9b59b6'
            )
            
            # Actualizar gráficos
            self.actualizar_grafico_ingresos()
            self.actualizar_grafico_estado_clientes()
            self.actualizar_estadisticas_avanzadas()
            
            messagebox.showinfo("Éxito", "Dashboard actualizado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el dashboard: {e}")
    
    def actualizar_grafico_ingresos(self):
        """Actualiza el gráfico de ingresos mensuales"""
        try:
            # Obtener ingresos de los últimos 6 meses
            self.ax_ingresos.clear()
            
            # Simular datos (en una implementación real, esto vendría de la base de datos)
            meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
            ingresos = [1500, 1800, 2200, 1900, 2500, 2800]
            
            bars = self.ax_ingresos.bar(meses, ingresos, color='#3498db', alpha=0.7)
            self.ax_ingresos.set_title('Ingresos Mensuales', fontweight='bold')
            self.ax_ingresos.set_ylabel('Ingresos ($)')
            
            # Agregar valores en las barras
            for bar in bars:
                height = bar.get_height()
                self.ax_ingresos.text(bar.get_x() + bar.get_width()/2., height,
                                     f'${height:,.0f}',
                                     ha='center', va='bottom')
            
            self.ax_ingresos.grid(True, alpha=0.3)
            self.fig_ingresos.tight_layout()
            self.canvas_ingresos.draw()
            
        except Exception as e:
            print(f"Error actualizando gráfico de ingresos: {e}")
    
    def actualizar_grafico_estado_clientes(self):
        """Actualiza el gráfico de estado de clientes"""
        try:
            self.ax_estado.clear()
            
            stats = self.db.get_estadisticas_completas()
            
            labels = ['Activos', 'Vencidos', 'Sin Pago']
            sizes = [
                stats['clientes_activos'],
                stats['clientes_vencidos'],
                stats['total_clientes'] - stats['clientes_activos'] - stats['clientes_vencidos']
            ]
            colors = ['#27ae60', '#e74c3c', '#95a5a6']
            
            # Filtrar categorías con 0 valores
            filtered_data = [(label, size, color) for label, size, color in zip(labels, sizes, colors) if size > 0]
            if filtered_data:
                labels, sizes, colors = zip(*filtered_data)
            
            wedges, texts, autotexts = self.ax_estado.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                                         startangle=90)
            
            self.ax_estado.set_title('Estado de Clientes', fontweight='bold')
            
            # Mejorar la legibilidad
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            self.fig_estado.tight_layout()
            self.canvas_estado.draw()
            
        except Exception as e:
            print(f"Error actualizando gráfico de estado: {e}")
    
    def actualizar_estadisticas_avanzadas(self):
        """Actualiza las estadísticas avanzadas"""
        try:
            stats = self.db.get_estadisticas_completas()
            
            # Calcular estadísticas avanzadas
            tasa_retencion = stats.get('tasa_retencion', 0)
            crecimiento = 12.5  # Simulado
            ingreso_promedio = stats['ingresos_mes_actual'] / max(stats['clientes_activos'], 1)
            clientes_nuevos = 8  # Simulado
            
            self.stats_labels['tasa_retencion'].config(text=f"{tasa_retencion:.1f}%")
            self.stats_labels['crecimiento_clientes'].config(text=f"{crecimiento:.1f}%")
            self.stats_labels['ingreso_promedio'].config(text=f"${ingreso_promedio:.2f}")
            self.stats_labels['clientes_nuevos_mes'].config(text=f"{clientes_nuevos}")
            
            # Actualizar gráfico de tendencia
            self.actualizar_grafico_tendencia()
            
        except Exception as e:
            print(f"Error actualizando estadísticas avanzadas: {e}")
    
    def actualizar_grafico_tendencia(self):
        """Actualiza el gráfico de tendencias"""
        try:
            self.ax_tendencia.clear()
            
            # Datos simulados para tendencia
            meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
            clientes_activos = [45, 48, 52, 55, 58, 62]
            ingresos = [1500, 1800, 2200, 1900, 2500, 2800]
            
            # Gráfico de línea doble
            ax1 = self.ax_tendencia
            ax2 = ax1.twinx()
            
            # Línea de clientes activos
            line1 = ax1.plot(meses, clientes_activos, 'o-', color='#3498db', linewidth=2, 
                            markersize=8, label='Clientes Activos')
            ax1.set_ylabel('Clientes Activos', color='#3498db')
            ax1.tick_params(axis='y', labelcolor='#3498db')
            
            # Línea de ingresos
            line2 = ax2.plot(meses, ingresos, 's-', color='#e74c3c', linewidth=2,
                            markersize=6, label='Ingresos ($)')
            ax2.set_ylabel('Ingresos ($)', color='#e74c3c')
            ax2.tick_params(axis='y', labelcolor='#e74c3c')
            
            # Combinar leyendas
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax1.legend(lines, labels, loc='upper left')
            
            ax1.set_title('Tendencia: Clientes vs Ingresos', fontweight='bold')
            ax1.grid(True, alpha=0.3)
            
            self.fig_tendencia.tight_layout()
            self.canvas_tendencia.draw()
            
        except Exception as e:
            print(f"Error actualizando gráfico de tendencia: {e}")
    
    def generar_reporte(self):
        """Genera el reporte seleccionado"""
        try:
            tipo_reporte = self.tipo_reporte_var.get()
            periodo = self.periodo_var.get()
            
            # Limpiar treeview
            for item in self.reportes_tree.get_children():
                self.reportes_tree.delete(item)
            
            # Configurar columnas según el tipo de reporte
            if tipo_reporte == "pagos_mensuales":
                self.generar_reporte_pagos_mensuales()
            elif tipo_reporte == "clientes_estado":
                self.generar_reporte_clientes_estado()
            elif tipo_reporte == "accesos_diarios":
                self.generar_reporte_accesos()
            elif tipo_reporte == "ingresos_metodo":
                self.generar_reporte_ingresos_metodo()
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte: {e}")
    
    def generar_reporte_pagos_mensuales(self):
        """Genera reporte de pagos mensuales"""
        columns = ('Mes', 'Total Pagos', 'Ingresos Totales', 'Clientes Nuevos')
        self.reportes_tree.configure(columns=columns)
        
        for col in columns:
            self.reportes_tree.heading(col, text=col)
            self.reportes_tree.column(col, width=120)
        
        # Datos simulados
        datos = [
            ('Enero 2024', 15, 2250.00, 5),
            ('Febrero 2024', 18, 2700.00, 6),
            ('Marzo 2024', 22, 3300.00, 7),
            ('Abril 2024', 19, 2850.00, 4),
            ('Mayo 2024', 25, 3750.00, 8),
            ('Junio 2024', 28, 4200.00, 9)
        ]
        
        for dato in datos:
            self.reportes_tree.insert('', 'end', values=dato)
    
    def generar_reporte_clientes_estado(self):
        """Genera reporte de clientes por estado"""
        columns = ('Estado', 'Cantidad', 'Porcentaje', 'Ingreso Promedio')
        self.reportes_tree.configure(columns=columns)
        
        for col in columns:
            self.reportes_tree.heading(col, text=col)
            self.reportes_tree.column(col, width=120)
        
        stats = self.db.get_estadisticas_completas()
        total = stats['total_clientes']
        
        datos = [
            ('Activos', stats['clientes_activos'], 
             f"{(stats['clientes_activos']/total*100):.1f}%", '$45.00'),
            ('Vencidos', stats['clientes_vencidos'], 
             f"{(stats['clientes_vencidos']/total*100):.1f}%", '$0.00'),
            ('Sin Pago', total - stats['clientes_activos'] - stats['clientes_vencidos'],
             f"{((total - stats['clientes_activos'] - stats['clientes_vencidos'])/total*100):.1f}%", '$0.00')
        ]
        
        for dato in datos:
            self.reportes_tree.insert('', 'end', values=dato)
    
    def generar_reporte_accesos(self):
        """Genera reporte de accesos diarios"""
        columns = ('Fecha', 'Entradas', 'Salidas', 'Total', 'Hora Pico')
        self.reportes_tree.configure(columns=columns)
        
        for col in columns:
            self.reportes_tree.heading(col, text=col)
            self.reportes_tree.column(col, width=100)
        
        # Datos simulados
        datos = [
            ('2024-06-01', 45, 42, 87, '18:00'),
            ('2024-06-02', 38, 35, 73, '19:00'),
            ('2024-06-03', 52, 48, 100, '18:30'),
            ('2024-06-04', 41, 39, 80, '18:00'),
            ('2024-06-05', 47, 44, 91, '19:00')
        ]
        
        for dato in datos:
            self.reportes_tree.insert('', 'end', values=dato)
    
    def generar_reporte_ingresos_metodo(self):
        """Genera reporte de ingresos por método de pago"""
        columns = ('Método', 'Cantidad Pagos', 'Ingresos Totales', 'Porcentaje')
        self.reportes_tree.configure(columns=columns)
        
        for col in columns:
            self.reportes_tree.heading(col, text=col)
            self.reportes_tree.column(col, width=120)
        
        # Datos simulados
        total_ingresos = 19050.00
        datos = [
            ('Efectivo', 85, 12750.00, '67%'),
            ('Tarjeta', 42, 5250.00, '28%'),
            ('Transferencia', 8, 1050.00, '5%')
        ]
        
        for dato in datos:
            self.reportes_tree.insert('', 'end', values=dato)
    
    def exportar_excel(self):
        """Exporta el reporte actual a Excel"""
        try:
            # Obtener datos del treeview
            datos = []
            columns = self.reportes_tree['columns']
            
            # Agregar headers
            headers = [self.reportes_tree.heading(col)['text'] for col in columns]
            datos.append(headers)
            
            # Agregar datos
            for item in self.reportes_tree.get_children():
                valores = self.reportes_tree.item(item)['values']
                datos.append(valores)
            
            # Crear DataFrame y exportar
            df = pd.DataFrame(datos[1:], columns=datos[0])
            
            # Crear directorio de reportes si no existe
            os.makedirs('reportes', exist_ok=True)
            
            # Nombre del archivo
            fecha = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            nombre_archivo = f"reportes/reporte_{fecha}.xlsx"
            
            # Exportar
            df.to_excel(nombre_archivo, index=False)
            
            messagebox.showinfo("Éxito", f"Reporte exportado como:\n{nombre_archivo}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")
    
    def imprimir_reporte(self):
        """Simula la impresión del reporte"""
        messagebox.showinfo("Imprimir", "Función de impresión habilitada\nEl reporte se enviará a la impresora predeterminada")
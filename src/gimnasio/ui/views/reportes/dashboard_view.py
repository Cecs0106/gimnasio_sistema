import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk, messagebox

import matplotlib

# Aseguramos backend compatible con Tk
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import pandas as pd

from gimnasio.services.reports_service import ReportsService
from gimnasio.utils import formatters


class DashboardView(ttk.Frame):
    def __init__(self, parent, reports_service: ReportsService, **_extra_kwargs):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        self.reports_service = reports_service
        self._build_ui()
        self.actualizar_dashboard()

    def _build_ui(self):
        ttk.Label(self, text="📊 DASHBOARD Y REPORTES", font=("Arial", 16, "bold")).pack(pady=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        self.tab_dashboard = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dashboard, text="📈 Dashboard")

        self.tab_reportes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_reportes, text="📋 Reportes")

        self.tab_estadisticas = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_estadisticas, text="📊 Estadísticas")

        self._build_dashboard_tab()
        self._build_reportes_tab()
        self._build_estadisticas_tab()

    # --- Dashboard principal ---
    def _build_dashboard_tab(self):
        main_frame = ttk.Frame(self.tab_dashboard)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=10)

        ttk.Button(top_frame, text="🔄 Actualizar", command=self.actualizar_dashboard).pack(side=tk.LEFT, padx=5)

        metricas_frame = ttk.LabelFrame(main_frame, text="📊 Métricas Rápidas")
        metricas_frame.pack(fill=tk.X, pady=10)

        self.metricas_labels = {}
        for i, (key, title) in enumerate(
            [
                ("clientes_total", "👥 Total Clientes"),
                ("clientes_activos", "✅ Clientes Activos"),
                ("clientes_vencidos", "⚠️ Clientes Vencidos"),
                ("ingresos_mes", "💰 Ingresos del Mes"),
            ]
        ):
            frame = ttk.Frame(metricas_frame)
            frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            ttk.Label(frame, text=title, font=("Arial", 10, "bold")).pack()
            label = ttk.Label(frame, text="Cargando...", font=("Arial", 14, "bold"))
            label.pack(pady=5)
            self.metricas_labels[key] = label
            metricas_frame.grid_columnconfigure(i, weight=1)

        graficos_frame = ttk.Frame(main_frame)
        graficos_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        ingresos_frame = ttk.LabelFrame(graficos_frame, text="📈 Ingresos Mensuales")
        ingresos_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.fig_ingresos = plt.Figure(figsize=(6, 4), dpi=80)
        self.ax_ingresos = self.fig_ingresos.add_subplot(111)
        self.canvas_ingresos = FigureCanvasTkAgg(self.fig_ingresos, ingresos_frame)
        self.canvas_ingresos.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        estado_frame = ttk.LabelFrame(graficos_frame, text="👥 Estado de Clientes")
        estado_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.fig_estado = plt.Figure(figsize=(6, 4), dpi=80)
        self.ax_estado = self.fig_estado.add_subplot(111)
        self.canvas_estado = FigureCanvasTkAgg(self.fig_estado, estado_frame)
        self.canvas_estado.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def actualizar_dashboard(self):
        stats = self.reports_service.estadisticas_generales()
        self.metricas_labels["clientes_total"].config(text=str(stats["total_clientes"]))
        self.metricas_labels["clientes_activos"].config(text=str(stats["clientes_activos"]))
        self.metricas_labels["clientes_vencidos"].config(text=str(stats["clientes_vencidos"]))
        self.metricas_labels["ingresos_mes"].config(
            text=formatters.format_currency(stats["ingresos_mes_actual"])
        )

        datos_ingresos = self.reports_service.ingresos_por_mes()
        self.ax_ingresos.clear()
        if datos_ingresos:
            meses = [row["mes"] for row in datos_ingresos]
            valores = [row["total_mes"] for row in datos_ingresos]
            self.ax_ingresos.plot(meses, valores, marker="o")
            self.ax_ingresos.set_title("Ingresos por mes")
            self.ax_ingresos.set_ylabel("Monto")
        else:
            self.ax_ingresos.text(0.5, 0.5, "Sin datos", ha="center", va="center")
        self.canvas_ingresos.draw()

        total = stats["total_clientes"]
        activos = stats["clientes_activos"]
        vencidos = stats["clientes_vencidos"]
        self.ax_estado.clear()
        if total:
            self.ax_estado.pie(
                [activos, vencidos],
                labels=["Activos", "Vencidos"],
                autopct="%1.1f%%",
                colors=["#27ae60", "#e74c3c"],
            )
            self.ax_estado.set_title("Estado de membresías")
        else:
            self.ax_estado.text(0.5, 0.5, "Sin datos", ha="center", va="center")
        self.canvas_estado.draw()

    # --- Reportes ---
    def _build_reportes_tab(self):
        main_frame = ttk.Frame(self.tab_reportes)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        controles_frame = ttk.LabelFrame(main_frame, text="⚙️ Configurar Reporte")
        controles_frame.pack(fill=tk.X, pady=10)

        ttk.Label(controles_frame, text="Tipo de Reporte:").grid(row=0, column=0, padx=5, pady=5)
        self.tipo_reporte_var = tk.StringVar(value="pagos_mensuales")
        for i, (text, value) in enumerate(
            [
                ("Pagos Mensuales", "pagos_mensuales"),
                ("Clientes por Estado", "clientes_estado"),
                ("Accesos Diarios", "accesos_diarios"),
            ]
        ):
            ttk.Radiobutton(
                controles_frame,
                text=text,
                variable=self.tipo_reporte_var,
                value=value,
                command=self.generar_reporte,
            ).grid(row=0, column=i + 1, padx=5, pady=5)

        ttk.Label(controles_frame, text="Período:").grid(row=1, column=0, padx=5, pady=5)
        self.periodo_var = tk.StringVar(value="mes_actual")
        for i, (text, value) in enumerate(
            [("Mes Actual", "mes_actual"), ("Últimos 3 Meses", "3_meses"), ("Este Año", "este_año")]
        ):
            ttk.Radiobutton(
                controles_frame,
                text=text,
                variable=self.periodo_var,
                value=value,
                command=self.generar_reporte,
            ).grid(row=1, column=i + 1, padx=5, pady=5)

        btn_frame = ttk.Frame(controles_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)
        ttk.Button(btn_frame, text="📊 Generar", command=self.generar_reporte).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Exportar Excel", command=self.exportar_excel).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.LabelFrame(main_frame, text="📋 Datos del Reporte")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.reportes_tree = ttk.Treeview(tree_frame, show="headings", height=15)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.reportes_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.reportes_tree.configure(yscrollcommand=scrollbar.set)
        self.reportes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def generar_reporte(self):
        tipo = self.tipo_reporte_var.get()
        data, columns = [], []
        stats = self.reports_service.estadisticas_generales()

        if tipo == "pagos_mensuales":
            data = self.reports_service.ingresos_por_mes()
            columns = [("mes", "Mes"), ("total_mes", "Total"), ("cantidad_pagos", "Pagos")]
        elif tipo == "clientes_estado":
            data = [
                {"estado": "Activos", "cantidad": stats["clientes_activos"]},
                {"estado": "Vencidos", "cantidad": stats["clientes_vencidos"]},
            ]
            columns = [("estado", "Estado"), ("cantidad", "Cantidad")]
        elif tipo == "accesos_diarios":
            hoy = datetime.now().date()
            rango = [(hoy - timedelta(days=i)).isoformat() for i in range(0, 7)]
            accesos = self.reports_service.accesos_estadisticas()
            data = [{"fecha": fecha, "entradas": accesos["accesos_hoy"] if fecha == hoy.isoformat() else 0} for fecha in rango]
            columns = [("fecha", "Fecha"), ("entradas", "Entradas")]

        self._fill_tree(columns, data)

    def _fill_tree(self, columns, data):
        self.reportes_tree.delete(*self.reportes_tree.get_children())
        self.reportes_tree["columns"] = [col for col, _ in columns]
        for col, heading in columns:
            self.reportes_tree.heading(col, text=heading)
            self.reportes_tree.column(col, anchor=tk.CENTER, width=120)
        for row in data:
            self.reportes_tree.insert("", tk.END, values=[row.get(col, "") for col, _ in columns])

        self.current_report = pd.DataFrame(data)

    def exportar_excel(self):
        if not hasattr(self, "current_report") or self.current_report.empty:
            messagebox.showwarning("Sin datos", "Genera un reporte antes de exportar.")
            return
        try:
            ruta = f"reportes/reporte_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
            self.current_report.to_excel(ruta, index=False)
            messagebox.showinfo("Éxito", f"Reporte exportado en {ruta}")
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo exportar: {exc}")

    # --- Estadísticas ---
    def _build_estadisticas_tab(self):
        main_frame = ttk.Frame(self.tab_estadisticas)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        stats_frame = ttk.LabelFrame(main_frame, text="Indicadores Clave")
        stats_frame.pack(fill=tk.X, pady=10)

        self.stats_labels = {}
        for i, (key, label) in enumerate(
            [
                ("tasa_retencion", "🎯 Tasa de Retención"),
                ("ingreso_promedio", "💰 Ingreso Promedio/Mes"),
            ]
        ):
            frame = ttk.Frame(stats_frame)
            frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            ttk.Label(frame, text=label, font=("Arial", 10)).pack()
            value = ttk.Label(frame, text="—", font=("Arial", 14, "bold"))
            value.pack(pady=5)
            self.stats_labels[key] = value
            stats_frame.grid_columnconfigure(i, weight=1)

        self._update_stats_tab()

    def _update_stats_tab(self):
        stats = self.reports_service.estadisticas_generales()
        self.stats_labels["tasa_retencion"].config(text=f"{stats['tasa_retencion']:.1f}%")
        total = stats["total_clientes"] or 1
        ingreso_promedio = stats["ingresos_mes_actual"] / total
        self.stats_labels["ingreso_promedio"].config(text=formatters.format_currency(ingreso_promedio))

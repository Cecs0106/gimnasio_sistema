import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from gimnasio.services.settings_service import SettingsService


class SettingsView(ttk.Frame):
    def __init__(self, parent, settings_service: SettingsService, **_extra_kwargs):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        self.settings_service = settings_service
        self.config = self.settings_service.load()
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="⚙️ CONFIGURACIÓN DEL SISTEMA", font=("Arial", 16, "bold")).pack(pady=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_info = ttk.Frame(self.notebook)
        self.tab_precios = ttk.Frame(self.notebook)
        self.tab_backup = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_info, text="🏢 Gimnasio")
        self.notebook.add(self.tab_precios, text="💰 Precios")
        self.notebook.add(self.tab_backup, text="💾 Backups")

        self._build_info_tab()
        self._build_precios_tab()
        self._build_backup_tab()

    def _build_info_tab(self):
        frame = ttk.LabelFrame(self.tab_info, text="Información del gimnasio")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        campos = [
            ("Nombre", "nombre"),
            ("Dirección", "direccion"),
            ("Teléfono", "telefono"),
        ]
        self.info_entries = {}
        for idx, (label, key) in enumerate(campos):
            ttk.Label(frame, text=f"{label}:").grid(row=idx, column=0, sticky=tk.W, padx=5, pady=5)
            entry = ttk.Entry(frame, width=40)
            entry.grid(row=idx, column=1, padx=5, pady=5, sticky=tk.W)
            entry.insert(0, self.config["gimnasio"].get(key, ""))
            self.info_entries[key] = entry

        ttk.Label(frame, text="Horario:").grid(row=len(campos), column=0, sticky=tk.NW, padx=5, pady=5)
        self.horario_text = tk.Text(frame, width=40, height=5)
        self.horario_text.grid(row=len(campos), column=1, padx=5, pady=5)
        self.horario_text.insert(tk.END, self.config["gimnasio"].get("horario", ""))

        ttk.Button(frame, text="💾 Guardar", command=self._save_info).grid(
            row=len(campos) + 1, column=1, sticky=tk.E, pady=10
        )

    def _build_precios_tab(self):
        frame = ttk.LabelFrame(self.tab_precios, text="Planes")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.precio_vars = {}
        for idx, (label, key) in enumerate(
            [
                ("Mensual", "mensual"),
                ("Trimestral", "trimestral"),
                ("Semestral", "semestral"),
                ("Anual", "anual"),
            ]
        ):
            ttk.Label(frame, text=f"{label}:").grid(row=idx, column=0, sticky=tk.W, padx=5, pady=5)
            var = tk.StringVar(value=str(self.config["precios"].get(key, "")))
            ttk.Entry(frame, textvariable=var, width=10).grid(row=idx, column=1, padx=5, pady=5, sticky=tk.W)
            self.precio_vars[key] = var

        ttk.Button(frame, text="💾 Guardar precios", command=self._save_precios).grid(
            row=5, column=1, sticky=tk.E, pady=10
        )

    def _build_backup_tab(self):
        frame = ttk.LabelFrame(self.tab_backup, text="Copias de seguridad")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        backup = self.config.get("backup", {})
        ttk.Label(frame, text=f"Último backup: {backup.get('ultimo_backup', 'Nunca')}").pack(anchor=tk.W, pady=5)

        ttk.Button(frame, text="💾 Crear backup", command=self._crear_backup).pack(anchor=tk.W, pady=5)
        ttk.Button(frame, text="♻️ Restaurar backup", command=self._restaurar_backup).pack(anchor=tk.W, pady=5)
        ttk.Button(frame, text="🧹 Optimizar base de datos", command=self._optimizar_bd).pack(anchor=tk.W, pady=5)

    # --- Actions ---
    def _save_info(self):
        for key, entry in self.info_entries.items():
            self.config["gimnasio"][key] = entry.get().strip()
        self.config["gimnasio"]["horario"] = self.horario_text.get("1.0", tk.END).strip()
        self.settings_service.save(self.config)
        messagebox.showinfo("Éxito", "Información guardada correctamente.")

    def _save_precios(self):
        for key, var in self.precio_vars.items():
            try:
                self.config["precios"][key] = float(var.get())
            except ValueError:
                messagebox.showerror("Error", f"Precio inválido para {key}")
                return
        self.settings_service.save(self.config)
        messagebox.showinfo("Éxito", "Precios guardados correctamente.")

    def _crear_backup(self):
        backup_path = self.settings_service.create_backup()
        self.config = self.settings_service.load()
        messagebox.showinfo("Éxito", f"Backup creado en {backup_path}")
        self._refresh_backup_tab()

    def _restaurar_backup(self):
        path = filedialog.askopenfilename(title="Seleccionar backup", filetypes=[("SQLite", "*.db")])
        if not path:
            return
        try:
            self.settings_service.restore_backup(Path(path))
            messagebox.showinfo("Éxito", "Backup restaurado correctamente.")
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo restaurar el backup: {exc}")

    def _optimizar_bd(self):
        try:
            self.settings_service.optimize_database()
            messagebox.showinfo("Éxito", "Base de datos optimizada correctamente.")
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo optimizar: {exc}")

    def _refresh_backup_tab(self):
        self.config = self.settings_service.load()
        for child in self.tab_backup.winfo_children():
            child.destroy()
        self._build_backup_tab()

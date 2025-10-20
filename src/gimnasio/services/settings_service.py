from __future__ import annotations

import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from gimnasio.infrastructure.database import Database


DEFAULT_CONFIG: Dict[str, Any] = {
    "gimnasio": {
        "nombre": "GIMNASIO FITNESS",
        "direccion": "Av. Principal #123",
        "telefono": "+1 234-567-8900",
        "horario": "Lunes a Viernes: 5:00 AM - 10:00 PM\nSábados: 6:00 AM - 8:00 PM\nDomingos: 7:00 AM - 6:00 PM",
    },
    "precios": {"mensual": 50.00, "trimestral": 135.00, "semestral": 240.00, "anual": 450.00},
    "backup": {"auto_backup": True, "frecuencia": "diario", "ultimo_backup": None},
    "accesos": {"notificaciones_sonido": True, "modo_kiosco": False, "tiempo_inactividad": 300},
}


class SettingsService:
    def __init__(self, database: Database, config_path: str = "config/config.json") -> None:
        self.database = database
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            self.save(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
        with self.config_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def save(self, data: Dict[str, Any]) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with self.config_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=4, ensure_ascii=False)

    def create_backup(self) -> Path:
        backup_path = self.database.create_backup()
        data = self.load()
        data.setdefault("backup", {})["ultimo_backup"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save(data)
        return backup_path

    def restore_backup(self, source: Path) -> None:
        if not source.exists():
            raise FileNotFoundError("Archivo de backup no encontrado")
        self.database.conn.close()
        shutil.copy2(source, self.database.db_path)
        self.database.conn = sqlite3.connect(self.database.db_path.as_posix(), check_same_thread=False)
        self.database.conn.row_factory = sqlite3.Row

    def optimize_database(self) -> None:
        with self.database.cursor() as cursor:
            cursor.execute("VACUUM")

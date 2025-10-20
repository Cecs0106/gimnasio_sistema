import os
import sqlite3
import shutil
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional


class Database:
    """Administra la conexión SQLite y garantiza que el esquema exista."""

    def __init__(self, db_path: str = "data/gimnasio.db") -> None:
        self.db_path = Path(db_path)
        self._ensure_parent()
        self.conn = sqlite3.connect(self.db_path.as_posix(), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        self._ensure_columns()

    def _ensure_parent(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _create_tables(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clientes (
                cedula TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                telefono TEXT,
                telefono_emergencia TEXT,
                direccion TEXT,
                email TEXT,
                foto_path TEXT,
                fecha_registro DATE
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pagos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cedula_cliente TEXT,
                monto REAL,
                duracion_meses INTEGER,
                fecha_pago DATE,
                fecha_vencimiento DATE,
                metodo_pago TEXT,
                activo BOOLEAN DEFAULT 1,
                FOREIGN KEY (cedula_cliente) REFERENCES clientes (cedula) ON DELETE CASCADE
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS accesos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cedula_cliente TEXT,
                tipo_movimiento TEXT,
                fecha_hora DATETIME,
                FOREIGN KEY (cedula_cliente) REFERENCES clientes (cedula) ON DELETE CASCADE
            )
            """
        )
        self.conn.commit()

    def _ensure_columns(self) -> None:
        """Asegura columnas opcionales del esquema (ej. 'activo', 'email')."""
        cursor = self.conn.cursor()

        cursor.execute("PRAGMA table_info(pagos)")
        pagos_columns = {column["name"] for column in cursor.fetchall()}
        if "activo" not in pagos_columns:
            cursor.execute("ALTER TABLE pagos ADD COLUMN activo BOOLEAN DEFAULT 1")
            self.conn.commit()

        cursor.execute("PRAGMA table_info(clientes)")
        clientes_columns = {column["name"] for column in cursor.fetchall()}
        if "email" not in clientes_columns:
            cursor.execute("ALTER TABLE clientes ADD COLUMN email TEXT")
            self.conn.commit()

    @contextmanager
    def cursor(self) -> Iterator[sqlite3.Cursor]:
        cur = self.conn.cursor()
        try:
            yield cur
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def create_backup(self, destination: Optional[Path] = None) -> Path:
        destination = destination or Path("backups") / f"backup_gimnasio_{datetime.now():%Y-%m-%d_%H-%M-%S}.db"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.db_path, destination)
        return destination

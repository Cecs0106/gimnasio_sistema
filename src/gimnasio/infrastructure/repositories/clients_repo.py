from __future__ import annotations

import sqlite3
from datetime import date
from typing import Dict, Iterable, List, Optional

from gimnasio.domain.models.client import Client
from gimnasio.infrastructure.database import Database


class ClientsRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def add(self, client: Client) -> bool:
        try:
            with self.database.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO clientes (
                        cedula, nombre, apellido, telefono, telefono_emergencia,
                        direccion, email, foto_path, fecha_registro
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        client.cedula,
                        client.nombre,
                        client.apellido,
                        client.telefono,
                        client.telefono_emergencia,
                        client.direccion,
                        client.email,
                        client.foto_path,
                        (client.fecha_registro or date.today()).isoformat(),
                    ),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def update(self, client: Client) -> bool:
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                UPDATE clientes
                SET nombre = ?, apellido = ?, telefono = ?, telefono_emergencia = ?,
                    direccion = ?, email = ?, foto_path = ?
                WHERE cedula = ?
                """,
                (
                    client.nombre,
                    client.apellido,
                    client.telefono,
                    client.telefono_emergencia,
                    client.direccion,
                    client.email,
                    client.foto_path,
                    client.cedula,
                ),
            )
            return cursor.rowcount > 0

    def get(self, cedula: str) -> Optional[Client]:
        with self.database.cursor() as cursor:
            cursor.execute("SELECT * FROM clientes WHERE cedula = ?", (cedula,))
            row = cursor.fetchone()
            return self._to_client(row) if row else None

    def remove(self, cedula: str) -> bool:
        with self.database.cursor() as cursor:
            cursor.execute("DELETE FROM clientes WHERE cedula = ?", (cedula,))
            return cursor.rowcount > 0

    def all(self) -> List[Client]:
        with self.database.cursor() as cursor:
            cursor.execute("SELECT * FROM clientes ORDER BY nombre, apellido")
            rows = cursor.fetchall()
            return [self._to_client(row) for row in rows]

    def search(self, criteria: Dict[str, str], estado: str = "Todos") -> Iterable[dict]:
        filters = []
        params: List[str] = []
        for field in ("cedula", "nombre", "apellido", "telefono"):
            value = criteria.get(field)
            if value:
                filters.append(f"c.{field} LIKE ?")
                params.append(f"%{value}%")

        estado_sql = ""
        if estado == "Activos":
            estado_sql = "AND p.fecha_vencimiento >= date('now')"
        elif estado == "Vencidos":
            estado_sql = "AND (p.fecha_vencimiento < date('now') OR p.id IS NULL)"

        where_clause = " AND ".join(filters)
        where_clause = f" AND {where_clause}" if where_clause else ""

        query = f"""
            SELECT
                c.*,
                p.fecha_vencimiento as fecha_vencimiento,
                CASE 
                    WHEN p.fecha_vencimiento >= date('now') THEN 'Activo'
                    WHEN p.fecha_vencimiento < date('now') THEN 'Vencido'
                    ELSE 'Sin pago'
                END as estado_pago
            FROM clientes c
            LEFT JOIN pagos p ON c.cedula = p.cedula_cliente AND p.activo = 1
            WHERE 1=1
            {where_clause}
            {estado_sql}
            ORDER BY c.nombre, c.apellido
        """

        with self.database.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                {
                    "cliente": self._to_client(row),
                    "fecha_vencimiento": row["fecha_vencimiento"],
                    "estado_pago": row["estado_pago"],
                }
                for row in rows
            ]

    def proximos_a_vencer(self, dias: int) -> List[dict]:
        query = """
            SELECT c.*, p.fecha_vencimiento,
                   JULIANDAY(p.fecha_vencimiento) - JULIANDAY('now') as dias_restantes
            FROM clientes c
            JOIN pagos p ON c.cedula = p.cedula_cliente
            WHERE p.activo = 1 
              AND p.fecha_vencimiento >= date('now')
              AND p.fecha_vencimiento <= date('now', ?)
            ORDER BY p.fecha_vencimiento ASC
        """
        with self.database.cursor() as cursor:
            cursor.execute(query, (f"+{dias} days",))
            rows = cursor.fetchall()
            return [
                {
                    "cliente": self._to_client(row),
                    "fecha_vencimiento": row["fecha_vencimiento"],
                    "dias_restantes": row["dias_restantes"],
                }
                for row in rows
            ]

    @staticmethod
    def _value(row, key: str, default=None):
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
        try:
            return row[key]
        except (KeyError, IndexError):
            return default

    @classmethod
    def _to_client(cls, row) -> Client:
        fecha_registro = cls._value(row, "fecha_registro")
        parsed_fecha = date.fromisoformat(fecha_registro) if fecha_registro else None
        return Client(
            cedula=cls._value(row, "cedula", ""),
            nombre=cls._value(row, "nombre", ""),
            apellido=cls._value(row, "apellido", ""),
            telefono=cls._value(row, "telefono"),
            telefono_emergencia=cls._value(row, "telefono_emergencia"),
            direccion=cls._value(row, "direccion"),
            email=cls._value(row, "email"),
            foto_path=cls._value(row, "foto_path"),
            fecha_registro=parsed_fecha,
        )

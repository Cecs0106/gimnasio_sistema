from __future__ import annotations

from datetime import datetime, date
from typing import Iterable, Optional

from gimnasio.domain.models.access import AccessEntry
from gimnasio.infrastructure.database import Database


class AccessesRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def add(self, entry: AccessEntry) -> bool:
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO accesos (cedula_cliente, tipo_movimiento, fecha_hora)
                VALUES (?, ?, ?)
                """,
                (
                    entry.cedula_cliente,
                    entry.tipo_movimiento,
                    entry.fecha_hora.isoformat(sep=" "),
                ),
            )
        return True

    def recientes(self, limite: int = 50):
        query = """
            SELECT a.*, c.nombre, c.apellido
            FROM accesos a
            JOIN clientes c ON a.cedula_cliente = c.cedula
            ORDER BY a.fecha_hora DESC
            LIMIT ?
        """
        with self.database.cursor() as cursor:
            cursor.execute(query, (limite,))
            return cursor.fetchall()

    def por_fecha(self, fecha_inicio: date, fecha_fin: Optional[date] = None):
        fecha_fin = fecha_fin or fecha_inicio
        query = """
            SELECT a.*, c.nombre, c.apellido 
            FROM accesos a
            JOIN clientes c ON a.cedula_cliente = c.cedula
            WHERE DATE(a.fecha_hora) BETWEEN ? AND ?
            ORDER BY a.fecha_hora DESC
        """
        with self.database.cursor() as cursor:
            cursor.execute(query, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
            return cursor.fetchall()

    def ultimo_de(self, cedula_cliente: str) -> Optional[AccessEntry]:
        query = """
            SELECT * FROM accesos
            WHERE cedula_cliente = ?
            ORDER BY fecha_hora DESC
            LIMIT 1
        """
        with self.database.cursor() as cursor:
            cursor.execute(query, (cedula_cliente,))
            row = cursor.fetchone()
            if not row:
                return None
            return AccessEntry(
                id=row["id"],
                cedula_cliente=row["cedula_cliente"],
                tipo_movimiento=row["tipo_movimiento"],
                fecha_hora=datetime.fromisoformat(row["fecha_hora"]),
            )

    def estadisticas(self):
        with self.database.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) 
                FROM accesos 
                WHERE DATE(fecha_hora) = DATE('now') 
                AND tipo_movimiento = 'Entrada'
                """
            )
            accesos_hoy = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*) 
                FROM accesos 
                WHERE fecha_hora >= date('now', 'weekday 0', '-7 days')
                AND tipo_movimiento = 'Entrada'
                """
            )
            accesos_semana = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT strftime('%H', fecha_hora) as hora, COUNT(*) as cantidad
                FROM accesos
                WHERE tipo_movimiento = 'Entrada'
                GROUP BY hora
                ORDER BY cantidad DESC
                LIMIT 1
                """
            )
            hora_pico = cursor.fetchone()

        return {
            "accesos_hoy": accesos_hoy,
            "accesos_semana": accesos_semana,
            "hora_pico": hora_pico[0] if hora_pico else "N/A",
        }

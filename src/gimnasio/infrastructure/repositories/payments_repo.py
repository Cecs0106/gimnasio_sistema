from __future__ import annotations

from datetime import date
from typing import Iterable, List, Optional

from gimnasio.domain.models.payment import Payment
from gimnasio.infrastructure.database import Database


class PaymentsRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save(self, payment: Payment) -> bool:
        with self.database.cursor() as cursor:
            cursor.execute(
                "UPDATE pagos SET activo = 0 WHERE cedula_cliente = ?",
                (payment.cedula_cliente,),
            )
            cursor.execute(
                """
                INSERT INTO pagos (
                    cedula_cliente, monto, duracion_meses,
                    fecha_pago, fecha_vencimiento, metodo_pago, activo
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payment.cedula_cliente,
                    payment.monto,
                    payment.duracion_meses,
                    payment.fecha_pago.isoformat(),
                    payment.fecha_vencimiento.isoformat(),
                    payment.metodo_pago,
                    int(payment.activo),
                ),
            )
        return True

    def active_for_client(self, cedula: str) -> Optional[Payment]:
        with self.database.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM pagos WHERE cedula_cliente = ? AND activo = 1",
                (cedula,),
            )
            row = cursor.fetchone()
            return self._to_payment(row) if row else None

    def for_client(self, cedula: str) -> List[Payment]:
        with self.database.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM pagos WHERE cedula_cliente = ? ORDER BY fecha_pago DESC",
                (cedula,),
            )
            rows = cursor.fetchall()
            return [self._to_payment(row) for row in rows]

    def all(self) -> Iterable[Payment]:
        with self.database.cursor() as cursor:
            cursor.execute("SELECT * FROM pagos ORDER BY fecha_pago DESC")
            return [self._to_payment(row) for row in cursor.fetchall()]

    def overdue_clients(self) -> List[dict]:
        query = """
            SELECT c.cedula, c.nombre, c.apellido, c.telefono, p.fecha_vencimiento,
                   JULIANDAY('now') - JULIANDAY(p.fecha_vencimiento) as dias_vencido
            FROM clientes c
            JOIN pagos p ON c.cedula = p.cedula_cliente
            WHERE p.activo = 1 AND p.fecha_vencimiento < date('now')
            ORDER BY p.fecha_vencimiento ASC
        """
        with self.database.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def ingresos_por_mes(self, year: Optional[int] = None):
        year = year or date.today().year
        query = """
            SELECT 
                strftime('%m', fecha_pago) as mes,
                SUM(monto) as total_mes,
                COUNT(*) as cantidad_pagos
            FROM pagos
            WHERE strftime('%Y', fecha_pago) = ?
            GROUP BY mes
            ORDER BY mes
        """
        with self.database.cursor() as cursor:
            cursor.execute(query, (str(year),))
            return cursor.fetchall()

    def resumen_mes_actual(self) -> float:
        query = """
            SELECT SUM(monto)
            FROM pagos
            WHERE strftime('%Y-%m', fecha_pago) = strftime('%Y-%m', 'now')
        """
        with self.database.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchone()[0] or 0.0

    def ingresos_mes_anterior(self) -> float:
        query = """
            SELECT SUM(monto)
            FROM pagos
            WHERE strftime('%Y-%m', fecha_pago) = strftime('%Y-%m', date('now', '-1 month'))
        """
        with self.database.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchone()[0] or 0.0

    @staticmethod
    def _to_payment(row) -> Payment:
        return Payment(
            id=row["id"],
            cedula_cliente=row["cedula_cliente"],
            monto=row["monto"],
            duracion_meses=row["duracion_meses"],
            fecha_pago=date.fromisoformat(row["fecha_pago"]),
            fecha_vencimiento=date.fromisoformat(row["fecha_vencimiento"]),
            metodo_pago=row["metodo_pago"],
            activo=bool(row["activo"]),
        )

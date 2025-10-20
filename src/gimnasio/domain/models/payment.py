from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional


@dataclass(frozen=True)
class Payment:
    id: Optional[int]
    cedula_cliente: str
    monto: float
    duracion_meses: int
    fecha_pago: date
    fecha_vencimiento: date
    metodo_pago: str
    activo: bool = True

    def vence_en(self, referencia: Optional[date] = None) -> int:
        today = referencia or date.today()
        return (self.fecha_vencimiento - today).days

    @property
    def esta_activo(self) -> bool:
        return self.fecha_vencimiento >= date.today() and self.activo

    def renovar(self) -> "Payment":
        nueva_fecha_pago = date.today()
        nueva_fecha_vencimiento = nueva_fecha_pago + timedelta(days=30 * self.duracion_meses)
        return Payment(
            id=None,
            cedula_cliente=self.cedula_cliente,
            monto=self.monto,
            duracion_meses=self.duracion_meses,
            fecha_pago=nueva_fecha_pago,
            fecha_vencimiento=nueva_fecha_vencimiento,
            metodo_pago=self.metodo_pago,
            activo=True,
        )

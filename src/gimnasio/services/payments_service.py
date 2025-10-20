from __future__ import annotations

from datetime import date, timedelta
from typing import List, Optional

from gimnasio.domain.models.payment import Payment
from gimnasio.infrastructure.repositories.clients_repo import ClientsRepository
from gimnasio.infrastructure.repositories.payments_repo import PaymentsRepository
from gimnasio.utils.validators import ValidationError


class PaymentsService:
    def __init__(self, payments_repo: PaymentsRepository, clients_repo: ClientsRepository) -> None:
        self.payments_repo = payments_repo
        self.clients_repo = clients_repo

    def registrar_pago(
        self,
        cedula: str,
        monto: float,
        duracion_meses: int,
        metodo: str,
    ) -> Payment:
        cliente = self.clients_repo.get(cedula)
        if not cliente:
            raise ValidationError("Cliente no encontrado")

        if monto <= 0:
            raise ValidationError("El monto debe ser mayor a 0")

        if duracion_meses <= 0:
            raise ValidationError("La duración debe ser al menos de 1 mes")

        fecha_pago = date.today()
        fecha_vencimiento = fecha_pago + timedelta(days=30 * duracion_meses)

        payment = Payment(
            id=None,
            cedula_cliente=cedula,
            monto=monto,
            duracion_meses=duracion_meses,
            fecha_pago=fecha_pago,
            fecha_vencimiento=fecha_vencimiento,
            metodo_pago=metodo,
            activo=True,
        )
        self.payments_repo.save(payment)
        return payment

    def pago_activo(self, cedula: str) -> Optional[Payment]:
        return self.payments_repo.active_for_client(cedula)

    def historial_cliente(self, cedula: str) -> List[Payment]:
        return self.payments_repo.for_client(cedula)

    def todos(self) -> List[Payment]:
        return list(self.payments_repo.all())

    def clientes_vencidos(self):
        return self.payments_repo.overdue_clients()

    def ingresos_mes_actual(self) -> float:
        return float(self.payments_repo.resumen_mes_actual())

    def ingresos_mes_anterior(self) -> float:
        return float(self.payments_repo.ingresos_mes_anterior())

    def ingresos_por_mes(self, year: Optional[int] = None):
        return self.payments_repo.ingresos_por_mes(year)

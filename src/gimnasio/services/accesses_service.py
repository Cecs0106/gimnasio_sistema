from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple

from gimnasio.domain.models.access import AccessEntry
from gimnasio.domain.models.client import Client
from gimnasio.infrastructure.repositories.accesses_repo import AccessesRepository
from gimnasio.infrastructure.repositories.clients_repo import ClientsRepository
from gimnasio.infrastructure.repositories.payments_repo import PaymentsRepository


class AccessesService:
    def __init__(
        self,
        clients_repo: ClientsRepository,
        payments_repo: PaymentsRepository,
        accesses_repo: AccessesRepository,
    ) -> None:
        self.clients_repo = clients_repo
        self.payments_repo = payments_repo
        self.accesses_repo = accesses_repo

    def registrar(self, cedula: str, tipo_movimiento: str = "Entrada") -> Tuple[bool, str, Optional["Client"]]:
        cliente = self.clients_repo.get(cedula)
        if not cliente:
            return False, "Cliente no encontrado", None

        pago_activo = self.payments_repo.active_for_client(cedula)
        if not pago_activo or not pago_activo.esta_activo:
            return False, "Membresía vencida o inexistente", cliente

        entry = AccessEntry(
            id=None,
            cedula_cliente=cedula,
            tipo_movimiento=tipo_movimiento,
            fecha_hora=datetime.now(),
        )
        self.accesses_repo.add(entry)
        return True, f"Acceso {tipo_movimiento.lower()} registrado correctamente", cliente

    def recientes(self, limite: int = 20):
        return self.accesses_repo.recientes(limite)

    def estadisticas(self):
        return self.accesses_repo.estadisticas()

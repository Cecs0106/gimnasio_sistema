from __future__ import annotations

from datetime import date
from typing import Dict, Iterable, List, Optional

from gimnasio.domain.models.client import Client
from gimnasio.infrastructure.repositories.clients_repo import ClientsRepository
from gimnasio.infrastructure.repositories.payments_repo import PaymentsRepository
from gimnasio.utils import validators
from gimnasio.utils.validators import ValidationError


class ClientsService:
    def __init__(self, clients_repo: ClientsRepository, payments_repo: PaymentsRepository) -> None:
        self.clients_repo = clients_repo
        self.payments_repo = payments_repo

    def register(self, data: Dict[str, str]) -> Client:
        validators.require_numeric(data.get("cedula"), "Cédula")
        validators.require(data.get("nombre"), "Nombre")
        validators.require(data.get("apellido"), "Apellido")

        client = Client(
            cedula=data["cedula"].strip(),
            nombre=data["nombre"].strip(),
            apellido=data["apellido"].strip(),
            telefono=data.get("telefono", "").strip() or None,
            telefono_emergencia=data.get("telefono_emergencia", "").strip() or None,
            direccion=data.get("direccion", "").strip() or None,
            email=data.get("email", "").strip() or None,
            foto_path=data.get("foto_path"),
            fecha_registro=date.today(),
        )

        created = self.clients_repo.add(client)
        if not created:
            raise ValidationError("La cédula ya existe en el sistema.")
        return client

    def update(self, client: Client) -> bool:
        return self.clients_repo.update(client)

    def get(self, cedula: str) -> Optional[Client]:
        return self.clients_repo.get(cedula)

    def delete(self, cedula: str) -> bool:
        return self.clients_repo.remove(cedula)

    def list_all(self) -> List[Client]:
        return self.clients_repo.all()

    def search(self, criteria: Dict[str, str], estado: str = "Todos") -> Iterable[dict]:
        return self.clients_repo.search(criteria, estado)

    def resumen_estado(self) -> Dict[str, int]:
        clientes = self.list_all()
        activos = vencidos = 0
        for cliente in clientes:
            pago = self.payments_repo.active_for_client(cliente.cedula)
            if pago and pago.esta_activo:
                activos += 1
            else:
                vencidos += 1
        return {"total": len(clientes), "activos": activos, "vencidos": vencidos}

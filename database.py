from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from gimnasio.infrastructure.database import Database as CoreDatabase
from gimnasio.infrastructure.repositories.accesses_repo import AccessesRepository
from gimnasio.infrastructure.repositories.clients_repo import ClientsRepository
from gimnasio.infrastructure.repositories.payments_repo import PaymentsRepository
from gimnasio.services.accesses_service import AccessesService
from gimnasio.services.clients_service import ClientsService
from gimnasio.services.payments_service import PaymentsService
from gimnasio.services.reports_service import ReportsService
from gimnasio.services.settings_service import SettingsService
from gimnasio.utils.validators import ValidationError


class Database:
    """Fachada de compatibilidad para código legado.

    Internamente delega en la nueva arquitectura (repositorios/servicios).
    """

    def __init__(self) -> None:
        self._db = CoreDatabase()
        self._clients_repo = ClientsRepository(self._db)
        self._payments_repo = PaymentsRepository(self._db)
        self._accesses_repo = AccessesRepository(self._db)

        self.clients_service = ClientsService(self._clients_repo, self._payments_repo)
        self.payments_service = PaymentsService(self._payments_repo, self._clients_repo)
        self.accesses_service = AccessesService(self._clients_repo, self._payments_repo, self._accesses_repo)
        self.reports_service = ReportsService(self.clients_service, self.payments_service, self.accesses_service)
        self.settings_service = SettingsService(self._db)

    # --- Clientes ---
    def insert_cliente(
        self,
        cedula: str,
        nombre: str,
        apellido: str,
        telefono: str = "",
        telefono_emergencia: str = "",
        direccion: str = "",
        email: str | None = None,
        foto_path: str | None = None,
    ) -> bool:
        try:
            self.clients_service.register(
                {
                    "cedula": cedula,
                    "nombre": nombre,
                    "apellido": apellido,
                    "telefono": telefono,
                    "telefono_emergencia": telefono_emergencia,
                    "direccion": direccion,
                    "email": email or "",
                    "foto_path": foto_path,
                }
            )
            return True
        except ValidationError:
            return False

    def get_cliente_by_cedula(self, cedula: str):
        cliente = self.clients_service.get(cedula)
        if not cliente:
            return None
        return (
            cliente.cedula,
            cliente.nombre,
            cliente.apellido,
            cliente.telefono,
            cliente.telefono_emergencia,
            cliente.direccion,
            cliente.email,
            cliente.foto_path,
            cliente.fecha_registro.isoformat() if cliente.fecha_registro else None,
        )

    def actualizar_cliente(
        self,
        cedula: str,
        nombre: str,
        apellido: str,
        telefono: str,
        telefono_emergencia: str,
        direccion: str,
        foto_path: str,
    ) -> bool:
        cliente_actual = self.clients_service.get(cedula)
        if not cliente_actual:
            return False
        actualizado = cliente_actual.__class__(
            cedula=cedula,
            nombre=nombre,
            apellido=apellido,
            telefono=telefono,
            telefono_emergencia=telefono_emergencia,
            direccion=direccion,
            email=cliente_actual.email,
            foto_path=foto_path,
            fecha_registro=cliente_actual.fecha_registro,
        )
        return self.clients_service.update(actualizado)

    def buscar_clientes(self, criterios: Dict[str, str], estado: str = "Todos") -> List[Tuple]:
        resultados = []
        for resultado in self.clients_service.search(criterios, estado):
            cliente = resultado["cliente"]
            resultados.append(
                (
                    cliente.cedula,
                    cliente.nombre,
                    cliente.apellido,
                    cliente.telefono,
                    cliente.telefono_emergencia,
                    cliente.direccion,
                    cliente.email,
                    cliente.foto_path,
                    resultado.get("fecha_vencimiento"),
                    resultado.get("estado_pago"),
                )
            )
        return resultados

    def get_all_clientes(self) -> List[Tuple]:
        clientes = []
        for cliente in self.clients_service.list_all():
            clientes.append(
                (
                    cliente.cedula,
                    cliente.nombre,
                    cliente.apellido,
                    cliente.telefono,
                    cliente.telefono_emergencia,
                    cliente.direccion,
                    cliente.email,
                    cliente.foto_path,
                    cliente.fecha_registro.isoformat() if cliente.fecha_registro else None,
                )
            )
        return clientes

    def eliminar_cliente(self, cedula: str) -> bool:
        return self.clients_service.delete(cedula)

    def get_historial_completo_cliente(self, cedula: str):
        return {
            "cliente": self.get_cliente_by_cedula(cedula),
            "pagos": self.get_pagos_by_cliente(cedula),
            "accesos": self.get_accesos_recientes(),
        }

    # --- Pagos ---
    def insert_pago(self, cedula_cliente: str, monto: float, duracion_meses: int, metodo_pago: str) -> bool:
        try:
            self.payments_service.registrar_pago(cedula_cliente, monto, duracion_meses, metodo_pago)
            return True
        except ValidationError:
            return False
        except Exception:
            return False

    def get_pagos_by_cliente(self, cedula_cliente: str) -> List[Tuple]:
        pagos = []
        for pago in self.payments_service.historial_cliente(cedula_cliente):
            pagos.append(
                (
                    pago.id,
                    pago.cedula_cliente,
                    pago.monto,
                    pago.duracion_meses,
                    pago.fecha_pago.isoformat(),
                    pago.fecha_vencimiento.isoformat(),
                    pago.metodo_pago,
                    int(pago.activo),
                )
            )
        return pagos

    def get_pago_activo(self, cedula_cliente: str):
        pago = self.payments_service.pago_activo(cedula_cliente)
        if not pago:
            return None
        return (
            pago.id,
            pago.cedula_cliente,
            pago.monto,
            pago.duracion_meses,
            pago.fecha_pago.isoformat(),
            pago.fecha_vencimiento.isoformat(),
            pago.metodo_pago,
            int(pago.activo),
        )

    def get_clientes_vencidos(self):
        return self.payments_service.clientes_vencidos()

    def get_ingresos_por_mes(self, year: Optional[int] = None):
        return self.payments_service.ingresos_por_mes(year)

    # --- Accesos ---
    def registrar_acceso(self, cedula_cliente: str, tipo_movimiento: str = "Entrada"):
        return self.accesses_service.registrar(cedula_cliente, tipo_movimiento)

    def get_accesos_recientes(self, limite: int = 20):
        return self.accesses_service.recientes(limite)

    def get_estadisticas_accesos(self):
        return self.accesses_service.estadisticas()

    # --- Reportes ---
    def get_estadisticas_completas(self):
        stats = self.reports_service.estadisticas_generales()
        return {
            "total_clientes": stats["total_clientes"],
            "clientes_activos": stats["clientes_activos"],
            "clientes_vencidos": stats["clientes_vencidos"],
            "ingresos_mes_actual": stats["ingresos_mes_actual"],
            "ingresos_mes_anterior": stats["ingresos_mes_anterior"],
            "accesos_hoy": self.accesses_service.estadisticas()["accesos_hoy"],
            "tasa_retencion": stats["tasa_retencion"],
        }

    # --- Utilidades ---
    def crear_backup(self, ruta_backup: Optional[str] = None):
        if ruta_backup:
            return self._db.create_backup(Path(ruta_backup))
        return self._db.create_backup()

from __future__ import annotations

from typing import Dict, Iterable, Optional

from gimnasio.services.accesses_service import AccessesService
from gimnasio.services.clients_service import ClientsService
from gimnasio.services.payments_service import PaymentsService


class ReportsService:
    def __init__(
        self,
        clients_service: ClientsService,
        payments_service: PaymentsService,
        accesses_service: AccessesService,
    ) -> None:
        self.clients_service = clients_service
        self.payments_service = payments_service
        self.accesses_service = accesses_service

    def estadisticas_generales(self) -> Dict[str, float]:
        resumen = self.clients_service.resumen_estado()
        ingresos_mes_actual = self.payments_service.ingresos_mes_actual()
        ingresos_mes_anterior = self.payments_service.ingresos_mes_anterior()
        return {
            "total_clientes": resumen["total"],
            "clientes_activos": resumen["activos"],
            "clientes_vencidos": resumen["vencidos"],
            "ingresos_mes_actual": ingresos_mes_actual,
            "ingresos_mes_anterior": ingresos_mes_anterior,
            "tasa_retencion": (resumen["activos"] / resumen["total"] * 100) if resumen["total"] else 0.0,
        }

    def ingresos_por_mes(self, year: Optional[int] = None):
        rows = self.payments_service.ingresos_por_mes(year)
        return [
            {
                "mes": row["mes"],
                "total_mes": row["total_mes"],
                "cantidad_pagos": row["cantidad_pagos"],
            }
            for row in rows
        ]

    def accesos_estadisticas(self) -> Dict[str, float]:
        return self.accesses_service.estadisticas()

    def clientes_vencidos(self):
        return self.payments_service.clientes_vencidos()

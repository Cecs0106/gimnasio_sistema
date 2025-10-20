from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class AccessEntry:
    id: Optional[int]
    cedula_cliente: str
    tipo_movimiento: str
    fecha_hora: datetime

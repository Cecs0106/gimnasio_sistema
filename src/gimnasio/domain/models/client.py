from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Client:
    cedula: str
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    telefono_emergencia: Optional[str] = None
    direccion: Optional[str] = None
    email: Optional[str] = None
    foto_path: Optional[str] = None
    fecha_registro: Optional[date] = None

    @property
    def full_name(self) -> str:
        return f"{self.nombre} {self.apellido}".strip()

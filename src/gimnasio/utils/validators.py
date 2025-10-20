from __future__ import annotations

from typing import Any


class ValidationError(Exception):
    pass


def require(value: Any, field: str) -> None:
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(f"El campo '{field}' es obligatorio.")


def require_numeric(value: str, field: str) -> None:
    require(value, field)
    if not str(value).isdigit():
        raise ValidationError(f"El campo '{field}' debe contener solo números.")

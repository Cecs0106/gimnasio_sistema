from datetime import date, datetime
from typing import Optional, Union


def format_currency(amount: float) -> str:
    return f"${amount:,.2f}"


def format_date(value: Optional[Union[date, datetime]]) -> str:
    if not value:
        return "N/A"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return value.strftime("%Y-%m-%d")

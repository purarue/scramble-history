import numpy  # type: ignore[import]
from decimal import Decimal


def format_decimal(d: Decimal | float | numpy.float64) -> str:
    """Formats time into h:mm:ss.xxx, removing leftmost places if they are zero"""
    minutes, seconds = divmod(float(d), 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{int(hours):01d}:{int(minutes):02d}:{seconds:0>6.3f}"
    elif minutes > 0:
        return f"{int(minutes):01d}:{seconds:0>6.3f}"
    else:
        return f"{seconds:0>5.3f}"

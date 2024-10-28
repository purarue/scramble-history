import numpy  # type: ignore[import]
from decimal import Decimal


def format_decimal(d: Decimal | float | numpy.float64) -> str:
    """Formats time into h:mm:ss.xxx, removing leftmost places if they are zero"""
    minutes, seconds = divmod(float(d), 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return "{:01d}:{:02d}:{:0>6.3f}".format(int(hours), int(minutes), seconds)
    elif minutes > 0:
        return "{:01d}:{:0>6.3f}".format(int(minutes), seconds)
    else:
        return "{:0>5.3f}".format(seconds)

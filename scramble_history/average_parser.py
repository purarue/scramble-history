import warnings
from typing import List, Union, Optional
from decimal import Decimal

import pytimeparse  # type: ignore[import]


def _is_float_like(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def parse_average(average_str: str) -> List[Union[Decimal, str]]:
    """
    Parses times that look like:
    3x3: 22.03 = (DNF), 25.14, 21.69, 19.26, (25.63)
    22.03 = (DNF), 25.14, 21.69, 19.26, (25.63)
    (DNF), 25.14, 21.69, 19.26, (25.63)

    into individual times, like:
    [
        "DNF",
        25.14,
        21.69,
        19.26,
        25.63
    ]

    If it cannot parse a token/time, it leaves it as a string
    """
    if "=" in average_str:
        average_str = average_str.split("=", maxsplit=1)[-1]
    average_str = average_str.strip()
    # split by commas or spaces
    raw_solves = []
    if "," in average_str:
        raw_solves = average_str.split(",")
    elif " " in average_str:
        raw_solves = average_str.split()
    else:
        raw_solves = [average_str]
    # remove parens
    raw_solves = [s.strip().lstrip("(").rstrip(")") for s in raw_solves]
    solves: List[Union[Decimal, str]] = []
    for s in raw_solves:
        if s.lower() in ("dns", "dnf"):
            solves.append(s.upper())
        else:
            if _is_float_like(s):
                solves.append(Decimal(s))
                continue
            td: Optional[Union[float, int]] = pytimeparse.parse(s)
            if td is None:
                solves.append(s)
                warnings.warn(f"Warning: Not sure how to parse token {s}")
            else:
                solves.append(Decimal(td))
    return solves

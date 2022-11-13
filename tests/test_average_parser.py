import json
from pathlib import Path
from decimal import Decimal

tests_dir = Path(__file__).parent.absolute()
average_data = tests_dir / "./average_data.json"
assert average_data.exists()

from scramble_history.average_parser import parse_average


def test_run_all() -> None:
    for avg in json.loads(average_data.read_text()):
        solves = parse_average(avg)
        assert len(solves) >= 1


def test_compare() -> None:
    assert [
        Decimal("7.61"),
        Decimal("8.02"),
        Decimal("10.04"),
        "DNF",
        Decimal("8.09"),
    ] == parse_average("2GEN: 8.71 = (7.61), 8.02, 10.04, (DNF), 8.09")
    assert [
        Decimal("13.5"),
        Decimal("15.18"),
        Decimal("14.5"),
        Decimal("11.29"),
        Decimal("18.82"),
    ] == parse_average("F2L: 14.39 = 13.50, 15.18, 14.50, (11.29), (18.82)")

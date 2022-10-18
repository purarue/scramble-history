import csv
from pathlib import Path
from decimal import Decimal
from typing import NamedTuple, Iterator
from datetime import datetime, timezone


class Result(NamedTuple):
    puzzle: str
    category: str
    scramble: str
    time: Decimal
    penalty: Decimal
    dnf: bool
    date: datetime
    comment: str


def parse_file(path: Path) -> Iterator[Result]:
    with path.open("r", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)
        for row in reader:
            [puzzle, category, time, date, scramble, penalty, comment] = row
            upenalty = 0
            is_dnf = penalty == "2"
            if penalty == "1":
                upenalty = 2
            yield Result(
                puzzle=puzzle,
                category=category,
                scramble=scramble,
                time=Decimal(time) / 1000,
                dnf=is_dnf,
                penalty=Decimal(upenalty),
                date=datetime.fromtimestamp(int(date) / 1000, tz=timezone.utc),
                comment=comment,
            )

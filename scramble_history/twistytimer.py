import sys
import csv
import io
from pathlib import Path
from itertools import chain
from decimal import Decimal
from typing import NamedTuple, Iterator, List, Dict, Any
from datetime import datetime, timezone

from more_itertools import unique_everseen

from .models import State


class Solve(NamedTuple):
    puzzle: str
    category: str
    scramble: str
    time: Decimal
    penalty: Decimal
    dnf: bool
    when: datetime
    comment: str

    def to_csv_list(self) -> List[str]:
        penalty_code = 0
        if self.penalty == Decimal("2"):
            penalty_code = 1
        if self.dnf:
            penalty_code = 2
        return [
            self.puzzle,
            self.category,
            str(int(self.time * 1000)),
            str(int(self.when.timestamp() * 1000)),
            self.scramble,
            str(penalty_code),
            self.comment,
        ]

    @property
    def _prompt_defaults(self) -> Dict[str, Any]:
        return {
            "transformed_puzzle": self.puzzle,
            "transformed_event_description": self.category,
        }

    def _transform_map(self) -> Dict[str, Any]:
        return dict(
            state=State.DNF if self.dnf else State.SOLVED,
            scramble=self.scramble,
            comment=self.comment,
            time=self.time,
            penalty=self.penalty,
            when=self.when,
            full_time=self.time + self.penalty,
        )


HEADER: str = "Puzzle,Category,Time(millis),Date(millis),Scramble,Penalty,Comment"


def serialize_solves(solves: List[Solve]) -> str:
    buf = io.StringIO()
    buf.write(HEADER)
    buf.write("\n")
    buf.flush()
    writer = csv.writer(buf, delimiter=";", quoting=csv.QUOTE_ALL)
    writer.writerows([r.to_csv_list() for r in solves])
    return str(buf.getvalue())


def parse_file(path: Path) -> Iterator[Solve]:
    with path.open("r", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)
        for row in reader:
            try:
                [puzzle, category, time, date, scramble, penalty, comment] = row
            except ValueError:
                print(
                    f"Could not parse line, expected 7 fields, found {len(row)}: {row}",
                    file=sys.stderr,
                )
                raise
            upenalty = 0
            is_dnf = penalty == "2"
            if penalty == "1":
                upenalty = 2
            yield Solve(
                puzzle=puzzle,
                category=category,
                scramble=scramble,
                time=Decimal(time) / 1000,
                dnf=is_dnf,
                penalty=Decimal(upenalty),
                when=datetime.fromtimestamp(int(date) / 1000, tz=timezone.utc),
                comment=comment,
            )


def merge_files(paths: List[Path]) -> Iterator[Solve]:
    yield from unique_everseen(
        chain(*(parse_file(p) for p in paths)),
        key=lambda s: (s.time + s.penalty, s.when),
    )

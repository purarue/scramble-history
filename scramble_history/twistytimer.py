import sys
import csv
import io
from pathlib import Path
from decimal import Decimal
from typing import NamedTuple, Iterator, List
from datetime import datetime, timezone


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

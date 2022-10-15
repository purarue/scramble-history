import sys
import json
import warnings
from decimal import Decimal
from typing import Dict, Any, NamedTuple, List, TextIO, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path


class Solve(NamedTuple):
    scramble: str
    comment: str
    solve_time: Decimal
    penalty: Decimal
    dnf: bool
    when: datetime


class Session(NamedTuple):
    number: int
    name: str
    raw_scramble_type: str
    solves: List[Solve]

    @property
    def scramble_type(self) -> Optional[str]:
        pass


def parse_file(path: Path) -> List[Session]:
    with path.open("r") as f:
        return _parse_blob(f)


def _parse_blob(f: TextIO) -> List[Session]:
    data = json.loads(f.read())
    props: Dict[str, Any] = data["properties"]
    session_raw: str = props["sessionData"]
    assert isinstance(
        session_raw, str
    ), "Fatal error parsing sessions, expected sessionData to be string"
    session_info = json.loads(session_raw)

    sessions: List[Session] = []

    # parse each session
    for session_number, session_val in session_info.items():
        # e.g. for session_number '1' -> key in top-level data
        # is "session1"
        data_key = f"session{session_number}"
        if data_key not in data:
            warnings.warn(
                f"Expected session key '{data_key}' in data, ignoring session '{session_val}'"
            )
            continue

        session_name = session_val["name"]

        options = session_val.get("opt", {})
        # default to WCA 333 scramble if unset
        scramble_code = options.get("scrType", "333")
        raw_scrambles = data[data_key]
        scrambles = map(_parse_scramble, raw_scrambles)

        sessions.append(
            Session(
                number=int(session_number),
                name=session_name,
                raw_scramble_type=scramble_code,
                solves=[s for s in scrambles if s is not None],
            )
        )

    return sessions


RawScramble = Tuple[Tuple[int, int], str, str, int]


def _parse_scramble(raw: RawScramble) -> Optional[Solve]:
    try:
        [[penalty, solve_time], scramble, comment, timestamp] = raw
        is_dnf = penalty == -1

        # if this was a DNF (did not finish), we should remove the penalty (is marked as '-1')
        if is_dnf:
            penalty = 0

        return Solve(
            scramble=scramble.strip(),
            comment=comment,
            solve_time=Decimal(solve_time) / 1000,
            penalty=Decimal(penalty) / 1000,
            dnf=is_dnf,
            when=datetime.fromtimestamp(timestamp, tz=timezone.utc),
        )
    except ValueError as e:
        print(f"Could not parse raw scramble info: {e}", file=sys.stderr)
        return None

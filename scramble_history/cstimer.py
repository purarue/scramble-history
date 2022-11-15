import sys
import json
from decimal import Decimal
from itertools import chain
from typing import Dict, Any, NamedTuple, List, TextIO, Optional, Tuple, Iterator
from datetime import datetime, timezone
from pathlib import Path

from more_itertools import unique_everseen

from .log import logger
from .cstimer_scramble_type import CSTimerScramble, parse_scramble_type
from .models import State


class SessionSolve(NamedTuple):
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
    scramble_type: Optional[CSTimerScramble]
    solves: List[SessionSolve]


class Solve(NamedTuple):
    number: int
    name: str
    raw_scramble_type: str
    scramble_type: Optional[CSTimerScramble]

    scramble: str
    comment: str
    solve_time: Decimal
    penalty: Decimal
    dnf: bool
    when: datetime

    @property
    def _prompt_defaults(self) -> Dict[str, Any]:
        return {
            "transformed_puzzle": self.raw_scramble_type,
            "transformed_event_description": self.scramble_type.name
            if self.scramble_type is not None
            else None,
        }

    def _transform_map(self) -> Dict[str, Any]:
        return dict(
            state=State.DNF if self.dnf else State.SOLVED,
            scramble=self.scramble,
            comment=self.comment,
            time=self.solve_time,
            penalty=self.penalty,
            when=self.when,
            full_time=self.solve_time + self.penalty,
        )


def parse_file(path: Path) -> List[Session]:
    with path.open("r") as f:
        return _parse_blob(f)


def denormalize(sessions: List[Session]) -> Iterator[Solve]:
    for sess in sessions:
        for solve in sess.solves:
            yield Solve(
                number=sess.number,
                name=sess.name,
                raw_scramble_type=sess.raw_scramble_type,
                scramble_type=sess.scramble_type,
                scramble=solve.scramble,
                comment=solve.comment,
                solve_time=solve.solve_time,
                penalty=solve.penalty,
                dnf=solve.dnf,
                when=solve.when,
            )


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
            logger.debug(
                f"Expected session key '{data_key}' in data, ignoring session '{session_val}'"
            )
            continue

        session_name = session_val["name"]

        options = session_val.get("opt", {})
        # default to WCA 333 scramble if unset
        scramble_code = options.get("scrType", "333")
        raw_scrambles = data[data_key]
        scrambles = map(_parse_scramble, raw_scrambles)

        scramble_type: Optional[CSTimerScramble] = None
        try:
            scramble_type = parse_scramble_type(scramble_code)
        except KeyError:
            pass

        sessions.append(
            Session(
                number=int(session_number),
                name=session_name,
                raw_scramble_type=scramble_code,
                scramble_type=scramble_type,
                solves=[s for s in scrambles if s is not None],
            )
        )

    return sessions


RawScramble = Tuple[Tuple[int, int], str, str, int]


def _parse_scramble(raw: RawScramble) -> Optional[SessionSolve]:
    try:
        [[penalty, solve_time], scramble, comment, timestamp] = raw
        is_dnf = penalty == -1

        # if this was a DNF (did not finish), we should remove the penalty (is marked as '-1')
        if is_dnf:
            penalty = 0

        return SessionSolve(
            scramble=scramble.strip(),
            comment=comment,
            solve_time=Decimal(solve_time) / 1000,
            penalty=Decimal(penalty) / 1000,
            dnf=is_dnf,
            when=datetime.fromtimestamp(timestamp, tz=timezone.utc),
        )
    except ValueError as e:
        print(f"Could not parse raw scramble info for {raw}: {e}", file=sys.stderr)
        return None


def merge_files(paths: List[Path]) -> Iterator[Solve]:
    yield from unique_everseen(
        chain(*(denormalize(parse_file(p)) for p in paths)),
        key=lambda s: (s.solve_time + s.penalty, s.when),
    )

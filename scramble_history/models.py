from enum import Enum
from datetime import datetime
from typing import Literal, NamedTuple, Optional
from decimal import Decimal

from .timeformat import format_decimal

Operation = Literal["average", "mean", "global_mean"]


class State(Enum):
    SOLVED = "Solved"
    DNS = "DNS"
    DNF = "DNF"


class Solve(NamedTuple):
    """
    The scramble_history 'merged' Solve model
    """

    # cstimer: scramble code/manual edit
    # twistytimer: puzzle
    # e.g. 333, 444, 222, pyra, skewb, megaminx
    puzzle: str

    # cstimer scramble code
    # twistytimer category/manually edit
    # What this is: e.g. OH, BLD, LSE, F2L
    event_code: str

    # cstimer CSTimerScramble.name
    # twistytimer category/manually edit
    event_description: str

    # if the cube is solved or not
    state: State
    # standard user-facing stuff here
    scramble: str
    comment: Optional[str]
    time: Decimal
    penalty: Decimal
    when: datetime

    def describe(self) -> str:
        if self.state == State.SOLVED:
            return format_decimal(self.time)
        elif self.state == State.DNF:
            return "DNF"
        else:
            return "DNS"

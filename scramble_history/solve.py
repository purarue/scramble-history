from datetime import datetime
from decimal import Decimal
from statistics import mean, StatisticsError
from typing import NamedTuple, Optional, List, Literal, Tuple, Dict

from .state import State
from .error import Res


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


def format_decimal(d: Decimal) -> str:
    """Formats time into h:mm:ss.xxx, removing leftmost places if they are zero"""
    minutes, seconds = divmod(d, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return "{:01d}:{:02d}:{:0>6.3f}".format(int(hours), int(minutes), seconds)
    elif minutes > 0:
        return "{:01d}:{:0>6.3f}".format(int(minutes), seconds)
    else:
        return "{:0>5.3f}".format(seconds)


def findminmax(solves: List[Solve]) -> Tuple[int, int]:
    """
    returns indexes of min, max
    """
    min_i = 0
    min_val = solves[min_i]
    max_i = 0
    max_val = solves[max_i]
    for i, s in enumerate(solves):
        # note: if there are multiple DNFs this marks the last DNF as the ignored one
        # TODO: make configurable?
        if s.state != State.SOLVED:
            # DNF/DNS
            max_i = i
            max_val = s
        else:
            # solve is an actual solve here (not DNF etc.)

            # set max value if larger
            if max_val.state != State.SOLVED:
                pass  # already have a DNF, ignore
            else:
                if s.time > max_val.time:
                    max_i = i
                    max_val = s

            # set min value if smaller

            # if we had saved a DNF (as the first value) and theres a better one, use that
            if min_val.state != State.SOLVED and s.state == State.SOLVED:
                min_i = i
                min_val = s
            else:
                if s.time < min_val.time:
                    min_i = i
                    min_val = s

    return min_i, max_i


Operation = Literal["average", "mean", "global_mean"]


def operation_code(operation: Operation, count: int, solves_len: int) -> str:
    if operation == "global_mean":
        return f"GlobalMean ({count}/{solves_len})"
    else:
        if operation == "mean":
            return f"Mo{count}"
        else:
            return f"Ao{count}"


# e.g. average of 5, mean of 5
class Grouping(NamedTuple):
    operation: Operation
    state: State
    result: Decimal
    solves: List[Solve]
    solve_count: Optional[int]

    def __str__(self) -> str:
        return self.describe()

    @property
    def operation_code(self) -> str:
        assert (
            self.solve_count is not None
        ), f"While computing operation code text, count is not set while operation is {self.operation}"
        return operation_code(self.operation, self.solve_count, len(self.solves))

    @property
    def lhs(self) -> str:
        return "DNF" if self.state != State.SOLVED else format_decimal(self.result)

    def describe_average(self) -> str:
        desc = [s.describe() for s in self.solves]
        if self.operation == "average" and self.state == State.SOLVED:
            mini, maxi = findminmax(self.solves)
            # surround min/max with parenthesis
            desc[mini] = f"({desc[mini]})"
            desc[maxi] = f"({desc[maxi]})"
        return f"{self.lhs} = {' '.join(desc)}"

    def describe(self) -> str:
        return f"{self.operation_code}: {self.describe_average()}"


def grouped(
    solves: List[Solve], operation: Operation, count: Optional[int] = None
) -> Res[Grouping]:
    """
    solves should be sorted/ordered prior to doing a grouping
    """
    # error checking
    if operation in ["average", "mean"]:
        if count is None:
            count = len(solves)
        else:
            if len(solves) < count:
                return ValueError(
                    f"Only have {len(solves)} solves, cannot compute {operation} of {count}"
                )
    if operation == "average" and (
        len(solves) < 3 or (count is not None and count < 3)
    ):
        return ValueError("Cannot do operation 'average' with less than 3 solves")

    # take first 'count' elements if user passed a larger list
    if count is not None and len(solves) > count:
        solves = solves[:count]

    bad_solves_count = len(list(filter(lambda s: s.state != State.SOLVED, solves)))

    # e.g. not set because this is a global mean
    if count is None:
        count = len(solves)

    if operation == "mean":
        if bad_solves_count > 0:
            return Grouping(
                solve_count=count,
                state=State.DNF,
                result=Decimal(0),
                operation=operation,
                solves=solves,
            )
        else:
            return Grouping(
                solve_count=count,
                state=State.SOLVED,
                result=mean([s.time for s in solves]),
                solves=solves,
                operation=operation,
            )
    elif operation == "average":
        if bad_solves_count > 1:
            return Grouping(
                solve_count=count,
                state=State.DNF,
                result=Decimal(0),
                operation=operation,
                solves=solves,
            )
        else:
            min_i, max_i = findminmax(solves)
            return Grouping(
                solve_count=count,
                state=State.SOLVED,
                result=mean(
                    [s.time for i, s in enumerate(solves) if i not in {min_i, max_i}]
                ),
                operation=operation,
                solves=solves,
            )
    elif operation == "global_mean":
        try:
            global_mean = mean([s.time for s in solves if s.state == State.SOLVED])
        except StatisticsError as e:
            return ValueError(str(e) + " - received no valid solves as input")

        return Grouping(
            # dont count DNFs in your global mean 'count'
            solve_count=count - bad_solves_count,
            state=State.SOLVED,
            operation=operation,
            result=global_mean,
            solves=solves,
        )
    else:
        raise ValueError(
            f"Unknown operation {operation}, known: 'average', 'mean', 'global_mean'"
        )


def run_operations(
    solves: List[Solve], operation: Operation, counts: List[int]
) -> Dict[int, str]:
    """
    User-facing function to run multiple operations and catch possible errors
    """
    res: Dict[int, str] = {}
    for c in counts:
        gr = grouped(solves, operation, count=c)
        if isinstance(gr, Exception):
            code = operation_code(operation, c, c)
            res[c] = f"{code}: --"
        else:
            res[c] = f"{gr.operation_code}: {gr.lhs}"

    return res

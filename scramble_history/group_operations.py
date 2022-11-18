from decimal import Decimal
from statistics import mean, StatisticsError
from typing import NamedTuple, Optional, List, Tuple, Dict, Union
from math import inf

from .models import State, Operation, Solve
from .error import Res
from .timeformat import format_decimal


def solves_to_float(solves_dec: List[Solve]) -> List[float]:
    return [inf if s.state != State.SOLVED else float(s.full_time) for s in solves_dec]


def findminmax(solves: Union[List[Solve], List[float]]) -> Tuple[int, int]:
    """
    returns indexes of min, max
    """
    solves_enumd: List[Tuple[int, float]]
    if isinstance(solves[0], Solve):
        solves_enumd = list(enumerate(solves_to_float(solves)))  # type: ignore[arg-type]
    else:
        solves_enumd = list(enumerate(solves))  # type: ignore[arg-type]
    min_i = min(solves_enumd, key=lambda s: s[1])[0]
    max_i = max(solves_enumd, key=lambda s: s[1])[0]
    return min_i, max_i


def operation_code(operation: Operation, count: int, solves_len: int) -> str:
    if operation == "global_mean":
        return f"Global Mean ({count}/{solves_len})"
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
        # should always sort according to datetime,
        # first solve should appear first in the average
        srt = sorted(self.solves, key=lambda sl: sl.when)
        desc = [s.describe() for s in srt]
        if self.operation == "average" and self.state == State.SOLVED:
            mini, maxi = findminmax(srt)
            # surround min/max with parenthesis
            desc[mini] = f"({desc[mini]})"
            desc[maxi] = f"({desc[maxi]})"
        return f"{self.lhs} = {' '.join(desc)}"

    def describe(self) -> str:
        return f"{self.operation_code}: {self.describe_average()}"


def grouped(
    solves_dc: List[Solve],
    *,
    operation: Operation,
    solves_flt: Optional[List[float]] = None,
    count: Optional[int] = None,
) -> Res[Grouping]:
    """
    solves should be sorted/ordered prior to doing a grouping
    """
    if solves_flt is None:
        solves_flt = solves_to_float(solves_dc)
    # error checking
    if operation == "average" or operation == "mean":
        if count is None:
            count = len(solves_flt)
        else:
            if len(solves_flt) < count:
                return ValueError(
                    f"Only have {len(solves_flt)} solves, cannot compute {operation} of {count}"
                )
    if operation == "average" and (
        len(solves_flt) < 3 or (count is not None and count < 3)
    ):
        return ValueError("Cannot do operation 'average' with less than 3 solves")

    # take first 'count' elements if user passed a larger list
    if count is not None and len(solves_flt) > count:
        solves_flt = solves_flt[:count]
        solves_dc = solves_dc[:count]

    bad_solves_count = solves_flt.count(inf)

    # e.g. not set because this is a global mean
    if count is None:
        count = len(solves_dc)

    if operation == "mean":
        if bad_solves_count > 0:
            return Grouping(
                solve_count=count,
                state=State.DNF,
                result=Decimal(0),
                operation=operation,
                solves=solves_dc,
            )
        else:
            return Grouping(
                solve_count=count,
                state=State.SOLVED,
                result=Decimal(mean([s for s in solves_flt if s != inf])),
                solves=solves_dc,
                operation=operation,
            )
    elif operation == "average":
        if bad_solves_count > 1:
            return Grouping(
                solve_count=count,
                state=State.DNF,
                result=Decimal(0),
                operation=operation,
                solves=solves_dc,
            )
        else:
            min_i, max_i = findminmax(solves_flt)
            return Grouping(
                solve_count=count,
                state=State.SOLVED,
                result=Decimal(
                    mean(
                        [s for i, s in enumerate(solves_flt) if i not in {min_i, max_i}]
                    )
                ),
                operation=operation,
                solves=solves_dc,
            )
    elif operation == "global_mean":
        try:
            global_mean = mean([s for s in solves_flt if s != inf])
        except StatisticsError as e:
            return ValueError(str(e) + " - received no valid solves as input")

        return Grouping(
            # dont count DNFs in your global mean 'count'
            solve_count=count - bad_solves_count,
            state=State.SOLVED,
            operation=operation,
            result=Decimal(global_mean),
            solves=solves_dc,
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
        gr = grouped(solves, operation=operation, count=c)
        if isinstance(gr, Exception):
            res[c] = "--"
        else:
            res[c] = gr.lhs

    return res


def find_best_group(
    solves: List[Solve], operation: Operation, counts: List[int]
) -> Dict[int, Grouping]:
    res: Dict[int, Grouping] = {}
    solves_flt = solves_to_float(solves)
    for c in counts:
        try:
            res[c] = min(
                (
                    g
                    for g in (
                        grouped(
                            solves_dc=solves[i:],
                            operation=operation,
                            solves_flt=solves_flt[i:],
                            count=c,
                        )
                        for i in range(len(solves) - c + 1)
                    )
                    if not isinstance(g, Exception) and g.state == State.SOLVED
                ),
                key=lambda gr: gr.result,
            )
        except ValueError as e:
            if str(e) != "min() arg is an empty sequence":
                raise e
    return res


def find_best(solves: List[Solve]) -> Solve:
    if len(solves) == 0:
        raise ValueError("Tried to find best solve on empty list")
    min_i = min(list(enumerate(solves_to_float(solves))), key=lambda o: o[1])[0]
    return solves[min_i]


def find_worst(solves: List[Solve]) -> Solve:
    if len(solves) == 0:
        raise ValueError("Tried to find worst solve on empty list")
    without_dnfs: List[Tuple[int, float]] = [
        tup for tup in enumerate(solves_to_float(solves)) if tup[1] != inf
    ]
    max_i = max(without_dnfs, key=lambda o: o[1])[0]
    return solves[max_i]

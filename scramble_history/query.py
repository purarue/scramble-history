from typing import Union, List, NamedTuple, Literal, Tuple

from .average_parser import parse_operation_code
from .group_operations import grouped
from .error import unwrap
from .models import Operation, Solve


class Filter(NamedTuple):
    attr: str
    value: str


class Average(NamedTuple):
    operation: Operation
    count_: int


Commands = Literal["dump"]


QueryPart = Union[Filter, Average, Commands]

Query = List[QueryPart]


def parse_query(inputs: Union[str, List[str]]) -> Query:
    raw_tokens = []
    if isinstance(inputs, str):
        raw_tokens.append(inputs)
    else:
        raw_tokens.extend(inputs)

    tokens = []
    for rt in raw_tokens:
        if "___" in rt:
            tokens.extend(rt.split("___"))
        else:
            tokens.append(rt)

    assert isinstance(inputs, list)
    parsed: Query = []
    for token in tokens:
        if "==" in token:
            solve_attr, value = token.split("==", maxsplit=1)
            parsed.append(Filter(solve_attr, value))
            continue

        try:
            op, count = parse_operation_code(token)
            parsed.append(Average(op, count))
            continue
        except ValueError:
            pass

        if token.lower() in {"dump"}:
            parsed.append("dump")
            continue

        raise ValueError(f"Query: not sure how to parse token '{token}'")

    return parsed


QueryRet = Union[Tuple[str, ...], List[Solve]]


def run_query(solves: List[Solve], *, query: Query) -> QueryRet:
    returns: List[str] = []
    for qr in query:
        if isinstance(qr, Filter):
            if len(solves) == 0:
                continue
            assert hasattr(
                solves[0], qr.attr
            ), f"could not find attribute {qr} on {solves[0]}"
            solves = list(filter(lambda solv: getattr(solv, qr.attr) == qr.value, solves))  # type: ignore[arg-type]
        elif isinstance(qr, str):
            assert qr == "dump"
            returns.append("\n".join([s.describe() for s in solves]))
        else:
            assert isinstance(qr, Average)
            g = unwrap(grouped(solves, operation=qr.operation, count=qr.count_))
            returns.append(g.describe())

    if len(returns) == 0:
        return solves

    return tuple(returns)

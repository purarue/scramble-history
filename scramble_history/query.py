import json
from typing import Union, List, NamedTuple, Literal, Tuple, Set

import more_itertools

from .average_parser import parse_operation_code
from .group_operations import grouped, find_best
from .error import unwrap
from .models import Operation, Solve


class Filter(NamedTuple):
    attr: str
    value: str


class FilterIn(NamedTuple):
    attr: str
    values: Set[str]


class Average(NamedTuple):
    operation: Operation
    count_: int


class Drop(NamedTuple):
    count_: int


class Limit(NamedTuple):
    count_: int


class Head(NamedTuple):
    count_: int


class Tail(NamedTuple):
    count_: int


Commands = Literal["dump", "best"]

QueryPart = Union[Filter, FilterIn, Average, Commands, Drop, Limit, Head, Tail]

Query = List[QueryPart]


def _parse_colon_cmd(text: str) -> int:
    return int(text.split(":", maxsplit=1)[-1])


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
        if "?=" in token:
            solve_attr, json_list = token.split("?=", maxsplit=1)
            err = """?= should be used with a JSON list on the right hand side, e.g. 'event_description=?["4x4", "2x2"]'"""
            try:
                data = json.loads(json_list)
            except json.JSONDecodeError as e:
                raise ValueError(f"{err}: {str(e)}")
            assert isinstance(data, list), err
            parsed.append(FilterIn(solve_attr, set(data)))
            continue

        try:
            op, count = parse_operation_code(token)
            parsed.append(Average(op, count))
            continue
        except ValueError:
            pass

        tl = token.lower()
        if tl == "dump":
            parsed.append("dump")
        elif tl == "best":
            parsed.append("best")
        elif tl.startswith("drop:"):
            parsed.append(Drop(_parse_colon_cmd(token)))
        elif tl.startswith("limit:"):
            parsed.append(Limit(_parse_colon_cmd(token)))
        elif tl.startswith("head:") or tl.startswith("first:"):
            parsed.append(Head(_parse_colon_cmd(token)))
        elif tl.startswith("tail:") or tl.startswith("last:"):
            parsed.append(Tail(_parse_colon_cmd(token)))
        else:
            raise ValueError(f"Query: not sure how to parse token '{token}'")

    return parsed


QueryRet = Union[Tuple[str, ...], List[Solve]]


def run_query(solves: List[Solve], *, query: Query) -> QueryRet:
    returns: List[str] = []
    for qr in query:
        if isinstance(qr, (Filter, FilterIn)):
            if len(solves) == 0:
                continue
            assert hasattr(
                solves[0], qr.attr
            ), f"could not find attribute {qr} on {solves[0]}"
            if isinstance(qr, Filter):
                solves = list(filter(lambda solv: getattr(solv, qr.attr) == qr.value, solves))  # type: ignore[arg-type]
            else:
                solves = list(filter(lambda solv: getattr(solv, qr.attr) in qr.values, solves))  # type: ignore[arg-type]
        elif isinstance(qr, Average):
            g = unwrap(grouped(solves, operation=qr.operation, count=qr.count_))
            returns.append(g.describe())
        elif isinstance(qr, Drop):
            solves = solves[qr.count_ :]
        elif isinstance(qr, Limit):
            solves = solves[: qr.count_]
        elif isinstance(qr, Head):
            solves = more_itertools.take(qr.count_, solves)
        elif isinstance(qr, Tail):
            solves = list(more_itertools.tail(qr.count_, solves))
        else:
            if qr == "best":
                returns.append(find_best(solves).describe())
            else:
                assert qr == "dump", str(qr)
                returns.append("\n".join([s.describe() for s in solves]))

    if len(returns) == 0:
        return solves

    return tuple(returns)

from typing import Union, TypeVar

T = TypeVar("T")
E = TypeVar("E", bound=Exception)

ResT = Union[T, E]

Res = ResT[T, Exception]


def unwrap(res: Res[T]) -> T:
    if isinstance(res, Exception):
        raise res
    else:
        return res

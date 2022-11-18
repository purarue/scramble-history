import datetime
from decimal import Decimal

import more_itertools

from scramble_history.models import Solve, State
from scramble_history.group_operations import Solve, grouped, run_operations
from scramble_history.error import unwrap

dnf = Solve(
    puzzle="333",
    event_code="WCA",
    event_description="3x3 CFOP",
    state=State.DNF,
    scramble="B R2 D2 R2 F2 U' F2 D B2 D2 B2 U' B L F R2 B U2 B2 D2",
    comment="",
    time=Decimal("15.254"),
    penalty=Decimal("0"),
    full_time=Decimal("15.254"),
    when=datetime.datetime(2022, 11, 3, 6, 36, 39, tzinfo=datetime.timezone.utc),
)

solves = [
    Solve(
        puzzle="333",
        event_code="WCA",
        event_description="3x3 CFOP",
        state=State.SOLVED,
        scramble="R' U2 D2 R F L2 F2 D F U2 L2 D R2 U' F2 D B2 L2 U2 L2",
        comment="",
        time=Decimal("21.966"),
        full_time=Decimal("21.966"),
        penalty=Decimal("0"),
        when=datetime.datetime(2022, 11, 3, 6, 37, 23, tzinfo=datetime.timezone.utc),
    ),
    Solve(
        puzzle="333",
        event_code="WCA",
        event_description="3x3 CFOP",
        state=State.SOLVED,
        scramble="L U L B' L B2 R2 L B F2 U2 D R2 D L2 F2 L2 U' F2",
        comment="",
        time=Decimal("15.788"),
        full_time=Decimal("15.788"),
        penalty=Decimal("0"),
        when=datetime.datetime(2022, 11, 3, 6, 38, 3, tzinfo=datetime.timezone.utc),
    ),
    Solve(
        puzzle="333",
        event_code="WCA",
        event_description="3x3 CFOP",
        state=State.SOLVED,
        scramble="F2 D' B2 R2 F2 U R2 D2 U' L2 B2 D' F L2 B L' D2 R2 F' D' R'",
        comment="",
        time=Decimal("23.533"),
        full_time=Decimal("23.533"),
        penalty=Decimal("0"),
        when=datetime.datetime(2022, 11, 3, 6, 38, 39, tzinfo=datetime.timezone.utc),
    ),
    Solve(
        puzzle="333",
        event_code="WCA",
        event_description="3x3 CFOP",
        state=State.SOLVED,
        scramble="U2 L F' U2 F U' D' L R2 B2 D2 B' L2 F' L2 F2 D2 R2 D2 L",
        comment="",
        time=Decimal("16.362"),
        full_time=Decimal("18.362"),
        penalty=Decimal("2"),
        when=datetime.datetime(2022, 11, 3, 6, 39, 20, tzinfo=datetime.timezone.utc),
    ),
]

hundred_solves = more_itertools.take(100, more_itertools.ncycles(solves, 50))
hundred_solves[0] = dnf


def test_mean() -> None:
    g = unwrap(grouped([dnf, solves[0], solves[1]], operation="mean"))

    # should assume count = 3
    assert g.solve_count == 3
    assert g.state == State.DNF
    assert g.describe() == "Mo3: DNF = DNF 21.966 15.788"

    g2 = grouped(solves[:3], operation="mean", count=5)
    assert isinstance(g2, ValueError)
    assert "Only have 3 solves, cannot compute mean of 5" == str(g2)

    g3 = unwrap(grouped(solves, operation="mean", count=3))
    assert len(g3.solves) == 3
    assert g3.solve_count == 3
    assert g3.describe() == "Mo3: 20.429 = 21.966 15.788 23.533"
    assert g3.describe_average() == "20.429 = 21.966 15.788 23.533"


def test_average() -> None:
    g = grouped(solves[:2], operation="average", count=1)
    assert isinstance(g, ValueError)
    assert str(g) == "Cannot do operation 'average' with less than 3 solves"

    g2 = grouped(solves[:3], operation="average", count=1)
    assert isinstance(g2, ValueError)
    assert str(g2) == "Cannot do operation 'average' with less than 3 solves"

    g3 = unwrap(grouped(solves[:3], operation="average", count=3))
    assert g3.state == State.SOLVED
    assert g3.solve_count == 3
    assert len(g3.solves) == 3

    doubled = [*solves, *solves]
    assert len(doubled) == 8
    g3 = unwrap(grouped(doubled, operation="average", count=5))
    assert g3.solve_count == 5
    assert len(g3.solves) == 5
    assert g3.result == Decimal("20.764666666666666827723020105622708797454833984375")
    assert g3.describe() == "Ao5: 20.765 = 21.966 21.966 (15.788) (23.533) 18.362"

    g4 = unwrap(grouped([dnf, *solves], operation="average", count=5))
    assert g4.solve_count == 5
    assert len(g4.solves) == 5
    assert g4.state == State.SOLVED
    assert g4.solves == [dnf, *solves]
    assert g4.describe_average() == "21.287 = (DNF) 21.966 (15.788) 23.533 18.362"

    g5 = unwrap(grouped([dnf, dnf, *solves], operation="average", count=5))
    assert g5.state == State.DNF
    assert g5.describe_average() == "DNF = DNF DNF 21.966 15.788 23.533"

    assert len(hundred_solves) == 100
    g6 = unwrap(grouped(hundred_solves, operation="average"))
    assert len(g6.solves) == 100
    assert g6.solve_count == 100
    assert g6.operation_code == "Ao100"
    assert (
        g6.describe()
        == "Ao100: 19.933 = (DNF) 21.966 21.966 21.966 21.966 21.966 21.966 21.966 21.966 21.966 21.966 21.966 21.966 21.966 21.966 21.966 21.966 21.966 21.966 21.966 21.966 21.966 21.966 21.966 21.966 (15.788) 15.788 15.788 15.788 15.788 15.788 15.788 15.788 15.788 15.788 15.788 15.788 15.788 15.788 15.788 15.788 15.788 15.788 15.788 15.788 15.788 15.788 15.788 15.788 15.788 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 23.533 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362 18.362"
    )
    solve_times = [s.time for s in g6.solves if s.state == State.SOLVED]
    min_solve = min(solve_times)
    assert min_solve == Decimal("15.788")


def test_global_mean() -> None:
    g = grouped([dnf], operation="global_mean")
    assert isinstance(g, ValueError)
    assert (
        str(g)
        == "mean requires at least one data point - received no valid solves as input"
    )

    g2 = unwrap(grouped(hundred_solves, operation="global_mean"))
    assert len(g2.solves) == 100
    assert g2.solve_count == 99
    assert g2.result == Decimal("19.891505050505049467801654827781021595001220703125")

    g3 = unwrap(grouped(hundred_solves, operation="global_mean", count=5))
    assert len(g3.solves) == 5
    assert g3.solve_count == 4
    assert (
        g3.describe() == "Global Mean (4/5): 19.912 = DNF 21.966 15.788 23.533 18.362"
    )
    assert g3.operation_code == "Global Mean (4/5)"

    g4 = unwrap(grouped([dnf, dnf, solves[0]], operation="global_mean"))
    assert len(g4.solves) == 3
    assert g4.solve_count == 1
    assert g4.describe() == "Global Mean (1/3): 21.966 = DNF DNF 21.966"


def test_run_operations() -> None:
    ops = run_operations(hundred_solves, operation="average", counts=[5, 12, 50, 100])
    assert ops == {5: "21.287", 12: "20.119", 50: "19.912", 100: "19.933"}

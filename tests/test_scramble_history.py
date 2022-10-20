import itertools
from pathlib import Path

from scramble_history.cstimer import parse_file

tests_dir = Path(__file__).parent.absolute()
cstimer_data = tests_dir / "cstimer_data.txt"
assert cstimer_data.exists()


def test_basic():
    data = list(parse_file(cstimer_data))
    assert len(data) == 17

    all_scrambles = list(itertools.chain(*(sess.solves for sess in data)))
    assert len(all_scrambles) == 23

    dnfs = list(filter(lambda s: s.dnf, all_scrambles))

    penaltys = list(filter(lambda s: s.penalty > 0, all_scrambles))

    assert len(dnfs) == 2
    assert int(dnfs[0].penalty) == 0
    assert len(penaltys) == 2
    assert int(penaltys[0].penalty) == 2

    assert data[0].scramble_type is not None
    assert data[0].scramble_type.name == "3x3x3"

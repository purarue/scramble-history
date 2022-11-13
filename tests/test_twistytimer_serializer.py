import os
import tempfile
import datetime
from decimal import Decimal
from pathlib import Path


from scramble_history import twistytimer


def test_twistytimer_serializer():
    data = [
        """
        "333";"2-GEN";"8000";"1664762422000";"U' R U' R U R2 U' R U R' U2 R' U R' U2 R' U2 R' U R' U2 R2 U' R' U2";"1";""
        """,
        """
        "333";"Roux";"36060";"1666129810202";"D2 F2 L2 B2 U' L2 D2 F2 D B' R D' U2 L2 U2 F2 L' B2 L2 U";"0";""
        """,
        """
        "333";"Roux";"37760";"1666129881408";"R' B2 D2 R B2 R2 D2 B2 R' B F2 D' L F D' B2 L B2 U2 L2";"2";""
        """,
    ]
    assert len(data) == 3
    parsed = [
        twistytimer.Solve(
            puzzle="333",
            category="2-GEN",
            scramble="U' R U' R U R2 U' R U R' U2 R' U R' U2 R' U2 R' U R' U2 R2 U' R' U2",
            time=Decimal("8"),
            penalty=Decimal("2"),
            dnf=False,
            when=datetime.datetime(2022, 10, 3, 2, 0, 22, tzinfo=datetime.timezone.utc),
            comment="",
        ),
        twistytimer.Solve(
            puzzle="333",
            category="Roux",
            scramble="D2 F2 L2 B2 U' L2 D2 F2 D B' R D' U2 L2 U2 F2 L' B2 L2 U",
            time=Decimal("36.06"),
            penalty=Decimal("0"),
            dnf=False,
            when=datetime.datetime(
                2022, 10, 18, 21, 50, 10, 202000, tzinfo=datetime.timezone.utc
            ),
            comment="",
        ),
        twistytimer.Solve(
            puzzle="333",
            category="Roux",
            scramble="R' B2 D2 R B2 R2 D2 B2 R' B F2 D' L F D' B2 L B2 U2 L2",
            time=Decimal("37.76"),
            penalty=Decimal("0"),
            dnf=True,
            when=datetime.datetime(
                2022, 10, 18, 21, 51, 21, 408000, tzinfo=datetime.timezone.utc
            ),
            comment="",
        ),
    ]

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(twistytimer.HEADER)
        f.write("\n")
        for line in data:
            f.write(line.strip())
            f.write("\n")
        f.flush()

        solves = list(twistytimer.parse_file(Path(f.name)))
        assert solves == parsed

        assert (
            Path(f.name).read_text().splitlines()
            == twistytimer.serialize_solves(parsed).splitlines()
        )

    os.unlink(f.name)

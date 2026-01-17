#!/usr/bin/env python3

import os
from typing import NamedTuple, Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime

import click
import autotui.shortcuts

from scramble_history.twistytimer import Solve, serialize_solves
from scramble_history.average_parser import parse_average


class RawComment(NamedTuple):
    is_group: bool
    times: str
    event: str
    scrambles: str
    when: datetime
    method: str | None
    comment: str | None

    @staticmethod
    def attr_use_values() -> dict[str, Any]:
        return {
            "scrambles": lambda: edit_in_vim("scramble"),
            "times": lambda: edit_in_vim("times"),
        }


def edit_in_vim(text: str | None) -> str | None:
    m = click.edit(text=text, editor="nvim")
    return m if m is None else m.strip()


this_dir = os.path.abspath(os.path.dirname(__file__))
manual_solves_file = os.path.join(this_dir, "./manual_solves.json")


@click.command()
@click.argument("CMD", type=click.Choice(["loop", "parse"]))
def main(cmd: str) -> None:
    """
    loop - repeatedly prompts to input data
    parse - parses those into the twistytimer csv export
    """
    if cmd == "loop":
        while True:
            autotui.shortcuts.load_prompt_and_writeback(RawComment, manual_solves_file)
    else:
        parsed: list[Solve] = []
        for m in autotui.shortcuts.load_from(RawComment, manual_solves_file):
            solves = parse_average(m.times)
            scram = [scr.strip() for scr in m.scrambles.splitlines()]
            assert len(solves) >= 1, f"no times {solves} {m}"
            assert len(scram) == len(
                solves
            ), f"solves didn't match scramble length {scram} {solves}"
            if m.is_group:
                assert len(solves) > 1, f"for group {m}, solve length <= 1"
            for _scr, _sl in zip(scram, solves):
                # the scramble/category probably has to be fixed
                # a bit here, but that can be done with a merge
                # at a higher level/cleaned up manually
                parsed.append(
                    Solve(
                        scramble=_scr,
                        puzzle=m.event,
                        category=m.method or "",
                        dnf=_sl == "DNF",
                        time=Decimal("0") if isinstance(_sl, str) else _sl,
                        penalty=Decimal("0"),
                        when=datetime.fromtimestamp(m.when.timestamp()),
                        comment=m.comment.strip() if m.comment is not None else "",
                    )
                )
        click.echo(serialize_solves(parsed), nl=False)


if __name__ == "__main__":
    main()

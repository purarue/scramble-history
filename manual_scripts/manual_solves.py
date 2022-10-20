#!/usr/bin/env python3

from typing import NamedTuple, Optional
from datetime import datetime

import click
import autotui.shortcuts


class RawComment(NamedTuple):
    is_group: bool
    times: str
    event: str
    scrambles: str
    when: datetime
    method: Optional[str]
    comment: str

    @staticmethod
    def attr_use_values() -> dict:
        return {
            "scrambles": lambda: edit_in_vim("scramble"),
            "times": lambda: edit_in_vim("times"),
        }


def edit_in_vim(text: str | None) -> str | None:
    m = click.edit(text=text, editor="nvim")
    return m if m is None else m.strip()


@click.command()
@click.argument("CMD", type=click.Choice(["loop", "parse"]))
def main(cmd: str):
    if cmd == "loop":
        while True:
            print("NEW SOLVE")
            autotui.shortcuts.load_prompt_and_writeback(
                RawComment, "./manual_solves.json"
            )
    else:
        pass


if __name__ == "__main__":
    main()

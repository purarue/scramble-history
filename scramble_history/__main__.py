from pathlib import Path

import click


@click.group()
def main() -> None:
    pass


@main.group()
def parse() -> None:
    """
    Parse the output of some file/directory
    """
    pass


@parse.command()
@click.argument(
    "CSTIMER_FILE",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
def cstimer(cstimer_file: Path) -> None:
    """
    Expects the cstimer.net export file as input
    """
    from .cstimer import parse_file
    import IPython  # type: ignore[import]

    sess = list(parse_file(cstimer_file))  # noqa: F841

    header = f"Use {click.style('sess', fg='green')} to review session data"

    IPython.embed(header=header)


if __name__ == "__main__":
    main(prog_name="scramble_history")

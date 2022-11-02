from pathlib import Path
from typing import Any
from decimal import Decimal

import click


def _default(o: Any) -> Any:
    # orjson doesn't serialize namedtuples to avoid serializing
    # them as tuples (arrays), since they're technically a subclass
    if isinstance(o, Decimal):
        return str(o)
    if hasattr(o, "_asdict"):
        return o._asdict()
    raise TypeError(f"Could not serialize object of type {type(o).__name__}")


def _serialize(data: Any) -> str:
    import orjson  # type: ignore[import]

    bdata: bytes = orjson.dumps(
        data,
        option=orjson.OPT_NON_STR_KEYS,
        default=_default,
    )
    return bdata.decode("utf-8")


JSON = click.option(
    "-j", "--json", "_json", is_flag=True, default=False, help="print data as JSON"
)


@click.group()
def main() -> None:
    """
    parses your rubiks cube scramble history
    """
    pass


@main.group()
def export() -> None:
    """
    Export data from a website
    """


@export.group(name="wca")
def _wca_export() -> None:
    """
    Data from the worldcubeassosiation.org website
    """


@_wca_export.command()
def update() -> None:
    """
    Download/update the local TSV data if its out of date
    """
    from .wca_export import ExportDownloader

    exp = ExportDownloader()
    exp.download_if_out_of_date()


@_wca_export.command()
@click.option(
    "-u", "--wca-user-id", type=str, help="WCA ID to extract results for", required=True
)
@JSON
def extract(_json: bool, wca_user_id: str) -> None:
    """
    Extract details from the local TSV data (must call update first)
    """
    from .wca_export import parse_return_all_details

    details = parse_return_all_details(wca_user_id)
    if _json:
        click.echo(_serialize(details))
    else:
        import IPython  # type: ignore[import]

        header = f"Use {click.style('details', fg='green')} to review TSV data"
        IPython.embed(header=header)


@main.group()
def parse() -> None:
    """
    Parse the output of some file/directory
    """
    pass


@parse.command(short_help="parse cstimer.net export file")
@JSON
@click.argument(
    "CSTIMER_FILE",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
def cstimer(_json: bool, cstimer_file: Path) -> None:
    """
    Expects the cstimer.net export file as input
    """
    from .cstimer import parse_file

    sess = parse_file(cstimer_file)
    if _json:
        click.echo(_serialize(sess))
    else:
        import IPython  # type: ignore[import]

        header = f"Use {click.style('sess', fg='green')} to review session data"
        IPython.embed(header=header)


@parse.command(short_help="parse twistytimer export file")
@click.argument(
    "TWISTYTIMER_FILE",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@JSON
def twistytimer(_json: bool, twistytimer_file: Path) -> None:
    """
    Expects the twistytimer export file as input

    This works for both the cubers.io and twistytimer export
    """
    from .twistytimer import parse_file

    solves = list(parse_file(twistytimer_file))
    if _json:
        click.echo(_serialize(solves))
    else:
        import IPython  # type: ignore[import]

        header = f"Use {click.style('solves', fg='green')} to review your solves"
        IPython.embed(header=header)


if __name__ == "__main__":
    main(prog_name="scramble_history")

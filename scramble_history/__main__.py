from pathlib import Path

import click


@click.group()
def main() -> None:
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
def extract(wca_user_id: str) -> None:
    """
    Extract details from the local TSV data (must call update first)
    """
    from .wca_export import parse_user_details

    parse_user_details(wca_user_id)


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

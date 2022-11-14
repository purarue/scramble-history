import os
import sys
import itertools
from pathlib import Path
from collections import defaultdict
from typing import Any, List, Dict, Sequence, Mapping, Optional
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


@click.group(context_settings={"max_content_width": 110})
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


KNOWN_PARSERS = {"--cstimer", "--twistytimer"}


def _parse_merge_inputs(
    ctx: click.Context, param: click.Argument, value: Sequence[str]
) -> Dict[str, List[Path]]:
    if len(value) < 1:
        raise click.BadArgumentUsage("Must supply some datafiles as input")
    parsed: Mapping[str, List[Path]] = defaultdict(list)
    val = list(value)
    parser: Optional[str] = None
    for p in val:
        if parser is None or p.startswith("--"):
            if p not in KNOWN_PARSERS:
                raise click.BadArgumentUsage(
                    f"Unknown option filetype {p}, should be one of {KNOWN_PARSERS}"
                )
            parser = p
        else:
            pp = Path(p)
            if not pp.exists():
                raise click.BadArgumentUsage(f"Filepath '{pp}' does not exist")
            parsed[parser].append(pp)
    return dict(parsed)


config_dir = Path(os.environ.get("XDG_CONFIG_DIR", Path.home() / ".config"))


@main.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
        max_content_width=110,
    )
)
@click.option(
    "-s",
    "--sourcemap-file",
    help="Configuration/data file which saves choices on how to map solves from different sources",
    default=config_dir / "scramble_history_sourcemap.json",
    show_default=True,
    type=click.Path(dir_okay=False, path_type=Path),
)
@click.option(
    "-a",
    "--action",
    type=click.Choice(["json", "repl", "stats"]),
    help="what to do with merged solves",
    default="repl",
    show_default=True,
)
@click.option(
    "-c",
    "--check",
    help="Dont print/interact, just check that all solves are transformed properly",
    is_flag=True,
    default=False,
)
@click.option(
    "-g",
    "--group-by",
    type=click.Choice(["puzzle", "event_code", "event_description"]),
    help="Group parsed results by key",
    default=None,
)
@click.argument(
    "DATAFILES", nargs=-1, type=click.UNPROCESSED, callback=_parse_merge_inputs
)
def merge(
    sourcemap_file: Path,
    action: str,
    check: bool,
    group_by: Optional[str],
    datafiles: Dict[str, List[Path]],
) -> None:
    """
    merge different data sources together
    """
    from .source_merger import SourceMerger, Solve
    from .cstimer import parse_files as cstimer_merge
    from .twistytimer import parse_files as twistytimer_merge

    merger = SourceMerger(sourcemap_file)

    solves: List[Solve] = []

    for flag, grouped_files in datafiles.items():
        assert flag in KNOWN_PARSERS
        mergefunc = cstimer_merge if flag == "--cstimer" else twistytimer_merge
        slv = list(mergefunc(grouped_files))
        if len(slv) == 0:
            click.echo(
                f"Did not parse any solves from {flag} {grouped_files}, double check to make sure inputs are correct",
                err=True,
            )
            sys.exit(1)
        solves.extend(map(merger.transform, slv))

    if check:
        return

    res: Any = solves
    if group_by is not None or action == "stats":
        if group_by is None:
            click.echo(
                "Passed 'stats' with no '--group_by', grouping by 'event_description'",
                err=True,
            )
            group_by = "event_description"
        key = str(group_by)
        assert hasattr(
            solves[0], key
        ), f"Error: could not find attribute {key} on {solves[0]}"
        solves.sort(key=lambda s: getattr(s, key))  # type: ignore[no-any-return]
        res = {
            k: list(g)
            for k, g in itertools.groupby(solves, key=lambda s: getattr(s, key))  # type: ignore[no-any-return]
        }

    if action == "json":
        click.echo(_serialize(res))
    elif action == "repl":
        import IPython  # type: ignore[import]

        header = f"Use {click.style('res', fg='green')} to review"
        IPython.embed(header=header)
    else:
        from .solve import run_operations, grouped

        click.echo("==============")
        for group_name, group_solves in res.items():
            group_solves.sort(key=lambda s: s.when, reverse=True)
            click.echo(group_name)
            click.echo("==============")
            recent_ao5 = grouped(group_solves, count=5, operation="average")
            desc = (
                "--"
                if isinstance(recent_ao5, Exception)
                else recent_ao5.describe_average()
            )
            click.echo(f"Most recent Ao5 => {desc}")
            click.echo(f"Solve Count => {len(group_solves)}")
            stat_data = run_operations(
                group_solves, operation="average", counts=[5, 12, 50, 100]
            )
            for description in stat_data.values():
                print(description)
            click.echo("==============")


if __name__ == "__main__":
    main(prog_name="scramble_history")

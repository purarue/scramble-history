import sys
import os
import re
import itertools
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, List, Dict, Sequence, Optional
from datetime import datetime
from decimal import Decimal

import click

from .config import (
    parse_config_file,
    ConfigPaths,
    group_args_by_options,
    check_config,
)
from .query import parse_query, run_query, Query


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


config_dir = Path(os.environ.get("XDG_CONFIG_DIR", Path.home() / ".config"))
scramble_history_config_dir = Path(
    os.environ.get("SCRAMBLE_HISTORY_CONFIG_DIR", config_dir / "scramble_history")
)
if not scramble_history_config_dir.exists():
    scramble_history_config_dir.mkdir(parents=True)


# this needs to be a global path that user cant modify in click option
# so _parse_merge_inputs can access it
config_file = scramble_history_config_dir / "files.yaml"


def _parse_merge_inputs(
    ctx: click.Context, param: click.Argument, value: Sequence[str]
) -> ConfigPaths:
    conf = {}
    if config_file.exists():
        conf = parse_config_file(config_file)

    if len(value) < 1 and len(conf) == 0:
        raise click.BadArgumentUsage(
            f"Must supply options/datafiles as input or create a config file at {config_file}"
        )
    try:
        # merge any options into dictionary if supplied in addition to config file
        for k, v in group_args_by_options(list(value)).items():
            conf[k] = conf.get(k, []) + v
    except ValueError as e:
        raise click.BadArgumentUsage(str(e))

    check_config(conf)
    return conf


def _parse_query(
    ctx: click.Context,
    param: click.Argument,
    value: Sequence[str],
) -> Query:
    return parse_query(list(value))


def banner() -> None:
    click.echo("===================")


KITTY_PATH = shutil.which("kitty")


def _print_kitty_images(imgs: List[str]) -> bool:
    if os.environ.get("TERM") != "xterm-kitty":
        return False
    printed = False
    assert KITTY_PATH is not None, "could not find kitty on your path"
    for img in imgs:
        subprocess.run([KITTY_PATH, "icat", "--align=left", str(img)])
        printed = True
    return printed


@main.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
        max_content_width=110,
    ),
    short_help="merge solves together",
)
@click.option(
    "-s",
    "--sourcemap-file",
    help="Data file which saves choices on how to map solves from different sources",
    default=scramble_history_config_dir / "sourcemap.json",
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
    "-C",
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
@click.option(
    "-G", "--graph", is_flag=True, help="graph grouped results", default=False
)
@click.option(
    "-O",
    "--graph-opt",
    default=(),
    multiple=True,
    type=click.Choice(
        ["show", "save", "date-axis", "kitty-print", "annotate", "annotate-average"]
    ),
    help="graph options",
)
@click.option(
    "-q",
    "--query",
    type=click.UNPROCESSED,
    default=(),
    multiple=True,
    callback=_parse_query,
    help="Solves to filter to, or actions to run",
)
@click.option(
    "-s",
    "--sort-by",
    type=click.Choice(["when"]),
    default="when",
    help="Sort the resulting solves",
)
@click.option(
    "-r",
    "--reverse/--no-reverse",
    "_reverse_flag",
    is_flag=True,
    default=None,
    help="Reverse the sort for --sort-by. Default is --no-reverse, stats uses --reverse",
)
@click.argument(
    "DATAFILES",
    type=click.UNPROCESSED,
    callback=_parse_merge_inputs,
    default=(),
)
def merge(
    sourcemap_file: Path,
    action: str,
    graph: bool,
    graph_opt: Sequence[str],
    check: bool,
    sort_by: Optional[str],
    _reverse_flag: Optional[bool],
    query: Optional[Query],
    group_by: Optional[str],
    datafiles: Dict[str, List[Path]],
) -> None:
    """
    merge solves from different data sources together

    To provide input, either define a config file, or pass paths like:

    \b
    --cstimer ~/Downloads/cstimer.json
    --twistytimer ~/Downloads/*twistytimer*.txt
    """
    from .source_merger import merge as merge_solves

    solves = list(merge_solves(sourcemap_file=sourcemap_file, conf=datafiles))

    if check:
        return

    # default to False, unless user provided the flag
    reverse: bool = False
    if _reverse_flag is None:
        # default to --reverse in stats since user probably
        # wants to see their most recent solves
        reverse = action == "stats"
    else:
        reverse = _reverse_flag

    if sort_by == "when":
        solves.sort(key=lambda s: s.when, reverse=reverse)

    if query:
        data = run_query(solves, query=query)
        # if these were not just a Filter and this modified
        # the shape/ran something, we should show that
        if isinstance(data, tuple):
            for resp in data:
                print(resp)
            return
        else:
            # we just filtered, so set the solves to what the query returned
            solves = data

    if graph and action != "stats":
        action = "stats"

    res: Any = solves
    if (group_by is not None or action == "stats" or graph) and isinstance(res, list):
        if group_by is None:
            click.echo(
                "Passed 'stats' with no '--group_by', grouping by 'event_description'",
                err=True,
            )
            group_by = "event_description"
        key = str(group_by)
        if len(solves) == 0:
            click.echo("Solve list is empty!", err=True)
            sys.exit(1)
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
        from .group_operations import (
            run_operations,
            grouped,
            find_best_group,
            operation_code,
            find_best,
            find_worst,
        )
        from .error import unwrap
        from .timeformat import format_decimal
        from tabulate import tabulate

        # order by number of solves in the group
        by_solve_count = sorted(
            [(gn, len(gs)) for gn, gs in res.items()],
            key=lambda k: k[1],
            reverse=True,
        )
        for group_name, _ in by_solve_count:
            group_solves = res[group_name]
            group_solves.sort(key=lambda s: s.when, reverse=reverse)
            banner()
            click.echo(group_name)
            banner()
            recent_ao5 = grouped(group_solves, count=5, operation="average")
            desc = (
                "--"
                if isinstance(recent_ao5, Exception)
                else recent_ao5.describe_average()
            )
            best_solve = find_best(group_solves).describe()
            worst_solve = find_worst(group_solves).describe()
            global_mean = unwrap(grouped(group_solves, operation="global_mean"))
            assert global_mean.solve_count is not None
            global_mean_desc = operation_code(
                "global_mean", global_mean.solve_count, len(global_mean.solves)
            )
            click.echo(f"Best => {best_solve}")
            click.echo(f"Worst => {worst_solve}")
            click.echo(f"Most recent Ao5 => {desc}")
            click.echo(f"{global_mean_desc} => {format_decimal(global_mean.result)}")
            click.echo(f"Solve Count => {len(group_solves)}")
            stat_data = run_operations(
                group_solves, operation="average", counts=[5, 12, 50, 100]
            )
            best = find_best_group(
                group_solves, operation="average", counts=[5, 12, 50, 100]
            )
            click.echo()
            click.echo(
                tabulate(
                    [
                        [
                            operation_code("average", count_, count_),
                            stat_data[count_],
                            format_decimal(best[count_].result)
                            if count_ in best
                            else "--",
                        ]
                        for count_ in stat_data.keys()
                    ],
                    headers=(group_name, "Current", "Best"),
                )
            )
            if graph:
                import seaborn as sns  # type: ignore[import]
                import matplotlib.pyplot as plt  # type: ignore[import]
                import pandas as pd  # type: ignore[import]

                from dataclasses import asdict
                from .models import State

                # if user didnt specify, sort with oldest solves first
                # (otherwise by default stats would print graphs going
                # backwards, with your most recent solve at the left)
                if _reverse_flag is None:
                    group_solves.sort(key=lambda s: s.when)

                text = ""
                if "annotate" in graph_opt:
                    text += f"Best: {best_solve}\n"
                    text += f"Worst: {worst_solve}\n"
                    text += f"Count: {len(group_solves)}\n"

                pd_input = pd.json_normalize(
                    list(
                        dict(list(asdict(solve).items()) + list({"solve": i}.items()))
                        for i, solve in enumerate(group_solves)
                        if solve.state == State.SOLVED
                    )
                )
                filename = re.sub(
                    r"[\?:\s\/\\]",
                    r"_",
                    f"{group_name}-{len(group_solves)}-{datetime.now().replace(microsecond=0)}.png",
                )
                _, ax = plt.subplots()
                sns.lineplot(
                    pd_input,
                    x="when" if "date-axis" in graph_opt else "solve",
                    y="full_time",
                    ax=ax,
                )
                plt.xlabel("solve date" if "date-axis" in graph_opt else "solve #")
                plt.ylabel("solve time")
                ticks, _ = plt.yticks()
                plt.yticks(ticks=ticks, labels=[format_decimal(t) for t in ticks])

                textbox_props = dict(boxstyle="round", facecolor="lightblue", alpha=0.5)
                if "annotate" in graph_opt:
                    plt.annotate(
                        text.strip(),
                        xy=(0.05, 0.95),
                        xycoords="axes fraction",
                        fontsize=14,
                        verticalalignment="top",
                        bbox=textbox_props,
                        color="black",
                        horizontalalignment="left",
                    )
                if "annotate-average" in graph_opt:
                    average = unwrap(grouped(solves, operation="average")).describe()
                    plt.annotate(
                        average,
                        xy=(0.05, 0.05),
                        xycoords="axes fraction",
                        fontsize=10,
                        verticalalignment="bottom",
                        bbox=textbox_props,
                        color="black",
                        horizontalalignment="left",
                    )
                plt.title(group_name)
                if "kitty-print" in graph_opt or "save" in graph_opt:
                    # print using icat for the kitty terminal
                    if "save" in graph_opt:
                        click.echo(f"Saving to {filename}", err=True)
                        plt.savefig(filename, format="png")
                    else:
                        with tempfile.TemporaryDirectory() as td:
                            target = os.path.join(td, filename)
                            plt.savefig(target, format="png")
                            _print_kitty_images([target])
                else:
                    plt.show()
                plt.clf()
                plt.cla()
                plt.close()


if __name__ == "__main__":
    main(prog_name="scramble_history")

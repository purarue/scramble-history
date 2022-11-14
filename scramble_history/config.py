import io
import warnings
from pathlib import Path
from glob import glob as do_glob
from collections import defaultdict
from typing import Iterable, List, Union, Optional, Dict, Mapping

PathIsh = Union[Path, str]
Paths = Union[PathIsh, List[PathIsh]]


DEFAULT_GLOB = "*"


# Modified from: https://github.com/karlicoss/HPI
def get_files(
    pp: Paths,
    glob: str = DEFAULT_GLOB,
) -> List[Path]:
    sources: List[Path]
    if isinstance(pp, Path):
        sources = [pp]
    elif isinstance(pp, str):
        sources = [Path(pp)]
    else:
        assert isinstance(
            pp, list
        ), f"Input should either be a Path, string or list of paths, found {type(pp)}"
        sources = [Path(p) for p in pp]

    paths: List[Path] = []
    for src in sources:
        if src.parts[0] == "~":
            src = src.expanduser()
        # note: glob handled first, because e.g. on Windows asterisk makes is_dir unhappy
        gs = str(src)
        if "*" in gs:
            if glob != DEFAULT_GLOB:
                warnings.warn(
                    f"treating {gs} as glob path. Explicit glob={glob} argument is ignored!"
                )
            paths.extend(map(Path, do_glob(gs)))
        elif src.is_dir():
            gp: Iterable[Path] = src.glob(glob)
            paths.extend(gp)
        else:
            if not src.is_file():
                # todo not sure, might be race condition?
                raise RuntimeError(f"Expected '{src}' to exist")
            paths.append(src)

    return paths


ConfigPaths = Dict[str, List[Path]]


def parse_config_file(file: Path) -> Dict[str, List[Path]]:
    return parse_config(file.read_text())


def parse_config(data: str) -> Dict[str, List[Path]]:
    import yaml

    buf = io.StringIO(data)
    loaded = yaml.load(buf, Loader=yaml.FullLoader)
    res: ConfigPaths = {}
    for k, v in loaded.items():
        res[k] = get_files(v)
    return res


KNOWN_PARSERS = {"cstimer", "twistytimer"}


# used in the CLI to parse unprocessed arguments
def group_args_by_options(args: List[str]) -> ConfigPaths:
    parser: Optional[str] = None
    parsed: Mapping[str, List[Path]] = defaultdict(list)
    for p in args:
        if parser is None or p.startswith("--"):
            parser = p.strip().strip("-")
        else:
            pp = Path(p)
            if not pp.exists():
                raise ValueError(f"Filepath '{pp}' does not exist")
            parsed[parser].append(pp)
    return dict(parsed)


def check_config(conf: ConfigPaths) -> None:
    for k in conf:
        if k not in KNOWN_PARSERS:
            raise ValueError(f"Could not find {k} in known sources: {KNOWN_PARSERS}")

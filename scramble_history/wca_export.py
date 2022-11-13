import shutil
import tempfile
import zipfile
import csv
from typing import (
    Dict,
    Optional,
    List,
    cast,
    Iterator,
    Set,
    Tuple,
    NamedTuple,
    TypeVar,
    Type,
)
from dataclasses import dataclass
from collections import defaultdict
from pathlib import Path
from functools import lru_cache

import requests
import platformdirs

from .log import logger


def cachedir() -> Path:
    return Path(platformdirs.user_cache_dir("wca_export"))


class ExportDownloader:
    def __init__(self) -> None:
        self.cache_dir = cachedir()
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)
        self.cache_tsv_dir = self.cache_dir / "tsv"
        self.database_name = "Scores"
        self.export_data_url = (
            "https://www.worldcubeassociation.org/api/v0/export/public"
        )

    @lru_cache(maxsize=1)
    def export_links(self) -> Dict[str, str]:
        req = requests.get(self.export_data_url)
        req.raise_for_status()
        data = req.json()
        assert isinstance(data, dict)
        return cast(Dict[str, str], data)

    @property
    def export_date_path(self) -> Path:
        return self.cache_dir / "export_date.txt"

    def export_date(self) -> Optional[str]:
        if self.export_date_path.exists():
            return self.export_date_path.read_text().strip()
        else:
            return None

    def update_date(self) -> None:
        self.export_date_path.write_text(self.export_links()["export_date"].strip())

    def export_out_of_date(self) -> bool:
        exp_date = self.export_date()
        if exp_date is None:
            return True
        current_date = self.export_links()["export_date"].strip()
        if current_date == exp_date:
            return False
        return True

    def download_export(self) -> None:
        tsv_url = self.export_links()["tsv_url"]
        assert "WCA_export" in tsv_url
        with tempfile.TemporaryDirectory() as td:
            ptd = Path(td)
            assert ptd.exists()
            logger.info("Downloading TSV export...")
            r = requests.get(tsv_url, stream=True)
            assert (
                r.status_code == 200
            ), "Failed to create connection to download TSV export"
            write_to = ptd / "export.zip"
            with open(write_to, "wb") as f:
                for chunk in r:
                    f.write(chunk)

            zip_extract_to = ptd / "archive"

            with zipfile.ZipFile(write_to, "r") as zip_r:
                zip_r.extractall(str(zip_extract_to))

            shutil.copytree(zip_extract_to, self.cache_tsv_dir, dirs_exist_ok=True)
            logger.info(f"Saved TSV export to {self.cache_tsv_dir}")

    def download_if_out_of_date(self) -> None:
        if self.export_out_of_date():
            self.download_export()
            self.update_date()
        else:
            logger.info("Export is already up to date")


TSV = List[str]


def _extract_records(wca_user_id: str, results_file: str) -> Iterator[TSV]:
    with open(results_file, "r", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for line in reader:
            if line[7] == wca_user_id:
                yield line


T = TypeVar("T")


# splat a TSV row onto a namedtuple, handling extra fields if missing
def row_to_type(data: List[str], nt: Type[T]) -> T:
    assert hasattr(nt, "_fields")
    fields: Tuple[str] = cast(Tuple[str], getattr(nt, "_fields"))
    assert isinstance(fields, tuple)
    while len(data) < len(fields):
        data.append("")
    assert len(data) == len(
        fields
    ), f"{data} has too many fields, tried to construct {nt.__name__} {fields}"
    return nt(*data)


class WCA_Result(NamedTuple):
    competitionId: str
    eventId: str
    roundTypeId: str
    pos: str
    best: str
    average: str
    personName: str
    personId: str
    personCountryId: str
    formatId: str
    value1: str
    value2: str
    value3: str
    value4: str
    value5: str
    regionalSingleRecord: str
    regionalAverageRecord: str

    @classmethod
    def parse(cls, data: List[str]) -> "WCA_Result":
        return row_to_type(data, cls)


class WCA_Scramble(NamedTuple):
    scrambleId: str
    competitionId: str
    eventId: str
    roundTypeId: str
    groupId: str
    isExtra: str
    scrambleNum: str
    scramble: str

    @classmethod
    def parse(cls, data: List[str]) -> "WCA_Scramble":
        return row_to_type(data, cls)


def _extract_scrambles_for_competitions(
    competitions_file: str, competitions: Set[str]
) -> Iterator[TSV]:
    with open(competitions_file, "r", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for line in reader:
            if line[1] in competitions:
                yield line


def _match_records_and_scrambles(
    records: List[WCA_Result], scrambles: List[WCA_Scramble]
) -> Iterator[Tuple[WCA_Result, List[WCA_Scramble]]]:
    results_scramble_map: Dict[WCA_Result, List[WCA_Scramble]] = defaultdict(list)
    for record in records:
        for scramble in scrambles:
            if (
                record.competitionId == scramble.competitionId
                and record.eventId == scramble.eventId
                and record.roundTypeId == scramble.roundTypeId
            ):
                results_scramble_map[record].append(scramble)
        if len(results_scramble_map) == 0:
            logger.warning(f"Could not find any scrambles for {record}")
    yield from results_scramble_map.items()


class WCA_Competition(NamedTuple):
    id: str
    name: str
    cityName: str
    countryId: str
    information: str
    year: str
    month: str
    day: str
    endMonth: str
    endDay: str
    cancelled: str
    eventSpecs: str
    wcaDelegate: str
    organiser: str
    venue: str
    venueAddress: str
    venueDetails: str
    external_website: str
    cellName: str
    latitude: str
    longitude: str

    @classmethod
    def parse(cls, data: List[str]) -> "WCA_Competition":
        return row_to_type(data, cls)


def _competition_data(competition_file: str, competitions: Set[str]) -> Iterator[TSV]:
    with open(competition_file, "r", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        for line in reader:
            if line[0] in competitions:
                yield line


@dataclass
class Details:
    competition_data: List[WCA_Competition]
    results_w_scrambles: List[Tuple[WCA_Result, List[WCA_Scramble]]]


def parse_return_all_details(wca_user_id: str) -> Details:
    exp = ExportDownloader()
    src = exp.cache_tsv_dir
    records = [
        WCA_Result.parse(row)
        for row in _extract_records(wca_user_id, str(src / "WCA_export_Results.tsv"))
    ]
    # all competitions user has been to
    competitions = {r.competitionId for r in records}
    # all scrambles from any competition user has been to
    comp_scrambles = [
        WCA_Scramble.parse(scr)
        for scr in _extract_scrambles_for_competitions(
            str(src / "WCA_export_Scrambles.tsv"), competitions
        )
    ]
    # match records/scrambles
    # TODO: need to find the group that user was in to match to their scrambles?
    results_w_scrambles = list(_match_records_and_scrambles(records, comp_scrambles))
    comp_data = [
        WCA_Competition.parse(c)
        for c in _competition_data(
            str(src / "WCA_export_Competitions.tsv"), competitions
        )
    ]

    return Details(competition_data=comp_data, results_w_scrambles=results_w_scrambles)

import shutil
import tempfile
import zipfile
import csv
from typing import Dict, Optional, List, cast
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
        assert isinstance(dict, data)
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


def _extract_records(wca_user_id: str, results_file: str) -> List[TSV]:
    results: List[List[str]] = []
    with open(results_file, "r", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        for line in reader:
            if line[7] == wca_user_id:
                results.append(line)
    return results


# WIP
def parse_user_details(wca_user_id: str) -> None:
    exp = ExportDownloader()
    src = exp.cache_tsv_dir
    _extract_records(wca_user_id, str(src / "WCA_export_Results.tsv"))
    # see 'value' rows here for what these mean
    # https://www.worldcubeassociation.org/results/misc/export.html
    #
    # need to extract dates/location info from export_Competitions
    # and Scrambles from WCA_export_Scrambles by matching the records
    breakpoint()

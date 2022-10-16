import os
import logging
from typing import Optional

from logzero import setup_logger  # type: ignore[import]

DEFAULT_LEVEL = logging.INFO


def setup(level: Optional[int] = None) -> logging.Logger:
    chosen_level = level or int(os.environ.get("SCRAMBLE_HISTORY_LOGS", DEFAULT_LEVEL))
    lgr: logging.Logger = setup_logger(name=__package__, level=chosen_level)
    return lgr


logger = setup()

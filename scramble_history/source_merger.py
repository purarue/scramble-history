"""
solves from different sources have to be manually mapped/confirmed
from source combinations (tagged with the source name)
to a shared categorization system
"""

import json
import pprint
from decimal import Decimal
from datetime import datetime
from pathlib import Path
from typing import NamedTuple, Optional, Any, Dict, List

from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.validation import Validator, ValidationError

from .state import State


class Solve(NamedTuple):
    # cstimer: scramble code/manual edit
    # twistytimer: puzzle
    # e.g. 333, 444, 222, pyra, skewb, megaminx
    puzzle: str

    # cstimer scramble code
    # twistytimer category/manually edit
    # What this is: e.g. OH, BLD, LSE, F2L
    event_code: str

    # cstimer CSTimerScramble.name
    # twistytimer category/manually edit
    event_description: str

    # if the cube is solved or not
    state: State
    # standard user-facing stuff here
    scramble: str
    comment: Optional[str]
    time: Decimal
    penalty: Decimal
    when: datetime


class SourceMap(NamedTuple):
    # the name of the class, e.g. scramble_history.cstimer, scramble_history.twistytimer
    source_class_name: str

    # these are the fields on the source solve/session
    # that have to match for this transform to be applied
    # as an example using twistytimer:
    # {
    #     "puzzle": "333",
    #     "category": "Normal"
    # }
    #
    # since the 'category'/session name is just a user defined string, user has
    # to be prompted to make sure multiple sources can be merged
    source_fields_match: Dict[str, Any]

    # the normalized fields to use if source_fields_match match
    transformed_puzzle: str
    transformed_event_code: str
    transformed_event_description: str


class HasattrValidator(Validator):
    def __init__(self, check_obj: Any) -> None:
        super().__init__()
        self.check_obj = check_obj

    def validate(self, document: Document) -> None:
        text = document.text

        for key in text.strip().split():
            if not hasattr(self.check_obj, key):
                raise ValidationError(
                    message=f"Could not find key {key} on {self.check_obj}"
                )


class SourceMerger:
    def __init__(self, sourcemap_file: Path) -> None:
        self.sourcemap_file = sourcemap_file
        self.sourcemap: List[SourceMap] = []
        self.load()

    def load(self) -> None:
        if self.sourcemap_file.exists():
            self.sourcemap = self.sourcemap_loads(self.sourcemap_file.read_text())

    def dump(self) -> None:
        self.sourcemap_file.write_text(self.sourcemap_dumps(self.sourcemap))

    @staticmethod
    def sourcemap_loads(json_data: str) -> List[SourceMap]:
        data = json.loads(json_data)
        assert isinstance(data, list)
        return [SourceMap(**kw) for kw in data]

    @staticmethod
    def sourcemap_dumps(sm: List[SourceMap]) -> str:
        return json.dumps([d._asdict() for d in sm], indent=4)

    @classmethod
    def _select_keys(cls, data: Any) -> List[str]:
        validator = HasattrValidator(data)
        text = prompt(
            "Which keys (e.g. puzzle, name) should be used to identify solves like this\nIf needed, enter multiple keys, separated by spaces, e.g. 'scramble_code name': ",
            validator=validator,
        )
        return text.strip().split()

    def _create_validator(
        self, key: str, defaults: Dict[str, Any]
    ) -> FuzzyWordCompleter:
        tokens = [getattr(s, key) for s in self.sourcemap]
        if defaults.get(key):
            tokens.append(defaults[key])
        return FuzzyWordCompleter(list(set(tokens)))

    def prompt_for_transform(self, data: Any) -> SourceMap:
        pprint.pprint(data)
        keys = self._select_keys(data)
        source_fields_match = {k: getattr(data, k) for k in keys}

        defaults = getattr(data, "_prompt_defaults", {})

        transformed_puzzle = prompt(
            "Transformed value for 'puzzle' (e.g. 333, 222, 444, pyra, skewb): ",
            completer=self._create_validator("transformed_puzzle", defaults),
        )

        transformed_event_code = prompt(
            "Transformed value for 'event_code' (e.g. WCA ('normal solving'), LSE, F2L, BLD, OH): ",
            completer=self._create_validator("transformed_event_code", defaults),
        )

        transformed_event_description = prompt(
            "Transformed value for 'event_description (e.g. '3x3 CFOP', 'OH Roux', 'Cross Practice'): ",
            completer=self._create_validator("transformed_event_description", defaults),
        )

        sm = SourceMap(
            source_class_name=self._qualclassname(data),
            source_fields_match=source_fields_match,
            transformed_puzzle=transformed_puzzle,
            transformed_event_code=transformed_event_code,
            transformed_event_description=transformed_event_description,
        )
        self.sourcemap.append(sm)
        self.dump()
        return sm

    @staticmethod
    def _qualclassname(solve: Any) -> str:
        return f"{solve.__module__}.{solve.__class__.__name__}"

    def match_sourcemap(self, solve: Any) -> Optional[SourceMap]:
        for s in self.sourcemap:
            if s.source_class_name != self._qualclassname(solve):
                continue
            if all(
                hasattr(solve, k) and getattr(solve, k) == v
                for k, v in s.source_fields_match.items()
            ):
                return s
        return None

    def match_or_prompt(self, solve: Any) -> SourceMap:
        return self.match_sourcemap(solve) or self.prompt_for_transform(solve)

    def transform(self, solve: Any, sourcemap: Optional[SourceMap] = None) -> Solve:
        if sourcemap is None:
            sourcemap = self.match_or_prompt(solve)
        transformed_data = solve._transform_map()
        return Solve(
            puzzle=sourcemap.transformed_puzzle,
            event_code=sourcemap.transformed_event_code,
            event_description=sourcemap.transformed_event_description,
            **transformed_data,
        )
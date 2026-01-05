"""Common JSON helpers for smufl-mapping tooling."""

from __future__ import annotations

import json
from collections import OrderedDict
from typing import Iterable, Tuple, Any


class DuplicateKeyError(ValueError):
    """Raised when a JSON object contains the same key more than once."""

    def __init__(self, location: str, key: str):
        super().__init__(f"{location}: duplicate key '{key}'")
        self.location = location
        self.key = key


def _unique_object_pairs_hook(location: str):
    def hook(pairs: Iterable[Tuple[str, Any]]):
        obj = OrderedDict()
        for key, value in pairs:
            if key in obj:
                raise DuplicateKeyError(location, key)
            obj[key] = value
        return obj

    return hook


def load_json_strict(handle, *, location: str = "JSON document"):
    """Load JSON while rejecting duplicate keys at any object depth."""

    return json.load(handle, object_pairs_hook=_unique_object_pairs_hook(location))

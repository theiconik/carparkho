"""Catalog port: load the car list from a backing store (JSON today, DB/HTTP later)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class CarCatalogRepository(Protocol):
    def load_cars(self) -> list[dict]:
        """Return raw car records (same shape as cars-dataset.json entries)."""
        ...


class JsonCarCatalogRepository:
    def __init__(self, path: Path) -> None:
        self._path = path

    def load_cars(self) -> list[dict]:
        data = json.loads(self._path.read_text(encoding="utf-8"))
        return data["cars"]

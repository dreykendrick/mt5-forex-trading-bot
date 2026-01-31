from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass
class TradeJournal:
    path: Path

    def __post_init__(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            with self.path.open("w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=[
                    "time",
                    "symbol",
                    "direction",
                    "volume",
                    "price",
                    "sl",
                    "tp",
                    "ticket",
                    "comment",
                ])
                writer.writeheader()

    def append(self, row: Dict[str, str | float | int]) -> None:
        with self.path.open("a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=row.keys())
            writer.writerow(row)

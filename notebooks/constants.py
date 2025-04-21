"""
Constants
"""

from __future__ import annotations

from pathlib import Path

SCENARIO_INPUT_PATH: Path = Path("example-input.csv")
"""
Path to your input file
"""

RUN_ID: str = "0001"
"""
A basic ID

Change this as you wish to keep track of different runs,
checks etc.
"""


INDEX_COLUMS: list[str] = ["model", "scenario", "variable", "region", "unit"]
"""
The list of columns to use as the index for data by default
"""

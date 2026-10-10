"""Read and write view parameter files (JSON)."""

import json
import os
from typing import Any, Union

PathLike = Union[str, "os.PathLike[str]"]
JSON_INDENT = 4


def write_parameters(path: PathLike, parameters: dict[str, Any]) -> None:
    """Write view parameters to a JSON file.

    Args:
        path: Destination file.
        parameters: Parameters produced by ``capture_view_parameters``.
    """
    with open(path, "w", encoding="utf-8") as file:
        json.dump(parameters, file, indent=JSON_INDENT)


def read_parameters(path: PathLike) -> dict[str, Any]:
    """Read view parameters from a JSON file.

    Args:
        path: Source file.

    Returns:
        The decoded parameters.
    """
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

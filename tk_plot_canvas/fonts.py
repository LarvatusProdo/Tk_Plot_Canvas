"""Font helpers shared by the canvas and the font dialogs.

Tk font specifications are strings such as ``"Arial 10 bold"`` or
``"{DejaVu Sans} 10 bold"`` (braces protect family names containing spaces).
"""

import platform
import re
from typing import Iterable, Optional

from .config import (
    FALLBACK_FONT_SIZE,
    FALLBACK_FONT_WEIGHT,
    LINUX_DEFAULT_FONT,
    LINUX_SYSTEM_NAME,
    OTHER_DEFAULT_FONT,
)

_BRACED_FAMILY = re.compile(r"^\{(?P<family>[^}]*)\}\s*(?P<rest>.*)$")


def is_linux() -> bool:
    """Tell whether the current operating system is Linux.

    Returns:
        True on Linux, False otherwise.
    """
    return platform.system() == LINUX_SYSTEM_NAME


def default_font_name() -> str:
    """Return the default UI font family for the current operating system.

    Returns:
        "DejaVu Sans" on Linux, "Arial" elsewhere.
    """
    return LINUX_DEFAULT_FONT if is_linux() else OTHER_DEFAULT_FONT


def split_tk_font_spec(spec: str) -> Optional[list[str]]:
    """Split a Tk font specification into its parts.

    Args:
        spec: Font specification, e.g. "Arial 10 bold" or "{Arial Greek} 14 bold".

    Returns:
        ``[family, size, *options]`` with an integer-like size, or None when
        the specification cannot be parsed.
    """
    parts = spec.split(" ")
    if _has_integer_size(parts):
        return parts
    match = _BRACED_FAMILY.match(spec)
    if match:
        parts = [match.group("family")] + match.group("rest").split(" ")
        if _has_integer_size(parts):
            return parts
    return None


def parse_tk_font_spec(spec: str, fallback_family: str) -> list[str]:
    """Parse a Tk font specification, falling back to safe defaults.

    Args:
        spec: Font specification to parse.
        fallback_family: Family used when the specification is invalid.

    Returns:
        ``[family, size, *options]``.
    """
    parts = split_tk_font_spec(spec)
    if parts is None:
        return [fallback_family, FALLBACK_FONT_SIZE, FALLBACK_FONT_WEIGHT]
    return parts


def safe_tk_font_spec(spec: str, default_family: str, available_families: Iterable[str]) -> str:
    """Return a font specification whose family exists on this system.

    Args:
        spec: Font specification read from a saved view.
        default_family: Family used when the requested one is unavailable.
        available_families: Font families known by Tk.

    Returns:
        A font specification that Tk can render.
    """
    parts = parse_tk_font_spec(spec, default_family)
    if parts[0] not in available_families:
        parts[0] = default_family
    if not parts[0].startswith("{") and is_linux():
        parts[0] = "{" + parts[0] + "}"
    return " ".join(parts)


def _has_integer_size(parts: list[str]) -> bool:
    """Tell whether the second part of a split font spec is an integer size.

    Args:
        parts: Font specification split into words.

    Returns:
        True when ``parts[1]`` exists and ``int(parts[1])`` succeeds.
    """
    if len(parts) < 2:
        return False
    try:
        int(parts[1])
    except ValueError:
        return False
    return True

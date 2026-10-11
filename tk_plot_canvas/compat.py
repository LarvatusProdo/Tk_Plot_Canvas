"""Compatibility helpers between Matplotlib versions and Tkinter."""

from typing import Any

import matplotlib
from matplotlib.colors import Colormap, to_hex


def to_tk_color(color: Any) -> str:
    """Convert a Matplotlib color into a value accepted by Tk widgets.

    Matplotlib may return colors as RGBA tuples, which Tk does not understand.
    String colors are returned unchanged.

    Args:
        color: Matplotlib color (name, hex string or RGB(A) tuple).

    Returns:
        A Tk-compatible color string.
    """
    if isinstance(color, str):
        return color
    return to_hex(color)


def get_colormap(name: str) -> Colormap:
    """Return a registered Matplotlib colormap by name.

    Args:
        name: Colormap name, e.g. "viridis".

    Returns:
        The colormap instance.
    """
    return matplotlib.colormaps[name]


def colormap_names() -> list[str]:
    """List the non-reversed colormaps, sorted case-insensitively.

    Returns:
        Sorted colormap names without the "_r" variants.
    """
    names = [name for name in matplotlib.colormaps if not name.endswith("_r")]
    return sorted(names, key=str.lower)

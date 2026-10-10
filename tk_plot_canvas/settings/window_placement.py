"""Placement of secondary windows relative to their parent window."""

import tkinter as tk

from ..config import DIALOG_OFFSET


def place_window(
    window: tk.Toplevel, reference: tk.Misc, size: str, offset: tuple[int, int] = DIALOG_OFFSET
) -> None:
    """Size a window and place it at an offset from a reference window.

    Args:
        window: Window to place.
        reference: Window whose top-left corner is the origin.
        size: Tk size, e.g. "400x450".
        offset: ``(x, y)`` offset in pixels from the reference corner.
    """
    offset_x, offset_y = offset
    window.geometry(f"{size}+{reference.winfo_x() + offset_x}+{reference.winfo_y() + offset_y}")

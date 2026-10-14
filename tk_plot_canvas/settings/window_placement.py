"""Placement and common behavior of secondary windows."""

import tkinter as tk
from typing import Callable, Optional

from ..config import DIALOG_OFFSET
from ..dpi import ui_scale

CLOSE_KEY = "<Escape>"


def scaled_size(widget: tk.Misc, size: str) -> str:
    """Scale a Tk size given for a 100 % screen to the current screen scale.

    Args:
        widget: Any widget of the application.
        size: Tk size at 100 %, e.g. "400x450".

    Returns:
        The scaled size, e.g. "600x675" at 150 %.
    """
    scale = ui_scale(widget)
    width, height = (int(value) for value in size.split("x"))
    return f"{round(width * scale)}x{round(height * scale)}"


def place_window(
    window: tk.Toplevel, reference: tk.Misc, size: str, offset: tuple[int, int] = DIALOG_OFFSET
) -> None:
    """Size a window and place it at an offset from a reference window.

    Args:
        window: Window to place.
        reference: Window whose top-left corner is the origin.
        size: Tk size at 100 % screen scale, e.g. "400x450".
        offset: ``(x, y)`` offset in pixels from the reference corner.
    """
    offset_x, offset_y = offset
    position = f"+{reference.winfo_x() + offset_x}+{reference.winfo_y() + offset_y}"
    window.geometry(scaled_size(window, size) + position)


def setup_secondary_window(
    window: tk.Toplevel, parent: tk.Misc, on_escape: Optional[Callable[[], None]] = None
) -> None:
    """Keep a window above its parent, close it with Escape and focus it.

    Args:
        window: Dialog or settings window.
        parent: Widget whose window owns ``window``.
        on_escape: Called by Escape instead of closing the window (e.g. "cancel").
    """
    window.transient(parent.winfo_toplevel())
    close = on_escape if on_escape is not None else window.destroy
    window.bind(CLOSE_KEY, lambda _event: close())
    window.focus_set()


def setup_dialog(
    window: tk.Toplevel,
    parent: tk.Misc,
    size: str,
    on_escape: Optional[Callable[[], None]] = None,
) -> None:
    """Place a dialog near its parent and give it the secondary window behavior.

    Args:
        window: Dialog to set up.
        parent: Window the dialog is positioned against and attached to.
        size: Tk size at 100 % screen scale.
        on_escape: Called by Escape instead of closing the dialog.
    """
    place_window(window, parent, size)
    setup_secondary_window(window, parent, on_escape)

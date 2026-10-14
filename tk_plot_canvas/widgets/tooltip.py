"""Tooltip: a short help text shown when the mouse rests on a widget."""

import tkinter as tk
from typing import Optional

TOOLTIP_DELAY_MS = 500
TOOLTIP_OFFSET = (12, 18)
TOOLTIP_WRAP_LENGTH = 320
TOOLTIP_BACKGROUND = "#ffffe1"
TOOLTIP_PADDING = (6, 3)


class ToolTip:
    """Show ``text`` near the mouse after it rests on ``widget``."""

    def __init__(self, widget: tk.Misc, text: str) -> None:
        """Attach the tooltip to a widget.

        Args:
            widget: Widget described by the tooltip.
            text: Help text.
        """
        self._widget = widget
        self._text = text
        self._window: Optional[tk.Toplevel] = None
        self._pending: Optional[str] = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _event: tk.Event) -> None:
        """Show the tooltip after a short delay.

        Args:
            _event: Mouse event (unused).
        """
        self._cancel()
        self._pending = self._widget.after(TOOLTIP_DELAY_MS, self._show)

    def _cancel(self) -> None:
        """Cancel a scheduled display."""
        if self._pending is not None:
            self._widget.after_cancel(self._pending)
            self._pending = None

    def _show(self) -> None:
        """Display the tooltip next to the mouse pointer."""
        self._pending = None
        offset_x, offset_y = TOOLTIP_OFFSET
        x_position = self._widget.winfo_pointerx() + offset_x
        y_position = self._widget.winfo_pointery() + offset_y
        self._window = tk.Toplevel(self._widget)
        self._window.wm_overrideredirect(True)
        self._window.wm_geometry(f"+{x_position}+{y_position}")
        tk.Label(
            self._window,
            text=self._text,
            justify="left",
            background=TOOLTIP_BACKGROUND,
            relief="solid",
            borderwidth=1,
            wraplength=TOOLTIP_WRAP_LENGTH,
            padx=TOOLTIP_PADDING[0],
            pady=TOOLTIP_PADDING[1],
        ).pack()

    def _hide(self, _event: Optional[tk.Event] = None) -> None:
        """Hide the tooltip, or cancel its display.

        Args:
            _event: Mouse event (unused).
        """
        self._cancel()
        if self._window is not None:
            self._window.destroy()
            self._window = None

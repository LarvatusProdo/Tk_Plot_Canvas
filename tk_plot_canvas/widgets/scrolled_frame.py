"""Vertically (and optionally horizontally) scrollable frame widget."""

import tkinter as tk
from tkinter import ttk
from typing import Any, Optional

from ..config import (
    DEFAULT_BACKGROUND_COLOR,
    SCROLLED_FRAME_DEFAULT_HEIGHT,
    SCROLLED_FRAME_INNER_OFFSET,
)

_LINUX_SCROLL_UP = "<4>"
_LINUX_SCROLL_DOWN = "<5>"
_MOUSE_WHEEL = "<MouseWheel>"
_SCROLL_EVENTS = (_LINUX_SCROLL_UP, _LINUX_SCROLL_DOWN, _MOUSE_WHEEL)
_OWN_ATTRIBUTES = ("outer", "inner", "canvas", "outer_attributes")


class VerticalScrolledFrame:
    """A scrollable frame that can be used like any other Tk frame.

    Geometry methods (pack, grid, destroy...) are forwarded to the outer
    frame; every other attribute is forwarded to the inner frame, so widgets
    can use an instance directly as their master.

    Attributes:
        outer: Frame holding the scrollbars and the canvas.
        canvas: Canvas providing the scrolling viewport.
        inner: Frame receiving the child widgets.
    """

    def __init__(
        self,
        master: tk.Misc,
        x_bar: bool = False,
        side_Y_bar: str = tk.RIGHT,  # noqa: N803 - historical keyword name
        side_X_bar: str = tk.BOTTOM,  # noqa: N803 - historical keyword name
        bg_canvas: str = "",
        height_canvas: Any = SCROLLED_FRAME_DEFAULT_HEIGHT,
        style_frame: str = "TFrame",
        **kwargs: Any,
    ) -> None:
        """Create the scrollable frame.

        Args:
            master: Parent widget.
            x_bar: Whether to add a horizontal scrollbar.
            side_Y_bar: Side of the vertical scrollbar.
            side_X_bar: Side of the horizontal scrollbar.
            bg_canvas: Canvas background ("" = taken from ``style_frame``).
            height_canvas: Canvas height (any Tk distance).
            style_frame: ttk style of the outer and inner frames.
            **kwargs: Passed to the outer ``ttk.Frame`` ("width" goes to the
                canvas).
        """
        width = kwargs.pop("width", None)
        self.outer = ttk.Frame(master, **kwargs, style=style_frame)
        if bg_canvas == "":
            bg_canvas = ttk.Style().lookup(
                style_frame, "background", default=DEFAULT_BACKGROUND_COLOR
            )
        vertical_bar = self._build_scrollbars(x_bar, side_Y_bar, side_X_bar)
        self.canvas = tk.Canvas(
            self.outer, bd=0, highlightthickness=0, width=width, height=height_canvas, bg=bg_canvas
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._connect_scrollbars(vertical_bar)
        self._build_inner_frame(style_frame)
        self.outer_attributes = set(dir(tk.Widget))

    def _build_inner_frame(self, style_frame: str) -> None:
        """Create the frame receiving the children, inside the canvas.

        Args:
            style_frame: ttk style of the frame.
        """
        self.inner = ttk.Frame(self.canvas, style=style_frame)
        offset = SCROLLED_FRAME_INNER_OFFSET
        self.canvas.create_window(offset, offset, window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._on_frame_configure)

    def __getattr__(self, item: str) -> Any:
        """Forward unknown attributes to the outer or inner frame.

        Args:
            item: Attribute name.

        Returns:
            The attribute of the outer frame for geometry/Tk widget methods,
            otherwise the attribute of the inner frame.
        """
        if item in _OWN_ATTRIBUTES:
            raise AttributeError(item)
        if item in self.outer_attributes:
            return getattr(self.outer, item)
        return getattr(self.inner, item)

    def __str__(self) -> str:
        """Return the Tk path of the outer frame.

        Returns:
            The outer frame path, so the instance can be managed by
            notebooks and paned windows.
        """
        return str(self.outer)

    def _build_scrollbars(self, x_bar: bool, side_y_bar: str, side_x_bar: str) -> ttk.Scrollbar:
        """Create the scrollbars inside the outer frame.

        Args:
            x_bar: Whether to add a horizontal scrollbar.
            side_y_bar: Side of the vertical scrollbar.
            side_x_bar: Side of the horizontal scrollbar.

        Returns:
            The vertical scrollbar.
        """
        vertical_bar = ttk.Scrollbar(self.outer, orient=tk.VERTICAL)
        vertical_bar.pack(fill=tk.Y, side=side_y_bar)
        self.horizontal_bar: Optional[ttk.Scrollbar] = None
        if x_bar:
            self.horizontal_bar = ttk.Scrollbar(self.outer, orient=tk.HORIZONTAL)
            self.horizontal_bar.pack(fill=tk.X, side=side_x_bar)
        return vertical_bar

    def _connect_scrollbars(self, vertical_bar: ttk.Scrollbar) -> None:
        """Link the scrollbars to the canvas and enable wheel scrolling.

        Args:
            vertical_bar: The vertical scrollbar.
        """
        self.canvas["yscrollcommand"] = vertical_bar.set
        if self.horizontal_bar is not None:
            self.canvas["xscrollcommand"] = self.horizontal_bar.set
        # Mouse-wheel events only reach the canvas through bind_all, so they
        # are bound while the pointer is over the canvas.
        self.canvas.bind("<Enter>", self._bind_mouse)
        self.canvas.bind("<Leave>", self._unbind_mouse)
        vertical_bar["command"] = self.canvas.yview
        if self.horizontal_bar is not None:
            self.horizontal_bar["command"] = self.canvas.xview

    def _on_frame_configure(self, event: Optional[tk.Event] = None) -> None:
        """Update the scroll region when the inner frame is resized.

        Args:
            event: Tk configure event (unused).
        """
        _, _, right, bottom = self.canvas.bbox("all")
        height = self.canvas.winfo_height()
        self.canvas.config(scrollregion=(0, 0, right, max(bottom, height)))

    def _bind_mouse(self, event: Optional[tk.Event] = None) -> None:
        """Start listening to mouse-wheel events.

        Args:
            event: Tk enter event (unused).
        """
        for sequence in _SCROLL_EVENTS:
            self.canvas.bind_all(sequence, self._on_mousewheel)

    def _unbind_mouse(self, event: Optional[tk.Event] = None) -> None:
        """Stop listening to mouse-wheel events.

        Args:
            event: Tk leave event (unused).
        """
        for sequence in _SCROLL_EVENTS:
            self.canvas.unbind_all(sequence)

    def _on_mousewheel(self, event: tk.Event) -> None:
        """Scroll the canvas (Linux uses event.num, Windows/macOS event.delta).

        Args:
            event: Tk mouse-wheel event.
        """
        try:
            if event.num == 4 or event.delta > 0:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                self.canvas.yview_scroll(1, "units")
        except (tk.TclError, TypeError, AttributeError):
            pass

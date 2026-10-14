"""Entry placed over a Matplotlib figure to edit one of its texts in place."""

import tkinter as tk
from tkinter import ttk
from typing import Callable

from matplotlib.text import Text

MINIMUM_WIDTH = 160
EXTRA_WIDTH = 24
COMMIT_EVENTS = ("<Return>", "<KP_Enter>", "<FocusOut>")


class InlineTextEditor:
    """Edit a figure text in an entry drawn over it.

    Enter (or leaving the entry) validates, Escape cancels.
    """

    def __init__(
        self, figure_widget: tk.Widget, text: Text, on_commit: Callable[[str], None]
    ) -> None:
        """Create the entry over the text and give it the focus.

        Args:
            figure_widget: Tk widget of the Matplotlib figure.
            text: Text being edited (title, axis label...).
            on_commit: Called with the new text when the edit is validated.
        """
        self._figure_widget = figure_widget
        self._on_commit = on_commit
        self._is_closed = False
        self._entry = ttk.Entry(figure_widget)
        self._entry.insert(0, text.get_text())
        self._entry.select_range(0, tk.END)
        self._place_over(text)
        for sequence in COMMIT_EVENTS:
            self._entry.bind(sequence, lambda _event: self._close(commit=True))
        self._entry.bind("<Escape>", lambda _event: self._close(commit=False))
        self._entry.focus_set()

    def _place_over(self, text: Text) -> None:
        """Center the entry on the text (Matplotlib's y axis points up, Tk's down).

        Args:
            text: Text being edited.
        """
        extent = text.get_window_extent()
        x_center = (extent.x0 + extent.x1) / 2
        y_center = self._figure_widget.winfo_height() - (extent.y0 + extent.y1) / 2
        width = max(max(extent.width, extent.height) + EXTRA_WIDTH, MINIMUM_WIDTH)
        self._entry.place(x=x_center, y=y_center, anchor="center", width=width)

    def _close(self, commit: bool) -> None:
        """Remove the entry, validating the edit when requested (only once).

        Args:
            commit: Whether to apply the typed text.
        """
        if self._is_closed:
            return
        self._is_closed = True
        new_text = self._entry.get()
        self._entry.destroy()
        self._figure_widget.focus_set()
        if commit:
            self._on_commit(new_text)

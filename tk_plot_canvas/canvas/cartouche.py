"""Cartouche: a table under the plot showing the metadata of each curve."""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from ..compat import to_tk_color
from ..config import (
    CARTOUCHE_LINE_SYMBOL_FONT,
    NO_STYLE,
    PLOT_TYPE_2D,
    SOLID_LINE_STYLE,
    SOLID_LINE_SYMBOL,
    STYLE_CARTOUCHE_CELL,
    STYLE_CARTOUCHE_HEADER,
)

LINE_SYMBOL_WIDTH = 3
CELL_PADDING = 5


def line_symbol(linestyle: str, marker: str) -> str:
    """Return the text drawn in the cartouche to represent a curve.

    Args:
        linestyle: Matplotlib line style ("-", "--", "None"...).
        marker: Matplotlib marker ("o", "x", "None"...).

    Returns:
        e.g. "―o" for a solid line with circle markers.
    """
    if linestyle == SOLID_LINE_STYLE:
        linestyle = SOLID_LINE_SYMBOL
    symbol = linestyle if linestyle != NO_STYLE else ""
    return symbol + (marker if marker != NO_STYLE else "")


class CartoucheMixin:
    """Fill the cartouche grid.

    Requires the host canvas attributes ``cartouche_frame``,
    ``cartouche_rows`` (widgets per curve; column 0 is the line symbol),
    ``cartouche_headers``, ``cartouche_initialized``, ``lines``,
    ``line_labels``, ``plot_type``, ``graph_background_color``,
    ``panedwindow`` and ``show_cartouche``.
    """

    def fill_cartouche_row(
        self,
        label_to_display: Optional[dict] = None,
        line_index: int = 0,
        line_display: bool = True,
    ) -> None:
        """Display the metadata of one curve in the cartouche.

        Args:
            label_to_display: Metadata to display ({column title: value}).
            line_index: Index of the curve.
            line_display: Whether to draw the line symbol in column 0.
        """
        self._reset_cartouche_row(line_index)
        if label_to_display is not None and not self.cartouche_initialized:
            self._create_cartouche_headers(list(label_to_display))
        if line_display and self.plot_type == PLOT_TYPE_2D:
            self._add_line_symbol(line_index)
        else:
            self.cartouche_rows[line_index].append(None)
        if label_to_display is not None:
            for column, value in enumerate(label_to_display.values(), start=1):
                self._add_cartouche_cell(line_index, column, value)

    def set_cartouche_visible(self, visible: bool) -> None:
        """Show or hide the cartouche below the plot.

        Args:
            visible: Whether the cartouche is displayed.
        """
        if visible == self.show_cartouche:
            return
        if visible:
            self.panedwindow.add(self.cartouche_frame, weight=0)
        else:
            self.panedwindow.forget(self.cartouche_frame)
        self.show_cartouche = visible

    def refresh_cartouche(self) -> None:
        """Rebuild the cartouche rows of every plotted curve."""
        for index in range(len(self.lines)):
            self.fill_cartouche_row(self.line_labels[index], line_index=index, line_display=True)

    def _reset_cartouche_row(self, line_index: int) -> None:
        """Destroy the widgets of a row, or make sure the row list exists.

        Args:
            line_index: Index of the curve.
        """
        rows = self.cartouche_rows
        if len(rows) > line_index + 1:
            for widget in rows[line_index]:
                try:
                    widget.destroy()
                except (tk.TclError, AttributeError):
                    pass
            rows[line_index] = []
            return
        rows.append([])
        while len(rows) <= line_index + 1:
            rows.append([])

    def _create_cartouche_headers(self, titles: list[str]) -> None:
        """Create the column titles (only once).

        Args:
            titles: Column titles.
        """
        for column, title in enumerate(titles, start=1):
            header = ttk.Label(self.cartouche_frame, text=title, style=STYLE_CARTOUCHE_HEADER)
            header.grid(row=0, column=column, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING)
            self.cartouche_headers.append(header)
        self.cartouche_initialized = True

    def _add_line_symbol(self, line_index: int) -> None:
        """Draw the line style and marker of a curve in column 0.

        Args:
            line_index: Index of the curve.
        """
        line = self.lines[line_index]
        symbol = tk.Label(
            self.cartouche_frame,
            text=line_symbol(line.get_linestyle(), line.get_marker()),
            background=self.graph_background_color,
            foreground=to_tk_color(line.get_color()),
            width=LINE_SYMBOL_WIDTH,
            font=CARTOUCHE_LINE_SYMBOL_FONT,
        )
        symbol.grid(row=line_index + 1, column=0, sticky="w", padx=(CELL_PADDING, 0), pady=0)
        self.cartouche_rows[line_index].append(symbol)

    def _add_cartouche_cell(self, line_index: int, column: int, value: object) -> None:
        """Add one metadata value to the cartouche.

        Args:
            line_index: Index of the curve.
            column: Grid column (1-based; column 0 is the line symbol).
            value: Value to display.
        """
        cell = ttk.Label(self.cartouche_frame, text=str(value), style=STYLE_CARTOUCHE_CELL)
        cell.grid(
            row=line_index + 1, column=column, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING
        )
        self.cartouche_rows[line_index].append(cell)

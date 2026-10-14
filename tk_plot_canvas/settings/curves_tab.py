"""Settings tab "Courbes": color, width, style and markers of 2D curves."""

import tkinter as tk
from dataclasses import dataclass
from functools import partial
from tkinter import colorchooser, ttk
from typing import Any, Optional

from ..canvas.cartouche import line_symbol
from ..compat import to_tk_color
from ..config import (
    CARTOUCHE_LINE_SYMBOL_FONT,
    LINE_STYLES,
    LINE_WIDTH_RANGE,
    MARKER_SIZE_RANGE,
    MARKERS,
    NO_LEGEND_LABEL,
    STYLE_COLUMN_HEADER,
)
from .base_tab import SettingsTab

COLUMN_TITLES = (
    "Couleur:",
    "Épaisseur de ligne:",
    "Style de ligne:",
    "Marqueur:",
    "Taille du marqueur:",
)
CELL_PADDING = 5
LINE_SYMBOL_WIDTH = 3
SPINBOX_RANGES = {"linewidth": LINE_WIDTH_RANGE, "markersize": MARKER_SIZE_RANGE}
# Typed values are applied when pressing Enter or leaving the field.
SPINBOX_TYPING_EVENTS = ("<Return>", "<FocusOut>")


@dataclass
class CurveWidgets:
    """Widgets editing one curve."""

    color_button: tk.Button
    linewidth_spinbox: ttk.Spinbox
    linestyle_combobox: ttk.Combobox
    marker_combobox: ttk.Combobox
    markersize_spinbox: ttk.Spinbox


class CurvesTab(SettingsTab):
    """Edit the appearance of every plotted line.

    Attributes:
        curve_widgets: Widgets of each curve, in plotting order.
    """

    def build(self) -> None:
        """Create the column titles and one row of widgets per curve."""
        ttk.Label(self.frame, text="Paramètres des courbes:", style=STYLE_COLUMN_HEADER).grid(
            row=0, column=0, sticky="w", padx=5, pady=10, columnspan=6
        )
        for column, title in enumerate(COLUMN_TITLES):
            ttk.Label(self.frame, text=title, style=STYLE_COLUMN_HEADER).grid(
                row=1, column=column, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING
            )
        self.curve_widgets: list[CurveWidgets] = []
        for index, line in enumerate(self.canvas.lines):
            self.curve_widgets.append(self._build_curve_row(line, index))

    def _build_curve_row(self, line: Any, index: int) -> CurveWidgets:
        """Create the widgets of one curve, initialized from the line.

        Args:
            line: Matplotlib ``Line2D``.
            index: Curve index.

        Returns:
            The created widgets.
        """
        row = index + 2
        color_button = tk.Button(
            self.frame,
            bg=to_tk_color(line.get_color()),
            width=5,
            command=partial(self._choose_color, index),
        )
        color_button.grid(row=row, column=0, padx=CELL_PADDING, pady=CELL_PADDING)
        linewidth = self._add_spinbox(row, 1, "linewidth", index)
        linewidth.set(line.get_linewidth())
        linestyle = self._add_combobox(
            row, 2, LINE_STYLES, line.get_linestyle(), "linestyle", index
        )
        marker = self._add_combobox(row, 3, MARKERS, line.get_marker(), "marker", index)
        markersize = self._add_spinbox(row, 4, "markersize", index)
        markersize.set(line.get_markersize())
        return CurveWidgets(color_button, linewidth, linestyle, marker, markersize)

    def _add_spinbox(
        self, row: int, column: int, property_name: str, index: int
    ) -> ttk.Spinbox:
        """Create a numeric spinbox updating a line property (arrows or typed value).

        Args:
            row: Grid row.
            column: Grid column.
            property_name: "linewidth" or "markersize".
            index: Curve index.

        Returns:
            The created spinbox.
        """
        minimum, maximum, increment = SPINBOX_RANGES[property_name]
        spinbox = ttk.Spinbox(
            self.frame,
            from_=minimum,
            to=maximum,
            increment=increment,
            width=5,
            command=partial(self._update_line_property, property_name, index),
        )
        spinbox.grid(row=row, column=column, padx=CELL_PADDING, pady=CELL_PADDING)
        for sequence in SPINBOX_TYPING_EVENTS:
            spinbox.bind(sequence, partial(self._on_value_typed, spinbox, property_name, index))
        return spinbox

    def _on_value_typed(
        self, spinbox: ttk.Spinbox, property_name: str, index: int, _event: tk.Event
    ) -> None:
        """Apply a typed width or size, clamped to its range; restore it when invalid.

        Args:
            spinbox: Spinbox holding the typed value.
            property_name: "linewidth" or "markersize".
            index: Curve index.
            _event: Key or focus event (unused).
        """
        minimum, maximum, _increment = SPINBOX_RANGES[property_name]
        try:
            value = float(spinbox.get().strip().replace(",", "."))
        except ValueError:
            spinbox.set(getattr(self.canvas.lines[index], f"get_{property_name}")())
            spinbox.bell()
            return
        spinbox.set(min(max(value, minimum), maximum))
        self._update_line_property(property_name, index)

    def _add_combobox(
        self,
        row: int,
        column: int,
        values: list[str],
        current: str,
        property_name: str,
        index: int,
    ) -> ttk.Combobox:
        """Create a read-only combobox updating a line property.

        Args:
            row: Grid row.
            column: Grid column.
            values: Available choices.
            current: Current value of the property.
            property_name: "linestyle" or "marker".
            index: Curve index.

        Returns:
            The created combobox.
        """
        combobox = ttk.Combobox(self.frame, values=values, state="readonly", width=8)
        combobox.grid(row=row, column=column, padx=CELL_PADDING, pady=CELL_PADDING)
        combobox.current(values.index(current))
        combobox.bind(
            "<<ComboboxSelected>>", partial(self._update_line_property, property_name, index)
        )
        return combobox

    def _choose_color(self, index: int) -> None:
        """Ask for a new curve color and apply it to the line and cartouche.

        Args:
            index: Curve index.
        """
        color_button = self.curve_widgets[index].color_button
        color_code = colorchooser.askcolor(
            color_button.cget("bg"), parent=self.window, title="Choisir une couleur"
        )
        if not (color_code and color_code[1]):
            return
        color = color_code[1]
        line = self.canvas.lines[index]
        line.set_color(color)
        if self.canvas.show_legend and line.get_label() != NO_LEGEND_LABEL:
            self.canvas.show_draggable_legend()
        self.redraw()
        color_button.configure(bg=color)
        self.canvas.cartouche_rows[index][0].configure(foreground=color)

    def _update_line_property(
        self, property_name: str, index: int, _event: Optional[tk.Event] = None
    ) -> None:
        """Apply the value of a widget to its line property.

        Args:
            property_name: "linewidth", "linestyle", "marker" or "markersize".
            index: Curve index.
            _event: Combobox event (unused).
        """
        widgets = self.curve_widgets[index]
        line = self.canvas.lines[index]
        linestyle = widgets.linestyle_combobox.get()
        marker = widgets.marker_combobox.get()
        if property_name == "linewidth":
            line.set_linewidth(float(widgets.linewidth_spinbox.get()))
        elif property_name == "linestyle":
            line.set_linestyle(linestyle)
        elif property_name == "marker":
            line.set_marker(marker)
        elif property_name == "markersize":
            line.set_markersize(float(widgets.markersize_spinbox.get()))
        self.redraw()
        self.canvas.cartouche_rows[index][0].configure(
            text=line_symbol(linestyle, marker),
            background=self.canvas.graph_background_color,
            foreground=to_tk_color(line.get_color()),
            width=LINE_SYMBOL_WIDTH,
            font=CARTOUCHE_LINE_SYMBOL_FONT,
        )

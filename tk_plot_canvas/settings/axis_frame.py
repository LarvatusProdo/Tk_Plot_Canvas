"""Label frame editing one axis: label, limits, scale, inversion, variable.

Changes are applied immediately: the label while typing, the limits when
pressing Enter or leaving the field, the other choices when selected.
"""

import tkinter as tk
from dataclasses import dataclass
from functools import partial
from tkinter import ttk
from typing import TYPE_CHECKING, Any, Optional

import matplotlib.dates as mdates
import numpy as np
from matplotlib.axes import Axes

from ..config import (
    AXIS_LIMIT_DECIMALS,
    AXIS_SCALE_NAMES,
    STYLE_BUTTON,
    STYLE_CHECKBUTTON,
    STYLE_COMBOBOX,
    STYLE_ENTRY,
    STYLE_LABEL,
    STYLE_LABELFRAME,
)
from ..widgets import ToolTip
from .choices import displayed_names, name_of

if TYPE_CHECKING:
    from .axes_tab import AxesTab

PADDING = (5, 5)
FRAME_PADDING = (10, 10)
SEPARATOR_PADY = (10, 10)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LIMIT_EVENTS = ("<Return>", "<FocusOut>")
LIMITS_HELP = (
    "Appuyez sur Entrée (ou quittez le champ) pour appliquer.\n"
    "Axe de dates : AAAA-MM-JJ ou AAAA-MM-JJ hh:mm:ss."
)
AUTO_HELP = "Ajuster les limites de l'axe aux données."


def format_limit(value: float, is_date: bool) -> str:
    """Format an axis limit for its entry.

    Args:
        value: Limit in data coordinates (matplotlib date number on a date axis).
        is_date: True when the axis shows dates.

    Returns:
        A "YYYY-MM-DD HH:MM:SS" text on a date axis, else the rounded number.
    """
    if is_date:
        return mdates.num2date(value).strftime(DATE_FORMAT)
    return str(np.round(value, AXIS_LIMIT_DECIMALS))


@dataclass
class AxisControls:
    """Tk variables and widgets editing one axis."""

    label_var: tk.StringVar
    min_var: tk.StringVar
    max_var: tk.StringVar
    scale_var: tk.StringVar
    autoscale_var: tk.BooleanVar
    inverted_var: tk.BooleanVar
    variable_combobox: Optional[ttk.Combobox] = None
    is_date: bool = False

    def show_limits(self, axes: Axes, axis_name: str) -> None:
        """Display the current limits of an axis (dates as text, numbers rounded).

        Args:
            axes: Matplotlib axes.
            axis_name: "x" or "y".
        """
        lower, upper = getattr(axes, f"get_{axis_name}lim")()
        self.min_var.set(format_limit(lower, self.is_date))
        self.max_var.set(format_limit(upper, self.is_date))


def create_axis_controls(axes: Axes, axis_name: str, is_date: bool = False) -> AxisControls:
    """Create the Tk variables of an axis from its current state.

    Args:
        axes: Matplotlib axes.
        axis_name: "x" or "y".
        is_date: True when the axis shows dates.

    Returns:
        The axis controls (without the variable combobox); the scale variable
        holds the displayed (French) scale name.
    """
    lower, upper = getattr(axes, f"get_{axis_name}lim")()
    scale = getattr(axes, f"get_{axis_name}scale")()
    return AxisControls(
        label_var=tk.StringVar(value=getattr(axes, f"get_{axis_name}label")()),
        min_var=tk.StringVar(value=format_limit(lower, is_date)),
        max_var=tk.StringVar(value=format_limit(upper, is_date)),
        scale_var=tk.StringVar(value=name_of(AXIS_SCALE_NAMES, scale)),
        autoscale_var=tk.BooleanVar(value=getattr(axes, f"get_autoscale{axis_name}_on")()),
        inverted_var=tk.BooleanVar(value=bool(getattr(axes, f"{axis_name}axis_inverted")())),
        is_date=is_date,
    )


class AxisFrame:
    """Widgets editing one axis, laid out in a label frame of the axes tab.

    Attributes:
        controls: Tk variables and widgets of the axis.
    """

    def __init__(self, tab: "AxesTab", axis_name: str, column: int, variables: list[str]) -> None:
        """Create the frame.

        Args:
            tab: The axes tab (applies the changes).
            axis_name: "x" or "y".
            column: Grid column of the frame in the tab.
            variables: xarray dimensions/variables selectable for this axis.
        """
        self._tab = tab
        self._axis_name = axis_name
        is_date = getattr(tab.canvas, f"is_date_on_{axis_name}_axis")
        self.controls = create_axis_controls(tab.canvas.axes, axis_name, is_date)
        self._frame = ttk.LabelFrame(
            tab.frame,
            text=f"Axe {axis_name.upper()}",
            padding=FRAME_PADDING,
            style=STYLE_LABELFRAME,
        )
        self._frame.grid(
            row=2, column=column, columnspan=2, sticky="nwe", padx=PADDING, pady=PADDING
        )
        self._build(variables)

    def _build(self, variables: list[str]) -> None:
        """Create the widgets of the frame.

        Args:
            variables: Selectable xarray dimensions/variables.
        """
        self._add_field_label("Libellé :", 1)
        ttk.Entry(
            self._frame, textvariable=self.controls.label_var, width=25, style=STYLE_ENTRY
        ).grid(row=1, column=1, columnspan=2, padx=(0, 4), sticky="w")
        self.controls.label_var.trace_add("write", self._on_label_typed)
        if len(variables) > 0:
            self._add_variable_selector(variables)
        self._add_separator(5)
        self._add_limit_entries()
        self._add_scale_controls()
        self._add_separator(20)
        ttk.Button(
            self._frame,
            text="Police du libellé et des graduations…",
            style=STYLE_BUTTON,
            command=partial(
                self._tab.open_font_dialog, f"{self._axis_name}label", self.controls.label_var.get
            ),
        ).grid(row=21, column=0, columnspan=3, padx=PADDING, sticky="ew")

    def _add_field_label(self, text: str, row: int) -> None:
        """Add a right-aligned field label in column 0.

        Args:
            text: Label text.
            row: Grid row.
        """
        ttk.Label(self._frame, text=text, style=STYLE_LABEL).grid(
            row=row, column=0, sticky="e", padx=PADDING, pady=PADDING
        )

    def _add_separator(self, row: int) -> None:
        """Add a horizontal separator spanning the frame.

        Args:
            row: Grid row.
        """
        ttk.Separator(self._frame, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky="we", pady=SEPARATOR_PADY
        )

    def _add_limit_entries(self) -> None:
        """Create the minimum and maximum limit entries (applied with Enter or on leaving)."""
        self._add_field_label("Minimum :", 6)
        self._add_field_label("Maximum :", 7)
        entry_width = 20 if self.controls.is_date else 15
        for row, variable in ((6, self.controls.min_var), (7, self.controls.max_var)):
            entry = ttk.Entry(
                self._frame, textvariable=variable, width=entry_width, style=STYLE_ENTRY
            )
            entry.grid(row=row, column=1, sticky="we")
            entry.bind("<KeyRelease>", self._on_limit_typed)
            for sequence in LIMIT_EVENTS:
                entry.bind(sequence, lambda _event: self._tab.apply_limits(self._axis_name))
            ToolTip(entry, LIMITS_HELP)

    def _on_limit_typed(self, event: tk.Event) -> None:
        """Turn the automatic limits off once the user types a limit.

        Args:
            event: Key event; only keys editing the text count as typing.
        """
        is_printable = bool(event.char) and event.char.isprintable()
        if is_printable or event.keysym in ("BackSpace", "Delete"):
            self.controls.autoscale_var.set(False)

    def _add_scale_controls(self) -> None:
        """Create the scale combobox (applied on selection) and the axis checkbuttons."""
        self._add_field_label("Échelle :", 8)
        scale_combobox = ttk.Combobox(
            self._frame,
            textvariable=self.controls.scale_var,
            values=displayed_names(AXIS_SCALE_NAMES),
            state="disabled" if self.controls.is_date else "readonly",
            width=14,
        )
        scale_combobox.grid(row=8, column=1, columnspan=2, sticky="we")
        scale_combobox.bind(
            "<<ComboboxSelected>>", lambda _event: self._tab.apply_scale(self._axis_name)
        )
        self._add_autoscale_control()
        self._add_inversion_control()

    def _add_autoscale_control(self) -> None:
        """Create the checkbutton fitting the axis limits to the data."""
        auto_checkbutton = ttk.Checkbutton(
            self._frame,
            text="Auto",
            variable=self.controls.autoscale_var,
            style=STYLE_CHECKBUTTON,
            command=partial(self._tab.autoscale_axis, self._axis_name),
        )
        auto_checkbutton.grid(row=6, column=2, rowspan=2, padx=PADDING, pady=PADDING, sticky="we")
        ToolTip(auto_checkbutton, AUTO_HELP)

    def _add_inversion_control(self) -> None:
        """Create the checkbutton inverting the axis."""
        ttk.Checkbutton(
            self._frame,
            text="Inverser l'axe",
            variable=self.controls.inverted_var,
            style=STYLE_CHECKBUTTON,
            command=self._invert_axis,
        ).grid(row=9, column=1, columnspan=2, padx=(0, 4), pady=PADDING, sticky="w")

    def _add_variable_selector(self, variables: list[str]) -> None:
        """Create the combobox choosing the xarray variable of the axis (applied on selection).

        Args:
            variables: Selectable dimensions and variables.
        """
        self._add_field_label("Variable :", 2)
        combobox = ttk.Combobox(
            self._frame, values=variables, state="readonly", width=20, style=STYLE_COMBOBOX
        )
        combobox.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="we")
        current = self._tab.canvas.xarray_variables[self._axis_name]
        combobox.current(variables.index(current) if current in variables else 0)
        combobox.bind("<<ComboboxSelected>>", lambda _event: self._tab.apply_variable_selection())
        self.controls.variable_combobox = combobox

    def _on_label_typed(self, *_trace_args: Any) -> None:
        """Show the typed label on the axis.

        Args:
            *_trace_args: Tk variable trace arguments (unused).
        """
        self._tab.set_axis_label(self._axis_name, self.controls.label_var.get())

    def _invert_axis(self) -> None:
        """Invert the axis and redraw."""
        getattr(self._tab.canvas.axes, f"invert_{self._axis_name}axis")()
        self._tab.redraw()

"""Label frame editing one axis: label, limits, scale, inversion, variable."""

import tkinter as tk
from dataclasses import dataclass
from functools import partial
from tkinter import ttk
from typing import TYPE_CHECKING, Optional

import numpy as np
from matplotlib.axes import Axes

from ..config import (
    AXIS_LIMIT_DECIMALS,
    AXIS_SCALES,
    STYLE_BUTTON,
    STYLE_CHECKBUTTON,
    STYLE_COMBOBOX,
    STYLE_ENTRY,
    STYLE_LABEL,
    STYLE_LABELFRAME,
)

if TYPE_CHECKING:
    from .axes_tab import AxesTab

PADDING = (5, 5)
FRAME_PADDING = (10, 10)
SEPARATOR_PADY = (10, 10)


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

    def show_limits(self, axes: Axes, axis_name: str) -> None:
        """Display the current limits of an axis, rounded.

        Args:
            axes: Matplotlib axes.
            axis_name: "x" or "y".
        """
        lower, upper = getattr(axes, f"get_{axis_name}lim")()
        self.min_var.set(np.round(lower, AXIS_LIMIT_DECIMALS))
        self.max_var.set(np.round(upper, AXIS_LIMIT_DECIMALS))


def create_axis_controls(axes: Axes, axis_name: str) -> AxisControls:
    """Create the Tk variables of an axis from its current state.

    Args:
        axes: Matplotlib axes.
        axis_name: "x" or "y".

    Returns:
        The axis controls (without the variable combobox).
    """
    lower, upper = getattr(axes, f"get_{axis_name}lim")()
    return AxisControls(
        label_var=tk.StringVar(value=getattr(axes, f"get_{axis_name}label")()),
        min_var=tk.StringVar(value=np.round(lower, AXIS_LIMIT_DECIMALS)),
        max_var=tk.StringVar(value=np.round(upper, AXIS_LIMIT_DECIMALS)),
        scale_var=tk.StringVar(value=getattr(axes, f"get_{axis_name}scale")()),
        autoscale_var=tk.BooleanVar(value=getattr(axes, f"get_autoscale{axis_name}_on")()),
        inverted_var=tk.BooleanVar(value=bool(getattr(axes, f"{axis_name}axis_inverted")())),
    )


class AxisFrame:
    """Widgets editing one axis, laid out in a label frame of the axes tab.

    Attributes:
        controls: Tk variables and widgets of the axis.
    """

    def __init__(
        self, tab: "AxesTab", axis_name: str, axis_title: str, column: int, variables: list[str]
    ) -> None:
        """Create the frame.

        Args:
            tab: The axes tab (receives the apply/autoscale/font requests).
            axis_name: "x" or "y".
            axis_title: Name of the axis shown before the label entry.
            column: Grid column of the frame in the tab.
            variables: xarray dimensions/variables selectable for this axis.
        """
        self._tab = tab
        self._axis_name = axis_name
        self.controls = create_axis_controls(tab.canvas.axes, axis_name)
        self._frame = ttk.LabelFrame(
            tab.frame,
            text=f"Axe {axis_name.upper()}",
            padding=FRAME_PADDING,
            style=STYLE_LABELFRAME,
        )
        self._frame.grid(
            row=2, column=column, columnspan=2, sticky="we", padx=PADDING, pady=PADDING
        )
        self._build(axis_title, variables)

    def _build(self, axis_title: str, variables: list[str]) -> None:
        """Create the widgets of the frame.

        Args:
            axis_title: Name of the axis shown before the label entry.
            variables: Selectable xarray dimensions/variables.
        """
        self._add_field_label(f"{axis_title}:", 1)
        ttk.Entry(
            self._frame, textvariable=self.controls.label_var, width=25, style=STYLE_ENTRY
        ).grid(row=1, column=1, columnspan=2, padx=(0, 4), sticky="w")
        self._add_separator(5)
        self._add_limit_entries()
        self._add_scale_controls()
        self._add_separator(20)
        ttk.Button(
            self._frame,
            text="Modifier la police",
            style=STYLE_BUTTON,
            command=partial(
                self._tab.open_font_dialog, f"{self._axis_name}label", self.controls.label_var.get
            ),
        ).grid(row=21, column=0, columnspan=3, padx=PADDING, sticky="ew")
        if len(variables) > 0:
            self._add_variable_selector(variables)

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
        """Create the minimum and maximum limit entries."""
        self._add_field_label("Valeur min:", 6)
        self._add_field_label("Valeur max:", 7)
        for row, variable in ((6, self.controls.min_var), (7, self.controls.max_var)):
            entry = ttk.Entry(self._frame, textvariable=variable, width=15, style=STYLE_ENTRY)
            entry.grid(row=row, column=1, sticky="we")
            entry.bind("<KeyRelease>", lambda _event: self.controls.autoscale_var.set(False))
            entry.bind("<Return>", lambda _event: self._tab.apply_changes())

    def _add_scale_controls(self) -> None:
        """Create the scale combobox and the autoscale/inversion checkbuttons."""
        self._add_field_label("Echelle:", 8)
        ttk.Combobox(
            self._frame,
            textvariable=self.controls.scale_var,
            values=AXIS_SCALES,
            state="readonly",
            width=8,
        ).grid(row=8, column=1, columnspan=2, sticky="we")
        ttk.Checkbutton(
            self._frame,
            text="Auto",
            variable=self.controls.autoscale_var,
            width=5,
            style=STYLE_CHECKBUTTON,
            command=partial(self._tab.autoscale_axis, self._axis_name),
        ).grid(row=6, column=2, rowspan=2, padx=PADDING, pady=PADDING, sticky="we")
        self._add_inversion_control()

    def _add_inversion_control(self) -> None:
        """Create the checkbutton inverting the axis."""
        self._add_field_label("Inversion axe:", 9)
        ttk.Checkbutton(
            self._frame,
            variable=self.controls.inverted_var,
            width=5,
            style=STYLE_CHECKBUTTON,
            command=self._invert_axis,
        ).grid(row=9, column=1, padx=PADDING, pady=PADDING, sticky="we")

    def _add_variable_selector(self, variables: list[str]) -> None:
        """Create the combobox choosing the xarray variable of the axis.

        Args:
            variables: Selectable dimensions and variables.
        """
        self._add_field_label("Variable:", 2)
        combobox = ttk.Combobox(
            self._frame, values=variables, state="readonly", width=20, style=STYLE_COMBOBOX
        )
        combobox.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="we")
        current = self._tab.canvas.xarray_variables[self._axis_name]
        combobox.current(variables.index(current) if current in variables else 0)
        self.controls.variable_combobox = combobox

    def _invert_axis(self) -> None:
        """Invert the axis and redraw."""
        getattr(self._tab.canvas.axes, f"invert_{self._axis_name}axis")()
        self._tab.redraw()

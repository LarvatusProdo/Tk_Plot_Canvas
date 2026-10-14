"""Settings tab "Axes et titre": title, axis labels, limits, scales, variables."""

import tkinter as tk
from functools import partial
from tkinter import messagebox, ttk
from typing import Any, Callable, Optional

import matplotlib.dates as mdates
import numpy as np

from ..config import (
    FONT_TARGET_TITLE,
    PLOT_TYPE_3D,
    STYLE_BUTTON,
    STYLE_ENTRY,
    STYLE_LABEL,
    STYLE_LABELFRAME,
    STYLE_SECTION_TITLE,
    VARIABLE_SEPARATOR,
)
from .axis_frame import FRAME_PADDING, PADDING, AxisControls, AxisFrame
from .base_tab import SettingsTab
from .font_dialogs import AxisFontDialog
from .surface_axes_frame import SurfaceAxesFrame

AXIS_NAMES = ("x", "y")
AXIS_TITLES = {"x": "Abscisse", "y": "Ordonnée"}
LIMIT_KEYWORDS = {"x": ("left", "right"), "y": ("bottom", "top")}


def parse_limit(variable: tk.StringVar, is_date: bool = False) -> Optional[float]:
    """Read an axis limit typed by the user.

    Args:
        variable: Variable of the limit entry.
        is_date: True when the axis shows dates ("YYYY-MM-DD" or "YYYY-MM-DD hh:mm:ss").

    Returns:
        The limit (matplotlib date number on a date axis), or None when the entry is empty.

    Raises:
        ValueError: If the entry is not a number (or not a valid date).
    """
    text = variable.get().strip()
    if not text:
        return None
    if is_date:
        return float(mdates.date2num(np.datetime64(text.replace(" ", "T"))))
    return float(text)


def set_limits(
    setter: Callable[..., Any], axis_name: str, lower: Optional[float], upper: Optional[float]
) -> None:
    """Apply the given limits of an axis (missing ones are left unchanged).

    Args:
        setter: ``Axes.set_xlim`` or ``Axes.set_ylim``.
        axis_name: "x" or "y".
        lower: Lower limit, or None.
        upper: Upper limit, or None.
    """
    lower_keyword, upper_keyword = LIMIT_KEYWORDS[axis_name]
    if lower is not None and upper is not None:
        setter(lower, upper)
    elif lower is not None:
        setter(**{lower_keyword: lower})
    elif upper is not None:
        setter(**{upper_keyword: upper})


class AxesTab(SettingsTab):
    """Edit the title and both axes.

    Attributes:
        title_var: Title typed by the user.
        axis_controls: Controls of the "x" and "y" axes.
    """

    def build(self) -> None:
        """Create the title frame, both axis frames and the apply button."""
        ttk.Label(
            self.frame, text="Modification des axes et titres:", style=STYLE_SECTION_TITLE
        ).grid(row=0, column=0, sticky="w", padx=5, pady=10, columnspan=2)
        self._build_title_frame()
        variables = self._xarray_variable_choices()
        self.axis_controls: dict[str, AxisControls] = {}
        for column, axis_name in enumerate(AXIS_NAMES):
            axis_frame = AxisFrame(self, axis_name, AXIS_TITLES[axis_name], 2 * column, variables)
            self.axis_controls[axis_name] = axis_frame.controls
        if self.canvas.plot_type == PLOT_TYPE_3D:
            SurfaceAxesFrame(self, row=2, column=2 * len(AXIS_NAMES))
        ttk.Button(
            self.frame,
            text="Appliquer les changements",
            command=self.apply_changes,
            width=20,
            style=STYLE_BUTTON,
        ).grid(row=0, column=2, columnspan=2, padx=PADDING, pady=PADDING, sticky="we")

    def _build_title_frame(self) -> None:
        """Create the title entry and its font button."""
        frame = ttk.LabelFrame(
            self.frame, text="Titre", padding=FRAME_PADDING, style=STYLE_LABELFRAME
        )
        frame.grid(row=1, column=0, columnspan=4, sticky="we", padx=PADDING, pady=PADDING)
        ttk.Label(frame, text="Titre:", style=STYLE_LABEL).grid(
            row=1, column=0, sticky="e", padx=PADDING, pady=PADDING
        )
        self.title_var = tk.StringVar(value="")
        ttk.Entry(frame, textvariable=self.title_var, width=50, style=STYLE_ENTRY).grid(
            row=1, column=1, padx=(0, 4), sticky="w"
        )
        self.title_var.set(self.canvas.axes.get_title())
        ttk.Button(
            frame,
            text="Modifier la police",
            style=STYLE_BUTTON,
            command=partial(self.open_font_dialog, FONT_TARGET_TITLE, self.title_var.get),
        ).grid(row=1, column=2, padx=(10, 5), sticky="ew")

    def open_font_dialog(self, target: str, label_text: Callable[[], str]) -> None:
        """Open the font dialog of the title or of an axis label.

        Args:
            target: "Graphique title", "xlabel" or "ylabel".
            label_text: Returns the text to redraw with the new font.
        """
        AxisFontDialog(self.window, self.canvas, target, label_text)

    def _xarray_variable_choices(self) -> list[str]:
        """List the dimensions and variables of the first xarray dataset.

        Returns:
            Dimensions, a separator, then variables ([] without dataset).
        """
        if len(self.canvas.datasets) == 0:
            return []
        dataset = self.canvas.datasets[0]
        return list(dataset.dims) + [VARIABLE_SEPARATOR] + list(dataset.data_vars)

    def autoscale_axis(self, axis_name: str) -> None:
        """Fit an axis to the data and show the resulting limits of both axes.

        Args:
            axis_name: "x" or "y".
        """
        axes = self.canvas.axes
        axes.autoscale(axis=axis_name, tight=True)
        self.redraw()
        for name in AXIS_NAMES:
            self.axis_controls[name].show_limits(axes, name)

    def apply_changes(self) -> None:
        """Apply the title, labels, xarray variables, limits and scales."""
        self._apply_texts()
        self._apply_variable_selection()
        self._apply_limits_and_scales()
        axes = self.canvas.axes
        for name in AXIS_NAMES:
            if self.axis_controls[name].autoscale_var.get():
                axes.autoscale(axis=name, tight=True)
        self.redraw()

    def _apply_texts(self) -> None:
        """Apply the title (keeping its font) and both axis labels."""
        axes = self.canvas.axes
        font = axes.title.get_fontproperties()
        axes.set_title(
            self.title_var.get(),
            fontfamily=font.get_name(),
            fontsize=font.get_size(),
            fontstyle=font.get_style(),
            fontweight=font.get_weight(),
            color=axes.title.get_color(),
        )
        axes.set_xlabel(self.axis_controls["x"].label_var.get())
        axes.set_ylabel(self.axis_controls["y"].label_var.get())

    def _apply_variable_selection(self) -> None:
        """Re-plot the xarray datasets when another x or y variable is chosen."""
        if len(self.canvas.datasets) == 0:
            return
        dataset = self.canvas.datasets[0]
        known_names = list(dataset.data_vars) + list(dataset.dims)
        selection = self.canvas.xarray_variables
        is_modified = False
        for name in AXIS_NAMES:
            selected = self.axis_controls[name].variable_combobox.get()
            if selected != selection[name] and selected in known_names:
                selection[name] = selected
                is_modified = True
        if is_modified:
            self.canvas.view_parameters = self.canvas.get_current_parameters()
            self.canvas.update_plot()

    def _apply_limits_and_scales(self) -> None:
        """Apply the typed limits and the selected scales."""
        axes = self.canvas.axes
        x_controls, y_controls = self.axis_controls["x"], self.axis_controls["y"]
        try:
            x_limits = (
                parse_limit(x_controls.min_var, x_controls.is_date),
                parse_limit(x_controls.max_var, x_controls.is_date),
            )
            y_limits = (
                parse_limit(y_controls.min_var, y_controls.is_date),
                parse_limit(y_controls.max_var, y_controls.is_date),
            )
            set_limits(axes.set_xlim, "x", *x_limits)
            set_limits(axes.set_ylim, "y", *y_limits)
            if not x_controls.is_date:
                axes.set_xscale(x_controls.scale_var.get())
            if not y_controls.is_date:
                axes.set_yscale(y_controls.scale_var.get())
        except ValueError:
            messagebox.showerror(
                "Invalid input",
                "Please enter valid axis limits (numbers, or YYYY-MM-DD [hh:mm:ss] on a date axis).",
            )

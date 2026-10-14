"""Settings tab "Axes et titre": title, axis labels, limits, scales, variables.

Every change is applied immediately: texts while typing, limits when pressing
Enter or leaving the field, choices as soon as they are selected.
"""

import tkinter as tk
from functools import partial
from tkinter import ttk
from typing import Any, Callable, Optional

import matplotlib.dates as mdates
import numpy as np

from ..config import (
    AXIS_SCALE_NAMES,
    FONT_TARGET_TITLE,
    PLOT_TYPE_3D,
    STYLE_BUTTON,
    STYLE_ENTRY,
    STYLE_LABEL,
    STYLE_LABELFRAME,
    VARIABLE_SEPARATOR,
)
from .axis_frame import FRAME_PADDING, PADDING, AxisControls, AxisFrame, format_limit
from .base_tab import SettingsTab
from .choices import value_of
from .font_dialogs import AxisFontDialog
from .surface_axes_frame import SurfaceAxesFrame

AXIS_NAMES = ("x", "y")
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
    return float(text.replace(",", "."))


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
        """Create the title frame and both axis frames."""
        self._build_title_frame()
        variables = self._xarray_variable_choices()
        self.axis_controls: dict[str, AxisControls] = {}
        for column, axis_name in enumerate(AXIS_NAMES):
            axis_frame = AxisFrame(self, axis_name, 2 * column, variables)
            self.axis_controls[axis_name] = axis_frame.controls
        if self.canvas.plot_type == PLOT_TYPE_3D:
            SurfaceAxesFrame(self, row=2, column=2 * len(AXIS_NAMES))

    def _build_title_frame(self) -> None:
        """Create the title entry (applied while typing) and its font button."""
        frame = ttk.LabelFrame(
            self.frame, text="Titre", padding=FRAME_PADDING, style=STYLE_LABELFRAME
        )
        frame.grid(row=1, column=0, columnspan=4, sticky="we", padx=PADDING, pady=PADDING)
        ttk.Label(frame, text="Texte :", style=STYLE_LABEL).grid(
            row=1, column=0, sticky="e", padx=PADDING, pady=PADDING
        )
        self.title_var = tk.StringVar(value=self.canvas.axes.get_title())
        ttk.Entry(frame, textvariable=self.title_var, width=50, style=STYLE_ENTRY).grid(
            row=1, column=1, padx=(0, 4), sticky="w"
        )
        self.title_var.trace_add("write", self._on_title_typed)
        ttk.Button(
            frame,
            text="Police…",
            style=STYLE_BUTTON,
            command=partial(self.open_font_dialog, FONT_TARGET_TITLE, self.title_var.get),
        ).grid(row=1, column=2, padx=(10, 5), sticky="ew")

    def _on_title_typed(self, *_trace_args: Any) -> None:
        """Show the typed title on the plot (its font is kept).

        Args:
            *_trace_args: Tk variable trace arguments (unused).
        """
        text = self.title_var.get()
        self.canvas.axes.title.set_text(text)
        self.canvas.title_var.set(text)
        self.redraw_idle()

    def set_axis_label(self, axis_name: str, text: str) -> None:
        """Show a typed axis label on the plot (its font is kept).

        Args:
            axis_name: "x" or "y".
            text: Label text.
        """
        getattr(self.canvas.axes, f"{axis_name}axis").label.set_text(text)
        getattr(self.canvas, f"{axis_name}label_var").set(text)
        self.redraw_idle()

    def open_font_dialog(self, target: str, label_text: Callable[[], str]) -> None:
        """Open the font dialog of the title or of an axis label.

        Args:
            target: "Graphique title", "xlabel" or "ylabel".
            label_text: Returns the text to redraw with the new font.
        """
        self.canvas.dialogs.show(
            f"font:{target}",
            partial(AxisFontDialog, self.window, self.canvas, target, label_text),
        )

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

    def apply_scale(self, axis_name: str) -> None:
        """Apply the selected scale (linear or logarithmic) to an axis.

        Args:
            axis_name: "x" or "y".
        """
        controls = self.axis_controls[axis_name]
        if controls.is_date:
            return
        axes = self.canvas.axes
        getattr(axes, f"set_{axis_name}scale")(
            value_of(AXIS_SCALE_NAMES, controls.scale_var.get())
        )
        if controls.autoscale_var.get():
            axes.autoscale(axis=axis_name, tight=True)
        self.redraw()
        controls.show_limits(axes, axis_name)

    def apply_limits(self, axis_name: str) -> None:
        """Apply the limits typed for an axis, or show the current ones when invalid.

        Args:
            axis_name: "x" or "y".
        """
        controls = self.axis_controls[axis_name]
        axes = self.canvas.axes
        try:
            lower = self._typed_limit(controls, axis_name, controls.min_var, 0)
            upper = self._typed_limit(controls, axis_name, controls.max_var, 1)
        except ValueError:
            controls.show_limits(axes, axis_name)
            self.frame.bell()
            return
        if lower is None and upper is None:
            return
        set_limits(getattr(axes, f"set_{axis_name}lim"), axis_name, lower, upper)
        self.redraw()

    def _typed_limit(
        self, controls: AxisControls, axis_name: str, variable: tk.StringVar, position: int
    ) -> Optional[float]:
        """Read a typed limit, ignoring an entry that still shows the current limit.

        Args:
            controls: Controls of the axis.
            axis_name: "x" or "y".
            variable: Variable of the limit entry.
            position: 0 for the minimum, 1 for the maximum.

        Returns:
            The new limit, or None when the entry is empty or unchanged.

        Raises:
            ValueError: If the entry is not a number (or not a valid date).
        """
        current = getattr(self.canvas.axes, f"get_{axis_name}lim")()[position]
        if variable.get().strip() == format_limit(current, controls.is_date):
            return None
        return parse_limit(variable, controls.is_date)

    def apply_variable_selection(self) -> None:
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

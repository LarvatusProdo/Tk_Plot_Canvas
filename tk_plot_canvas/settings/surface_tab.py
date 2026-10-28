"""Settings tab "Graphique 3D": variable, plot kind, colormap, alpha and colorbar of maps."""

import tkinter as tk
from dataclasses import dataclass
from functools import partial
from tkinter import ttk
from typing import Any

from ..canvas.surface_kinds import set_surface_colormap
from ..compat import colormap_names
from ..config import (
    ALPHA_RANGE,
    DEFAULT_ALPHA,
    STYLE_BUTTON,
    STYLE_CHECKBUTTON,
    STYLE_COLUMN_HEADER,
    STYLE_COMBOBOX,
    SURFACE_SIZE_RANGES,
)
from ..widgets import CheckedSpinbox, ToolTip
from .base_tab import SettingsTab
from .colorbar_dialog import ColorbarDialog
from .surface_kind_combobox import SurfaceKindCombobox
from .value_range_dialog import ValueRangeDialog

COLUMN_TITLES = (
    ("N°", 1),
    ("Variable", 5),
    ("Type", 8),
    ("Classes", 10),
    ("Palette", 20),
    ("Opacité", 30),
    ("Taille", 35),
    ("Colorbar", 40),
)
OPACITY_HELP = "Opacité de la surface : 0 = transparente, 1 = opaque."
MAP_HELP = "Dessiner les côtes et les frontières (données longitude/latitude, cartopy)."
SIZE_HELP = (
    "Épaisseur des isolignes (points) ou taille des points du nuage (points²).\n"
    "Sans effet pour les autres types."
)
CELL_PADDING = (10, 10)


@dataclass
class SurfaceWidgets:
    """Widgets editing one surface plot."""

    variable_combobox: ttk.Combobox
    kind_combobox: SurfaceKindCombobox
    colormap_combobox: ttk.Combobox
    alpha_spinbox: CheckedSpinbox
    size_spinbox: CheckedSpinbox
    colorbar_var: tk.BooleanVar
    colorbar_button: ttk.Button


class SurfaceTab(SettingsTab):
    """Edit the surface plots of 2D xarray datasets.

    Attributes:
        surface_widgets: Widgets of each plot, indexed by plot index.
    """

    def build(self) -> None:
        """Create the column titles, the map toggle and one row per plot."""
        for title, column in COLUMN_TITLES:
            ttk.Label(self.frame, text=title, style=STYLE_COLUMN_HEADER).grid(
                row=1, column=column, padx=5, pady=5
            )
        self.show_map_var = tk.BooleanVar(value=self.canvas.show_map)
        map_checkbutton = ttk.Checkbutton(
            self.frame,
            text="Fond de carte (côtes et frontières)",
            variable=self.show_map_var,
            command=self._toggle_map,
        )
        map_checkbutton.grid(row=0, column=0, columnspan=20, sticky="w", padx=5, pady=10)
        ToolTip(map_checkbutton, MAP_HELP)
        self.surface_widgets: dict[int, SurfaceWidgets] = {}
        if len(self.canvas.datasets) == 0:
            return
        for index, surface in enumerate(self.canvas.lines):
            self.surface_widgets[index] = self._build_surface_row(surface, index)

    def _build_surface_row(self, surface: Any, index: int) -> SurfaceWidgets:
        """Create the widgets of one plot.

        Args:
            surface: Surface plot.
            index: Plot index.

        Returns:
            The created widgets.
        """
        row = index + 2
        ttk.Label(self.frame, text=str(index + 1), style=STYLE_COLUMN_HEADER).grid(
            row=row, column=1, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING
        )
        variable_combobox = self._add_variable_combobox(row, index)
        kind_combobox = SurfaceKindCombobox(
            self.frame, self.canvas.surface_kind, partial(self._update_surface_kind, index)
        )
        kind_combobox.grid(row=row, column=8, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING)
        self._add_button(row, 10, "Classes…", partial(self._open_value_range_dialog, index))
        colormap_combobox = self._add_colormap_combobox(row, index, surface.get_cmap().name)
        alpha = surface.get_alpha()
        alpha_spinbox = self._add_spinbox(row, 30, OPACITY_HELP, partial(self._update_alpha, index))
        alpha_spinbox.set_range(ALPHA_RANGE, float(DEFAULT_ALPHA) if alpha is None else alpha)
        size_spinbox = self._add_spinbox(row, 35, SIZE_HELP, partial(self._update_size, index))
        self._sync_size_spinbox(size_spinbox)
        colorbar_var = self._add_colorbar_checkbutton(row, index)
        colorbar_button = self._add_button(
            row, 50, "Réglages…", partial(self._open_colorbar_dialog, index)
        )
        self._update_colorbar_button(colorbar_button)
        return SurfaceWidgets(
            variable_combobox,
            kind_combobox,
            colormap_combobox,
            alpha_spinbox,
            size_spinbox,
            colorbar_var,
            colorbar_button,
        )

    def _add_button(self, row: int, column: int, text: str, command: Any) -> ttk.Button:
        """Add a button to a plot row.

        Args:
            row: Grid row.
            column: Grid column.
            text: Button text.
            command: Button callback.

        Returns:
            The created button.
        """
        button = ttk.Button(self.frame, text=text, command=command, style=STYLE_BUTTON)
        button.grid(row=row, column=column, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING)
        return button

    def _update_colorbar_button(self, button: ttk.Button) -> None:
        """Enable the colorbar settings button only while a colorbar is displayed.

        Args:
            button: The colorbar "Réglages…" button.
        """
        button.state(["!disabled"] if self.canvas.colorbar is not None else ["disabled"])

    def _add_variable_combobox(self, row: int, index: int) -> ttk.Combobox:
        """Create the combobox choosing the plotted variable.

        Args:
            row: Grid row.
            index: Plot index.

        Returns:
            The created combobox.
        """
        variables = list(self.canvas.datasets[0].data_vars)
        combobox = ttk.Combobox(
            self.frame, values=variables, state="readonly", width=20, style=STYLE_COMBOBOX
        )
        combobox.grid(
            row=row, column=5, columnspan=2, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING
        )
        current = self.canvas.xarray_variables["z"]
        combobox.current(variables.index(current) if current in variables else 0)
        combobox.bind("<<ComboboxSelected>>", lambda _event: self._update_z_variable(index))
        return combobox

    def _add_colormap_combobox(self, row: int, index: int, current: str) -> ttk.Combobox:
        """Create the combobox choosing the colormap.

        Args:
            row: Grid row.
            index: Plot index.
            current: Name of the current colormap.

        Returns:
            The created combobox.
        """
        colormaps = colormap_names()
        combobox = ttk.Combobox(
            self.frame, values=colormaps, state="readonly", width=20, style=STYLE_COMBOBOX
        )
        combobox.grid(
            row=row, column=20, columnspan=2, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING
        )
        combobox.current(colormaps.index(current) if current in colormaps else 0)
        combobox.bind("<<ComboboxSelected>>", lambda _event: self._update_colormap(index))
        return combobox

    def _add_spinbox(
        self, row: int, column: int, help_text: str, on_change: Any
    ) -> CheckedSpinbox:
        """Create a numeric spinbox (its range is set by the caller).

        Args:
            row: Grid row.
            column: Grid column.
            help_text: Tooltip text.
            on_change: Called with each new valid value.

        Returns:
            The created spinbox.
        """
        spinbox = CheckedSpinbox(self.frame, on_change)
        spinbox.grid(
            row=row, column=column, columnspan=2, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING
        )
        ToolTip(spinbox, help_text)
        return spinbox

    def _add_colorbar_checkbutton(self, row: int, index: int) -> tk.BooleanVar:
        """Create the checkbutton showing or hiding the colorbar.

        Args:
            row: Grid row.
            index: Plot index.

        Returns:
            The variable bound to the checkbutton.
        """
        colorbar_var = tk.BooleanVar(value=self.canvas.colorbar is not None)
        checkbutton = ttk.Checkbutton(
            self.frame, text="Afficher", variable=colorbar_var, style=STYLE_CHECKBUTTON
        )
        checkbutton.grid(row=row, column=40, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING)
        # Bound to the release event, which runs *before* the variable toggles.
        checkbutton.bind("<ButtonRelease-1>", lambda _event: self._toggle_colorbar(index))
        return colorbar_var

    def _open_colorbar_dialog(self, index: int) -> None:
        """Open the colorbar dialog (only when a colorbar is displayed).

        Args:
            index: Plot index.
        """
        if self.canvas.colorbar is not None:
            self.canvas.dialogs.show(
                "colorbar",
                partial(ColorbarDialog, self.window, self.canvas, self.canvas.colorbar, index),
            )

    def _open_value_range_dialog(self, index: int) -> None:
        """Open the dialog editing value limits and contour classes.

        Args:
            index: Plot index.
        """
        if index < len(self.canvas.lines):
            surface = self.canvas.lines[index]
            self.canvas.dialogs.show(
                f"value_range:{index}",
                partial(ValueRangeDialog, self.window, self.canvas, surface, index),
            )

    def _toggle_colorbar(self, index: int) -> None:
        """Show or hide the colorbar (the variable still holds the old state).

        Args:
            index: Plot index.
        """
        if self.surface_widgets[index].colorbar_var.get():
            self.canvas.hide_colorbar()
        else:
            self.canvas.show_colorbar(index)
        self.redraw()
        self._update_colorbar_button(self.surface_widgets[index].colorbar_button)

    def _update_colormap(self, index: int) -> None:
        """Apply the selected colormap.

        Args:
            index: Plot index.
        """
        colormap = self.surface_widgets[index].colormap_combobox.get()
        set_surface_colormap(self.canvas.lines[index], colormap)
        self.redraw()

    def _update_surface_kind(self, index: int) -> None:
        """Redraw the plot with the selected kind.

        Args:
            index: Plot index.
        """
        kind = self.surface_widgets[index].kind_combobox.kind
        if kind != self.canvas.surface_kind:
            self.canvas.set_surface_kind(kind, index)
            self._sync_size_spinbox(self.surface_widgets[index].size_spinbox)
            self.redraw()

    def _sync_size_spinbox(self, spinbox: CheckedSpinbox) -> None:
        """Show the size of the current kind, or disable the spinbox when it has none.

        Args:
            spinbox: The "Taille" spinbox.
        """
        kind = self.canvas.surface_kind
        if kind not in SURFACE_SIZE_RANGES:
            spinbox.state(["disabled"])
            spinbox.variable.set("")
            return
        spinbox.state(["!disabled"])
        spinbox.set_range(SURFACE_SIZE_RANGES[kind], self.canvas.surface_sizes[kind])

    def _update_size(self, index: int, size: float) -> None:
        """Apply a line width or marker area.

        Args:
            index: Plot index.
            size: New size.
        """
        self.canvas.set_surface_size(size, index)
        self.redraw()

    def _update_alpha(self, index: int, alpha: float) -> None:
        """Apply a transparency.

        Args:
            index: Plot index.
            alpha: New transparency (0 = transparent, 1 = opaque).
        """
        self.canvas.lines[index].set_alpha(alpha)
        self.redraw()

    def _update_z_variable(self, index: int) -> None:
        """Re-plot with the selected variable.

        Args:
            index: Plot index.
        """
        selected = self.surface_widgets[index].variable_combobox.get()
        if selected in self.canvas.datasets[index].data_vars:
            self.canvas.xarray_variables["z"] = selected
            self.canvas.view_parameters = self.canvas.get_current_parameters()
            self.canvas.update_plot()

    def _toggle_map(self) -> None:
        """Switch between a geographic map and plain axes, then re-plot."""
        self.canvas.show_map = self.show_map_var.get()
        self.canvas.update_plot(is_map=self.canvas.show_map)

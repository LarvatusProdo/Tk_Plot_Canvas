"""Settings tab "Graphique 3D": variable, colormap, alpha and colorbar of maps."""

import tkinter as tk
from dataclasses import dataclass
from functools import partial
from tkinter import messagebox, ttk
from typing import Any, Optional

from ..compat import colormap_names
from ..config import (
    ALPHA_RANGE,
    COLORBAR_VERTICAL,
    DEFAULT_ALPHA,
    STYLE_BUTTON,
    STYLE_CHECKBUTTON,
    STYLE_COLUMN_HEADER,
    STYLE_COMBOBOX,
    STYLE_SECTION_TITLE,
    STYLE_SPINBOX,
)
from .base_tab import SettingsTab
from .colorbar_dialog import ColorbarDialog
from .value_range_dialog import ValueRangeDialog

COLUMN_TITLES = (
    ("Indice", 1),
    ("Variable affichée", 5),
    ("Plage de valeur", 10),
    ("Couleur", 20),
    ("Transparence", 30),
    ("Affichage colorbar", 40),
    ("Paramètre colorbar", 50),
)
ALPHA_EVENTS = ("<Return>", "<FocusOut>", "<KeyRelease>", "<MouseWheel>", "<ButtonRelease-1>")
CELL_PADDING = (10, 10)


@dataclass
class SurfaceWidgets:
    """Widgets editing one filled-contour plot."""

    variable_combobox: ttk.Combobox
    colormap_combobox: ttk.Combobox
    alpha_var: tk.StringVar
    colorbar_var: tk.BooleanVar


class SurfaceTab(SettingsTab):
    """Edit the filled-contour plots of 2D xarray datasets.

    Attributes:
        surface_widgets: Widgets of each plot, indexed by plot index.
    """

    def build(self) -> None:
        """Create the column titles, the map toggle and one row per plot."""
        ttk.Label(self.frame, text="Paramètres du graphique 3D:", style=STYLE_SECTION_TITLE).grid(
            row=0, column=0, sticky="w", padx=5, pady=10, columnspan=10
        )
        for title, column in COLUMN_TITLES:
            ttk.Label(self.frame, text=title, style=STYLE_COLUMN_HEADER).grid(
                row=1, column=column, padx=5, pady=5
            )
        self.show_map_var = tk.BooleanVar(value=self.canvas.show_map)
        ttk.Checkbutton(
            self.frame,
            text="Affichage d'une carte",
            variable=self.show_map_var,
            command=self._toggle_map,
        ).grid(row=0, column=20, padx=5, pady=5)
        self.surface_widgets: dict[int, SurfaceWidgets] = {}
        self._last_colorbar_label: Optional[str] = None
        if len(self.canvas.datasets) == 0:
            return
        for index, surface in enumerate(self.canvas.lines):
            self.surface_widgets[index] = self._build_surface_row(surface, index)

    def _build_surface_row(self, surface: Any, index: int) -> SurfaceWidgets:
        """Create the widgets of one plot.

        Args:
            surface: Filled-contour set.
            index: Plot index.

        Returns:
            The created widgets.
        """
        row = index + 2
        ttk.Label(self.frame, text=str(index + 1), style=STYLE_COLUMN_HEADER).grid(
            row=row, column=1, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING
        )
        variable_combobox = self._add_variable_combobox(row, index)
        self._add_button(row, 10, "Valeurs", partial(self._open_value_range_dialog, index))
        colormap_combobox = self._add_colormap_combobox(row, index, surface.get_cmap().name)
        alpha_var = self._add_alpha_spinbox(row, index, surface.get_alpha())
        colorbar_var = self._add_colorbar_checkbutton(row, index)
        self._add_button(row, 50, "Modifier colorbar", partial(self._open_colorbar_dialog, index))
        return SurfaceWidgets(variable_combobox, colormap_combobox, alpha_var, colorbar_var)

    def _add_button(self, row: int, column: int, text: str, command: Any) -> None:
        """Add a button to a plot row.

        Args:
            row: Grid row.
            column: Grid column.
            text: Button text.
            command: Button callback.
        """
        ttk.Button(self.frame, text=text, command=command, style=STYLE_BUTTON).grid(
            row=row, column=column, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING
        )

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

    def _add_alpha_spinbox(self, row: int, index: int, alpha: Optional[float]) -> tk.StringVar:
        """Create the transparency spinbox.

        Args:
            row: Grid row.
            index: Plot index.
            alpha: Current transparency (None = opaque).

        Returns:
            The variable bound to the spinbox.
        """
        alpha_var = tk.StringVar(value=str(alpha) if alpha is not None else DEFAULT_ALPHA)
        minimum, maximum, increment = ALPHA_RANGE
        spinbox = ttk.Spinbox(
            self.frame,
            from_=minimum,
            to=maximum,
            increment=increment,
            width=5,
            style=STYLE_SPINBOX,
            textvariable=alpha_var,
        )
        spinbox.grid(
            row=row, column=30, columnspan=2, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING
        )
        for sequence in ALPHA_EVENTS:
            spinbox.bind(sequence, lambda _event: self._update_alpha(index))
        return alpha_var

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
            ColorbarDialog(self.window, self.canvas, self.canvas.colorbar, index)

    def _open_value_range_dialog(self, index: int) -> None:
        """Open the dialog editing value limits and contour classes.

        Args:
            index: Plot index.
        """
        if index < len(self.canvas.lines):
            ValueRangeDialog(self.window, self.canvas, self.canvas.lines[index], index)

    def _toggle_colorbar(self, index: int) -> None:
        """Show or hide the colorbar (the variable still holds the old state).

        Args:
            index: Plot index.
        """
        was_shown = self.surface_widgets[index].colorbar_var.get()
        canvas = self.canvas
        if not was_shown:
            canvas.colorbar = canvas.figure.colorbar(
                canvas.lines[index], ax=canvas.axes, orientation=COLORBAR_VERTICAL
            )
            canvas.colorbar.set_label((self._last_colorbar_label or "").capitalize())
        elif canvas.colorbar is not None:
            self._last_colorbar_label = canvas.colorbar.ax.get_ylabel()
            canvas.colorbar.remove()
        self.redraw()

    def _update_colormap(self, index: int) -> None:
        """Apply the selected colormap.

        Args:
            index: Plot index.
        """
        self.canvas.lines[index].set_cmap(self.surface_widgets[index].colormap_combobox.get())
        self.redraw()

    def _update_alpha(self, index: int) -> None:
        """Apply the typed transparency (between 0 and 1).

        Args:
            index: Plot index.
        """
        try:
            alpha = float(self.surface_widgets[index].alpha_var.get())
            if not 0.0 <= alpha <= 1.0:
                raise ValueError("Alpha must be between 0.0 and 1.0")
            self.canvas.lines[index].set_alpha(alpha)
            self.redraw()
        except ValueError:
            messagebox.showerror(
                "Invalid input",
                "Please enter a valid numeric value for alpha between 0.0 and 1.0.",
            )

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

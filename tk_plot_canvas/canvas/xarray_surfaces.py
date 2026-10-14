"""Plotting of two-dimensional xarray datasets as filled contours (maps)."""

from tkinter import messagebox
from typing import Any, Optional

import numpy as np
import xarray as xr

from ..config import BORDER_WIDTH, COASTLINE_WIDTH, GEOGRAPHIC_DIMENSIONS
from .xarray_curves import label_with_units

try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    CARTOPY_INSTALLED = True
except Exception:  # cartopy may fail with errors other than ImportError
    CARTOPY_INSTALLED = False


class XarraySurfacePlotMixin:
    """Plot 2D datasets (requires :class:`PlotHelpersMixin` and the colorbar mixin)."""

    def _plot_xarray_surface(
        self,
        ds: xr.Dataset,
        *,
        title: Optional[str] = None,
        grid: bool = True,
        clear: bool = True,
        legend: bool = False,
        label: Optional[dict] = None,
        replot: bool = False,
        is_map: Optional[bool] = None,
        **plot_kwargs: Any,
    ) -> None:
        """Plot a two-dimensional dataset as filled contours with a colorbar.

        Args:
            ds: Dataset with two dimensions.
            title: Plot title.
            grid: Unused for filled contours.
            clear: Whether to clear the previous plot and colorbar first.
            legend: Unused for filled contours.
            label: Plot metadata shown in the cartouche.
            replot: True when re-plotting an already registered dataset.
            is_map: Accepted for compatibility; the map mode is driven by
                ``show_map`` and by longitude/latitude dimensions.
            **plot_kwargs: Unused.
        """
        if clear:
            self._reset_plot_data()
            self.remove_colorbar()
        x_name, y_name, z_name = self._select_surface_variables(ds)
        self._setup_map_axes(self._is_map_requested(x_name, y_name))
        values = self._surface_values(ds, x_name, y_name, z_name)
        if values is None:
            return
        x_values, y_values, z_values = values
        self._detect_date_axis(x_values, "x")
        self._detect_date_axis(y_values, "y")
        surface = self.axes.contourf(x_values, y_values, z_values, antialiased=False)
        self._replace_colorbar(surface, label_with_units(ds, z_name))
        self._register_plot(surface, label)
        self._update_cartouche_for_new_plot(label, replot)
        self._apply_surface_texts(title, x_name.capitalize(), y_name.capitalize())
        self._finish_surface_plot()

    def _finish_surface_plot(self) -> None:
        """Apply the loaded view, show both axes and redraw."""
        if self.view_parameters != {} and self.view_parameters is not None:
            self.load_parameters(parameters_to_load=self.view_parameters)
        self.axes.xaxis.set_visible(True)
        self.axes.yaxis.set_visible(True)
        self.figure_canvas.draw()

    def _select_surface_variables(self, ds: xr.Dataset) -> tuple[str, str, str]:
        """Choose the x/y dimensions and the plotted variable, and remember them.

        By default, x and y are the two dimensions of the plotted variable.

        Args:
            ds: Dataset holding a two-dimensional variable.

        Returns:
            ``(x_name, y_name, z_name)``.
        """
        known_names = list(ds.dims) + list(ds.data_vars)
        selection = self.xarray_variables
        z_name = selection["z"] if selection["z"] in known_names else list(ds.data_vars)[0]
        dimensions = list(ds[z_name].dims) if z_name in ds.data_vars else list(ds.dims)
        x_name = selection["x"] if selection["x"] in dimensions else dimensions[0]
        y_name = selection["y"] if selection["y"] in dimensions else dimensions[1]
        if x_name == y_name:
            x_name, y_name = dimensions[0], dimensions[1]
        selection.update(x=x_name, y=y_name, z=z_name)
        return x_name, y_name, z_name

    def _is_map_requested(self, x_name: str, y_name: str) -> bool:
        """Tell whether the plot should be drawn on a geographic map.

        Args:
            x_name: Dimension plotted along x.
            y_name: Dimension plotted along y.

        Returns:
            ``show_map`` for longitude/latitude data, False otherwise.
        """
        lower_names = [x_name.lower(), y_name.lower()]
        is_geographic = all(name in lower_names for name in GEOGRAPHIC_DIMENSIONS)
        return self.show_map if is_geographic else False

    def _setup_map_axes(self, is_map: bool) -> None:
        """Replace the axes by a PlateCarree map when requested and possible.

        Args:
            is_map: Whether a map is requested.
        """
        if not (is_map and CARTOPY_INSTALLED):
            self.show_map = False
            return
        subplot_spec = self.axes.get_subplotspec()
        self.axes.remove()
        self.axes = self.figure.add_subplot(subplot_spec, projection=ccrs.PlateCarree())
        self.axes.add_feature(cfeature.COASTLINE, linewidth=COASTLINE_WIDTH)
        self.axes.add_feature(cfeature.BORDERS, linewidth=BORDER_WIDTH)
        self.axes.xaxis.set_visible(True)
        self.axes.yaxis.set_visible(True)
        self.show_map = True

    def _surface_values(
        self, ds: xr.Dataset, x_name: str, y_name: str, z_name: str
    ) -> Optional[tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """Extract coordinates and values, with ``z`` shaped as ``(len(y), len(x))``.

        Args:
            ds: Dataset to plot.
            x_name: Dimension plotted along x.
            y_name: Dimension plotted along y.
            z_name: Plotted variable.

        Returns:
            ``(x, y, z)`` arrays, or None (after an error dialog) when the
            shapes are inconsistent.
        """
        x_values = ds[x_name].values
        y_values = ds[y_name].values
        z_values = ds[z_name].values
        if (len(y_values), len(x_values)) == z_values.shape:
            return x_values, y_values, z_values
        if (len(x_values), len(y_values)) == z_values.shape:
            return x_values, y_values, z_values.T
        messagebox.showerror(
            "Error",
            "Dimensions of x, y, and z are inconsistent for contourf plotting. "
            f"x: {len(x_values)}, y: {len(y_values)}, z: {z_values.shape}",
            parent=self,
        )
        return None

    def _replace_colorbar(self, surface: Any, label: str) -> None:
        """Replace the current colorbar by one attached to ``surface``.

        Args:
            surface: Filled-contour set.
            label: Colorbar label.
        """
        self.remove_colorbar()
        self.create_colorbar(surface)
        self.colorbar.set_label(label)

    def _apply_surface_texts(self, title: Optional[str], x_label: str, y_label: str) -> None:
        """Set the title (when given) and both axis labels.

        Args:
            title: Plot title.
            x_label: X-axis label.
            y_label: Y-axis label.
        """
        if title is not None:
            self.axes.set_title(title)
            self.title_var.set(title)
        self.axes.set_xlabel(x_label)
        self.xlabel_var.set(x_label)
        self.axes.set_ylabel(y_label)
        self.ylabel_var.set(y_label)

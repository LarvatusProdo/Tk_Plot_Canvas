"""Plotting of two-dimensional xarray datasets as surfaces (maps)."""

from tkinter import messagebox
from typing import Any, Optional

import numpy as np
import xarray as xr

from ..config import BORDER_WIDTH, COASTLINE_WIDTH, GEOGRAPHIC_DIMENSIONS
from .surface_kinds import draw_surface
from .xarray_curves import label_with_units

try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    CARTOPY_INSTALLED = True
except Exception:  # cartopy may fail with errors other than ImportError
    CARTOPY_INSTALLED = False

LONGITUDE, LATITUDE = GEOGRAPHIC_DIMENSIONS
RECTILINEAR_AXES = "rectilinear"


def surface_arrays(
    ds: xr.Dataset, x_name: str, y_name: str, z_name: str
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract the coordinates and values of a surface, with ``z`` shaped as ``(y, x)``.

    The orientation of ``z`` follows the dimension names, not the array shapes,
    so that square grids (as many longitudes as latitudes) are not swapped.

    Args:
        ds: Dataset to plot.
        x_name: Dimension plotted along x.
        y_name: Dimension plotted along y.
        z_name: Plotted variable, whose dimensions are exactly ``x_name`` and ``y_name``.

    Returns:
        ``(x, y, z)`` arrays.

    Raises:
        ValueError: If the dimensions of ``z_name`` are not ``x_name`` and ``y_name``.
    """
    z_values = ds[z_name].transpose(y_name, x_name).values
    return ds[x_name].values, ds[y_name].values, z_values


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
        """Plot a two-dimensional dataset as a surface (``surface_kind``) with a colorbar.

        Args:
            ds: Dataset with two dimensions.
            title: Plot title.
            grid: Unused for surfaces.
            clear: Whether to clear the previous plot and colorbar first.
            legend: Unused for surfaces.
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
        self._detect_date_axis(values[0], "x")
        self._detect_date_axis(values[1], "y")
        surface = draw_surface(
            self.axes, self.surface_kind, values, size=self.surface_sizes.get(self.surface_kind)
        )
        self._replace_colorbar(surface, label_with_units(ds, z_name))
        self._apply_default_metadata_keys(label, legend=False)
        self._register_plot(surface, label)
        self._update_cartouche_for_new_plot(label, replot)
        self._apply_surface_texts(title, x_name.capitalize(), y_name.capitalize())
        self._finish_surface_plot()

    def _finish_surface_plot(self) -> None:
        """Apply the loaded view and the axes settings, show both axes and redraw."""
        if self.view_parameters != {} and self.view_parameters is not None:
            self.load_parameters(parameters_to_load=self.view_parameters)
        self.apply_surface_axes_style()
        self.axes.xaxis.set_visible(True)
        self.axes.yaxis.set_visible(True)
        self.figure_canvas.draw()

    def _select_surface_variables(self, ds: xr.Dataset) -> tuple[str, str, str]:
        """Choose the x/y dimensions and the plotted variable, and remember them.

        By default, as in xarray, the last dimension of the plotted variable is
        along x and the first one along y (e.g. longitude along x for data
        stored as ``(latitude, longitude)``).

        Args:
            ds: Dataset holding a two-dimensional variable.

        Returns:
            ``(x_name, y_name, z_name)``.
        """
        known_names = list(ds.dims) + list(ds.data_vars)
        selection = self.xarray_variables
        z_name = selection["z"] if selection["z"] in known_names else list(ds.data_vars)[0]
        dimensions = list(ds[z_name].dims) if z_name in ds.data_vars else list(ds.dims)
        x_name = selection["x"] if selection["x"] in dimensions else dimensions[-1]
        y_name = selection["y"] if selection["y"] in dimensions else dimensions[0]
        if x_name == y_name:
            x_name, y_name = dimensions[-1], dimensions[0]
        selection.update(x=x_name, y=y_name, z=z_name)
        return x_name, y_name, z_name

    def _is_map_requested(self, x_name: str, y_name: str) -> bool:
        """Tell whether the plot should be drawn on a geographic map.

        Args:
            x_name: Dimension plotted along x.
            y_name: Dimension plotted along y.

        Returns:
            ``show_map`` when longitude is along x and latitude along y (the
            PlateCarree layout), False otherwise.
        """
        is_geographic = x_name.lower() == LONGITUDE and y_name.lower() == LATITUDE
        return self.show_map if is_geographic else False

    def _setup_map_axes(self, is_map: bool) -> None:
        """Use a PlateCarree map when requested and possible, plain axes otherwise.

        Args:
            is_map: Whether a map is requested.
        """
        if not (is_map and CARTOPY_INSTALLED):
            self.show_map = False
            if self.axes.name != RECTILINEAR_AXES:
                self._replace_axes()
            return
        self._replace_axes(projection=ccrs.PlateCarree())
        self.axes.add_feature(cfeature.COASTLINE, linewidth=COASTLINE_WIDTH)
        self.axes.add_feature(cfeature.BORDERS, linewidth=BORDER_WIDTH)
        self.axes.xaxis.set_visible(True)
        self.axes.yaxis.set_visible(True)
        self.show_map = True

    def _replace_axes(self, projection: Optional[Any] = None) -> None:
        """Replace the axes by new ones at the same place.

        A map's axes keep their projection when cleared, so they must be
        replaced to go back to plain axes.

        Args:
            projection: Projection of the new axes (None for plain axes).
        """
        subplot_spec = self.axes.get_subplotspec()
        self.axes.remove()
        self.axes = self.figure.add_subplot(subplot_spec, projection=projection)
        self.axes.set_facecolor(self.graph_background_color)

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
            dimensions of ``z_name`` are not ``x_name`` and ``y_name``.
        """
        try:
            return surface_arrays(ds, x_name, y_name, z_name)
        except ValueError:
            messagebox.showerror(
                "Erreur",
                "Les dimensions de x, y et z ne correspondent pas : surface impossible à tracer.\n"
                f"x : {x_name}, y : {y_name}, z : {z_name} {tuple(ds[z_name].dims)}",
                parent=self,
            )
            return None

    def _replace_colorbar(self, surface: Any, label: str) -> None:
        """Replace the current colorbar by one attached to ``surface``.

        Args:
            surface: Plotted surface.
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

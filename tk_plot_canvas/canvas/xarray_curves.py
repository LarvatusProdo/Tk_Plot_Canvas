"""Plotting of xarray datasets: dispatcher and one-dimensional curves."""

from typing import Any, Optional

import xarray as xr

from ..config import PLOT_TYPE_2D, PLOT_TYPE_3D
from ..view import apply_axis_parameters


def label_with_units(dataset: xr.Dataset, name: str) -> str:
    """Build an axis label such as "Temperature (°C)".

    Args:
        dataset: Dataset holding the variable or dimension.
        name: Variable or dimension name.

    Returns:
        The capitalized name, followed by its units when known.
    """
    if "units" in dataset[name].attrs:
        return f"{name.capitalize()} ({dataset[name].attrs['units']})"
    return name.capitalize()


class XarrayCurvePlotMixin:
    """Plot xarray datasets (requires :class:`PlotHelpersMixin`)."""

    def plot_xarray(
        self,
        ds: xr.Dataset,
        *,
        title: Optional[str] = None,
        grid: bool = True,
        clear: bool = True,
        legend: bool = False,
        label: Optional[dict] = None,
        replot: bool = False,
        **plot_kwargs: Any,
    ) -> None:
        """Plot an xarray Dataset: a curve (1 dimension) or a map (2 dimensions).

        Args:
            ds: Dataset to plot.
            title: Plot title.
            grid: Whether to show a grid (curves only).
            clear: Whether to clear the previous plot first.
            legend: Whether to show a legend (when labels are provided).
            label: Metadata shown in the legend and the cartouche.
            replot: True when re-plotting an already registered dataset.
            **plot_kwargs: Passed to the underlying Matplotlib call.

        Raises:
            ValueError: If the dataset has neither 1 nor 2 dimensions.
        """
        if clear:
            self._reset_plot_data()
        if not replot:
            self.datasets.append(ds)
        options = dict(title=title, grid=grid, clear=clear, legend=legend, label=label)
        options.update(replot=replot, **plot_kwargs)
        if len(ds.dims) == 1:
            self.plot_type = PLOT_TYPE_2D
            self._plot_xarray_curve(ds, **options)
        elif len(ds.dims) == 2:
            self.plot_type = PLOT_TYPE_3D
            self._plot_xarray_surface(ds, **options)
        else:
            raise ValueError("The xarray dataset must have either 1 or 2 dimensions for plotting.")

    def _plot_xarray_curve(
        self,
        ds: xr.Dataset,
        *,
        title: Optional[str] = None,
        grid: bool = True,
        clear: bool = True,
        legend: bool = False,
        label: Optional[dict] = None,
        replot: bool = False,
        **plot_kwargs: Any,
    ) -> None:
        """Plot a one-dimensional dataset as a curve.

        Args:
            ds: Dataset with a single dimension.
            title: Plot title (applied only when a view has been loaded).
            grid: Whether to show a grid.
            clear: Unused (clearing is done by :meth:`plot_xarray`).
            legend: Whether to show a legend.
            label: Curve metadata.
            replot: True when re-plotting an already registered dataset.
            **plot_kwargs: Passed to ``Axes.plot``.
        """
        legend_label = self._legend_label_for(label)
        line_kwargs = self._curve_kwargs_from_view(plot_kwargs)
        dimension, variable = self._select_curve_variables(ds)
        x_values = ds[dimension].values
        self._detect_date_axis(x_values, "x")
        (line,) = self.axes.plot(x_values, ds[variable].values, label=legend_label, **line_kwargs)
        self._register_plot(line, label)
        self._update_cartouche_for_new_plot(label, replot)
        self.axes.grid(grid)
        if self.view_parameters != {}:
            self._apply_view_to_curve(ds, title, dimension, variable)
        self._show_legend_if_requested(legend, legend_label)
        self.figure_canvas.draw()

    def _select_curve_variables(self, ds: xr.Dataset) -> tuple[str, str]:
        """Choose the plotted dimension and variable, and remember them.

        The previous selection is reused when it exists in ``ds``.

        Args:
            ds: Dataset with a single dimension.

        Returns:
            ``(dimension, variable)`` names.
        """
        known_names = list(ds.dims) + list(ds.data_vars)
        selection = self.xarray_variables
        dimension = selection["x"] if selection["x"] in known_names else list(ds.dims)[0]
        variable = selection["y"] if selection["y"] in known_names else list(ds.data_vars)[0]
        selection["x"] = dimension
        selection["y"] = variable
        return dimension, variable

    def _apply_view_to_curve(
        self, ds: xr.Dataset, title: Optional[str], dimension: str, variable: str
    ) -> None:
        """Apply the loaded view's axes, title and label fonts to a curve.

        Args:
            ds: Plotted dataset.
            title: Plot title, if any.
            dimension: Name plotted along x.
            variable: Name plotted along y.
        """
        view = self.view_parameters
        apply_axis_parameters(self, "x", view.get("X_axis"))
        apply_axis_parameters(self, "y", view.get("Y_axis"))
        if title is not None and "title" in view:
            self.axes.set_title(title, view["title"])
            self.title_var.set(title)
        if "xlabel" in view:
            x_label = label_with_units(ds, dimension)
            self.axes.set_xlabel(x_label, view["xlabel"])
            self.xlabel_var.set(x_label)
        if "ylabel" in view:
            y_label = label_with_units(ds, variable)
            self.axes.set_ylabel(y_label, view["ylabel"])
            self.ylabel_var.set(y_label)

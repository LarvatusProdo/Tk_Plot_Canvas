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

        The plot type ("2D" or "3D") is defined by the number of dimensions of
        the displayed variable, whatever the ``plot_type`` of a loaded view.

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
            ValueError: If the displayed variable has neither 1 nor 2 dimensions.
        """
        variable = self._displayed_variable(ds)
        dimension_count = ds[variable].ndim
        if dimension_count not in (1, 2):
            raise ValueError(
                "The displayed xarray variable must have either 1 or 2 dimensions for plotting."
            )
        if clear:
            self._reset_plot_data()
        if not replot:
            self.datasets.append(ds)
        options = dict(title=title, grid=grid, clear=clear, legend=legend, label=label)
        options.update(replot=replot, **plot_kwargs)
        if dimension_count == 1:
            self.plot_type = PLOT_TYPE_2D
            self.xarray_variables["y"] = variable
            self._plot_xarray_curve(ds, **options)
        else:
            self.plot_type = PLOT_TYPE_3D
            self.xarray_variables["z"] = variable
            self._plot_xarray_surface(ds, **options)

    def _displayed_variable(self, ds: xr.Dataset) -> str:
        """Return the data variable to display.

        The variable selected for z (surfaces) then for y (curves) is reused
        when it exists in ``ds``; otherwise the first data variable is used.

        Args:
            ds: Dataset to plot.

        Returns:
            Name of the displayed data variable.
        """
        data_variables = list(ds.data_vars)
        for axis_name in ("z", "y"):
            if self.xarray_variables[axis_name] in data_variables:
                return self.xarray_variables[axis_name]
        return data_variables[0]

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
            title: Plot title (with the font of the loaded view, if any).
            grid: Whether to show a grid.
            clear: Unused (clearing is done by :meth:`plot_xarray`).
            legend: Whether to show a legend (by default with the first metadata key).
            label: Curve metadata.
            replot: True when re-plotting an already registered dataset.
            **plot_kwargs: Passed to ``Axes.plot``.
        """
        self._apply_default_metadata_keys(label, legend)
        legend_label = self._legend_label_for(label)
        line_kwargs = self._curve_kwargs_from_view(plot_kwargs)
        dimension, variable = self._select_curve_variables(ds)
        x_values = ds[dimension].values
        self._detect_date_axis(x_values, "x")
        (line,) = self.axes.plot(x_values, ds[variable].values, label=legend_label, **line_kwargs)
        self._register_plot(line, label)
        self._update_cartouche_for_new_plot(label, replot)
        self.axes.grid(grid)
        self._apply_curve_texts(ds, title, dimension, variable)
        if self.view_parameters:
            apply_axis_parameters(self, "x", self.view_parameters.get("X_axis"))
            apply_axis_parameters(self, "y", self.view_parameters.get("Y_axis"))
        self._show_legend_if_requested(legend, legend_label)
        self.figure_canvas.draw()

    def _select_curve_variables(self, ds: xr.Dataset) -> tuple[str, str]:
        """Choose the plotted dimension and variable, and remember them.

        The previous selection is reused when it exists in ``ds``; by default the
        variable is plotted along its own dimension.

        Args:
            ds: Dataset holding a one-dimensional variable.

        Returns:
            ``(dimension, variable)`` names.
        """
        known_names = list(ds.dims) + list(ds.data_vars)
        selection = self.xarray_variables
        variable = selection["y"] if selection["y"] in known_names else list(ds.data_vars)[0]
        default_dimension = ds[variable].dims[0] if variable in ds.data_vars else list(ds.dims)[0]
        is_valid_x = selection["x"] in known_names and selection["x"] != variable
        dimension = selection["x"] if is_valid_x else default_dimension
        selection["x"] = dimension
        selection["y"] = variable
        return dimension, variable

    def _apply_curve_texts(
        self, ds: xr.Dataset, title: Optional[str], dimension: str, variable: str
    ) -> None:
        """Set the title (when given) and both axis labels, with their units.

        Args:
            ds: Plotted dataset.
            title: Plot title, if any.
            dimension: Name plotted along x.
            variable: Name plotted along y.
        """
        if title is not None:
            self._set_axes_text("title", title)
        self._set_axes_text("xlabel", label_with_units(ds, dimension))
        self._set_axes_text("ylabel", label_with_units(ds, variable))

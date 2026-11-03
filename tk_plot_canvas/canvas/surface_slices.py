"""Selection of the slice shown for variables having more than two dimensions."""

from typing import Any

import numpy as np
import xarray as xr

from ..config import PLOT_TYPE_3D, SLICE_VALUE_DECIMALS
from .surface_kinds import surface_levels
from .xarray_surfaces import clamped_index, slice_dimensions


def coordinate_text(coordinate: xr.DataArray) -> str:
    """Format the value of a coordinate for display.

    Args:
        coordinate: Zero-dimensional coordinate (one value of a dimension).

    Returns:
        A "YYYY-MM-DD hh:mm:ss" text for dates, else the rounded value,
        followed by its units when known.
    """
    value = coordinate.values
    if np.issubdtype(value.dtype, np.datetime64):
        text = np.datetime_as_string(value, unit="s").replace("T", " ")
    elif np.issubdtype(value.dtype, np.number):
        text = str(np.round(value, SLICE_VALUE_DECIMALS))
    else:
        text = str(value)
    units = coordinate.attrs.get("units")
    return f"{text} {units}" if units else text


class SurfaceSlicesMixin:
    """Choose the index shown along the dimensions plotted along neither x nor y.

    Requires the host canvas attributes ``datasets``, ``lines``, ``plot_type``,
    ``xarray_variables``, ``slice_indices`` and ``figure_canvas``, and the
    :class:`SurfaceRedrawMixin` methods.
    """

    def _sliced_variable(self) -> Any:
        """Return the plotted variable of the first dataset, if a surface is shown.

        Returns:
            The ``xr.DataArray`` plotted along z, or None.
        """
        if self.plot_type != PLOT_TYPE_3D or len(self.datasets) == 0:
            return None
        z_name = self.xarray_variables["z"]
        dataset = self.datasets[0]
        return dataset[z_name] if z_name in dataset.data_vars else None

    def slice_dimensions(self) -> list[str]:
        """List the dimensions of the plotted variable reduced to a single index.

        Returns:
            The dimensions other than x and y ([] when no surface is shown).
        """
        variable = self._sliced_variable()
        if variable is None:
            return []
        return slice_dimensions(variable, self.xarray_variables["x"], self.xarray_variables["y"])

    def slice_size(self, dimension: str) -> int:
        """Return the number of values of a sliced dimension.

        Args:
            dimension: One of :meth:`slice_dimensions`.

        Returns:
            The length of the dimension.
        """
        return int(self._sliced_variable().sizes[dimension])

    def slice_index(self, dimension: str) -> int:
        """Return the index shown along a sliced dimension.

        Args:
            dimension: One of :meth:`slice_dimensions`.

        Returns:
            The selected index (0 by default).
        """
        return clamped_index(self.slice_indices.get(dimension, 0), self.slice_size(dimension))

    def slice_value_text(self, dimension: str) -> str:
        """Describe the value shown along a sliced dimension.

        Args:
            dimension: One of :meth:`slice_dimensions`.

        Returns:
            The formatted coordinate value at the selected index.
        """
        variable = self._sliced_variable()
        return coordinate_text(variable[dimension][self.slice_index(dimension)])

    def set_slice_index(self, dimension: str, index: int) -> None:
        """Show another slice of every surface, keeping its classes and style.

        Args:
            dimension: One of :meth:`slice_dimensions`.
            index: Index to show along this dimension.
        """
        index = clamped_index(index, self.slice_size(dimension))
        if index == self.slice_index(dimension):
            return
        self.slice_indices[dimension] = index
        # The colorbar follows the last redrawn surface: end with the first one.
        for line_index in reversed(range(len(self.lines))):
            self._redraw_surface(line_index, surface_levels(self.lines[line_index]))
        self.figure_canvas.draw_idle()

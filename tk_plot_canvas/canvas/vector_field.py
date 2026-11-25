"""Vector field (e.g. wind direction) drawn as arrows over a surface plot.

The arrows are drawn with ``Axes.quiver`` from two variables of the first
dataset: the x component (``u``) and the y component (``v``). They follow the
slice shown along the other dimensions, like the surface below them. The
arrow length is fixed from the largest speed of the whole variables, so that
lengths can be compared from one slice to another.
"""

import math
from typing import Any, Optional

import numpy as np
import xarray as xr
from matplotlib.axes import Axes

from ..config import (
    VECTOR_AUTO_ARROW_COUNT,
    VECTOR_FIELD_DEFAULT,
    VECTOR_KEY_POSITION,
    VECTOR_ZORDER,
)
from .xarray_surfaces import surface_arrays

VectorArrays = tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
REFERENCE_DIGITS = 2


def automatic_step(x_size: int, y_size: int) -> int:
    """Choose a step giving about ``VECTOR_AUTO_ARROW_COUNT`` arrows along the longest axis.

    Args:
        x_size: Number of grid nodes along x.
        y_size: Number of grid nodes along y.

    Returns:
        The step (at least 1).
    """
    return max(1, math.ceil(max(x_size, y_size) / VECTOR_AUTO_ARROW_COUNT))


def reference_speed(dataset: xr.Dataset, u_name: str, v_name: str) -> float:
    """Return the largest vector norm of the whole variables, rounded to 2 digits.

    Args:
        dataset: Dataset holding both components.
        u_name: Variable of the x component.
        v_name: Variable of the y component.

    Returns:
        The rounded largest norm (1 when the field is null or empty).
    """
    speed = float(np.hypot(dataset[u_name], dataset[v_name]).max())
    if not math.isfinite(speed) or speed <= 0:
        return 1.0
    return float(f"{speed:.{REFERENCE_DIGITS}g}")


def vector_arrays(
    dataset: xr.Dataset,
    names: tuple[str, str, str, str],
    slice_indices: dict[str, int],
    step: int,
) -> VectorArrays:
    """Extract the sub-sampled coordinates and components of the shown slice.

    Args:
        dataset: Dataset holding both components.
        names: ``(x_name, y_name, u_name, v_name)``.
        slice_indices: Index selected along each other dimension.
        step: One arrow every ``step`` grid nodes (0 = automatic).

    Returns:
        ``(x, y, u, v)``, with ``u`` and ``v`` shaped as ``(len(y), len(x))``.

    Raises:
        ValueError: If x or y is not a dimension of both components.
    """
    x_name, y_name, u_name, v_name = names
    x_values, y_values, u_values = surface_arrays(
        dataset, x_name, y_name, u_name, slice_indices
    )
    v_values = surface_arrays(dataset, x_name, y_name, v_name, slice_indices)[2]
    if step <= 0:
        step = automatic_step(len(x_values), len(y_values))
    grid = (slice(None, None, step), slice(None, None, step))
    return x_values[::step], y_values[::step], u_values[grid], v_values[grid]


def unit_vectors(arrays: VectorArrays) -> VectorArrays:
    """Scale every vector to a norm of 1, keeping its direction (null vectors stay null).

    Args:
        arrays: ``(x, y, u, v)`` from :func:`vector_arrays`.

    Returns:
        ``(x, y, u, v)`` with unit vectors.
    """
    x_values, y_values, u_values, v_values = arrays
    norm = np.hypot(u_values, v_values)
    norm = np.where(norm > 0, norm, 1.0)
    return x_values, y_values, u_values / norm, v_values / norm


def draw_vector_field(
    axes: Axes, arrays: VectorArrays, style: dict[str, Any], reference: tuple[float, str]
) -> list[Any]:
    """Draw the arrows and, if requested, a key showing the reference speed.

    An arrow of the reference speed spans ``length`` times the space between
    two arrows along x. Normalized arrows all have the length of a unit
    vector of speed 1, and no key (their length carries no speed).

    Args:
        axes: Axes to draw on.
        arrays: ``(x, y, u, v)`` from :func:`vector_arrays`.
        style: Vector field settings (see ``VECTOR_FIELD_DEFAULT``).
        reference: Reference speed and its units ("" when unknown).

    Returns:
        The drawn artists (quiver, then key).
    """
    speed, units = reference
    if style["normalize"]:
        arrays, speed = unit_vectors(arrays), 1.0
    arrow_count = max(1, len(arrays[0]))
    quiver = axes.quiver(
        *arrays,
        color=style["color"],
        scale=speed * arrow_count / style["length"],
        scale_units="width",
        zorder=VECTOR_ZORDER,
    )
    if not style["key"] or style["normalize"]:
        return [quiver]
    key = axes.quiverkey(
        quiver,
        *VECTOR_KEY_POSITION,
        speed,
        f"{speed:g} {units}".strip(),
        labelpos="E",
        coordinates="axes",
    )
    return [quiver, key]


def remove_artist(artist: Any) -> None:
    """Remove an artist, ignoring those already removed with their axes.

    Args:
        artist: Matplotlib artist.
    """
    try:
        artist.remove()
    except (ValueError, NotImplementedError, AttributeError):
        pass


class VectorFieldMixin:
    """Draw a vector field over the surface plots.

    Requires the host canvas attributes ``axes``, ``datasets``,
    ``xarray_variables``, ``slice_indices``, ``figure_canvas``, ``vector_field``
    (settings, see ``VECTOR_FIELD_DEFAULT``), ``vector_artists`` (drawn arrows
    and key) and ``vector_reference_cache``.
    """

    def set_vector_field(self, changes: dict[str, Any]) -> None:
        """Change some vector field settings, redraw the arrows and the figure.

        Args:
            changes: Entries of ``vector_field`` to change.
        """
        self.vector_field.update(changes)
        self.draw_vector_field()
        self.figure_canvas.draw_idle()

    def draw_vector_field(self) -> None:
        """Replace the arrows by those of the selected components and slice, if any."""
        self.remove_vector_field()
        dataset = self._vector_dataset()
        if dataset is None:
            return
        selection = self.xarray_variables
        names = (selection["x"], selection["y"], self.vector_field["u"], self.vector_field["v"])
        try:
            arrays = vector_arrays(dataset, names, self.slice_indices, self.vector_field["step"])
            self.vector_artists = draw_vector_field(
                self.axes, arrays, self.vector_field, self._vector_reference(dataset)
            )
        except (ValueError, TypeError):
            # Components not defined on the x/y grid, or non-numeric axes (dates).
            self.remove_vector_field()

    def remove_vector_field(self) -> None:
        """Remove the arrows and their key from the figure."""
        for artist in self.vector_artists:
            remove_artist(artist)
        self.vector_artists = []

    def vector_variable_names(self) -> list[str]:
        """List the variables of the first dataset usable as vector components.

        Returns:
            The data variables having both plotted dimensions ([] without data).
        """
        if not self.datasets:
            return []
        dataset = self.datasets[0]
        plotted = {self.xarray_variables["x"], self.xarray_variables["y"]}
        return [str(name) for name in dataset.data_vars if plotted <= set(dataset[name].dims)]

    def get_vector_field_parameter(self) -> dict[str, Any]:
        """Return the vector field settings for persistence."""
        return dict(self.vector_field)

    def load_vector_field_parameter(self, saved: Optional[dict[str, Any]]) -> None:
        """Restore persisted vector field settings, ignoring ill-typed entries.

        Args:
            saved: "vector_field" entry of the 3D view parameters, if any.
        """
        self.vector_field = dict(VECTOR_FIELD_DEFAULT)
        if not isinstance(saved, dict):
            return
        for key, default in VECTOR_FIELD_DEFAULT.items():
            value = saved.get(key)
            if isinstance(value, type(default)) or (
                isinstance(default, float) and isinstance(value, int)
            ):
                self.vector_field[key] = type(default)(value)

    def _vector_dataset(self) -> Optional[xr.Dataset]:
        """Return the first dataset when it holds both selected components.

        Returns:
            The dataset, or None when the arrows are disabled or cannot be drawn.
        """
        components = (self.vector_field["u"], self.vector_field["v"])
        if not self.vector_field["enabled"] or not self.datasets or not all(components):
            return None
        dataset = self.datasets[0]
        return dataset if all(name in dataset.data_vars for name in components) else None

    def _vector_reference(self, dataset: xr.Dataset) -> tuple[float, str]:
        """Return the reference speed (computed once per dataset and components) and units.

        Args:
            dataset: Dataset holding both components.

        Returns:
            The reference speed and the units of the x component.
        """
        u_name, v_name = self.vector_field["u"], self.vector_field["v"]
        cache_key = (id(dataset), u_name, v_name)
        cache = self.vector_reference_cache
        if cache_key not in cache:
            cache[cache_key] = reference_speed(dataset, u_name, v_name)
        return cache[cache_key], str(dataset[u_name].attrs.get("units", ""))

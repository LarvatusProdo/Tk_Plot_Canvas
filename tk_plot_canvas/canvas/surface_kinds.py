"""Drawing of a surface (2D dataset) with one of the available plot kinds.

Every kind is drawn with classes: contour sets have their own ``levels``,
meshes and scatter plots get a :class:`BoundaryNorm` built from the same bounds,
so that switching kinds keeps the classes, the colormap and the colorbar.
"""

from typing import Any, Optional

import matplotlib
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import BoundaryNorm, Colormap
from matplotlib.ticker import MaxNLocator

from ..config import (
    DEFAULT_CLASS_COUNT,
    SURFACE_KIND_CONTOUR_LINES,
    SURFACE_KIND_FILLED_CONTOURS,
    SURFACE_KIND_MESH,
    SURFACE_KIND_SCATTER,
    SURFACE_SIZE_DEFAULTS,
)


def draw_surface(
    axes: Axes,
    kind: str,
    values: tuple[np.ndarray, np.ndarray, np.ndarray],
    *,
    levels: Optional[Any] = None,
    cmap: Optional[Any] = None,
    alpha: Optional[float] = None,
    size: Optional[float] = None,
) -> Any:
    """Draw a surface with the requested kind.

    Args:
        axes: Axes to draw on.
        kind: One of ``SURFACE_KINDS`` (unknown kinds draw filled contours).
        values: ``(x, y, z)`` arrays, with ``z`` shaped as ``(len(y), len(x))``.
        levels: Class bounds; None lets Matplotlib choose them.
        cmap: Colormap (name or instance); None uses the default one.
        alpha: Transparency (None = opaque).
        size: Line width or marker area for the kinds that have one (None =
            ``SURFACE_SIZE_DEFAULTS``).

    Returns:
        The drawn artist (contour set, mesh or path collection).
    """
    colormap = matplotlib.colormaps.get_cmap(cmap)
    if size is None:
        size = SURFACE_SIZE_DEFAULTS.get(kind)
    if kind in (SURFACE_KIND_MESH, SURFACE_KIND_SCATTER):
        bounds = default_levels(values[2]) if levels is None else levels
        norm = BoundaryNorm(bounds, colormap.N)
        if kind == SURFACE_KIND_MESH:
            return axes.pcolormesh(*values, cmap=colormap, norm=norm, alpha=alpha, shading="auto")
        return _draw_scatter(axes, values, (colormap, norm, alpha), size)
    style: dict[str, Any] = {"cmap": colormap, "alpha": alpha}
    if levels is not None:
        style["levels"] = levels
    if kind == SURFACE_KIND_CONTOUR_LINES:
        return axes.contour(*values, linewidths=size, **style)
    return axes.contourf(*values, antialiased=False, **style)


def _draw_scatter(
    axes: Axes,
    values: tuple[np.ndarray, np.ndarray, np.ndarray],
    colors: tuple[Colormap, BoundaryNorm, Optional[float]],
    size: float,
) -> Any:
    """Draw one colored point per grid node.

    Args:
        axes: Axes to draw on.
        values: ``(x, y, z)`` arrays, with ``z`` shaped as ``(len(y), len(x))``.
        colors: Colormap, classes of the colors and transparency (None = opaque).
        size: Marker area (points²).

    Returns:
        The path collection.
    """
    x_grid, y_grid = np.meshgrid(values[0], values[1])
    colormap, norm, alpha = colors
    return axes.scatter(
        x_grid.ravel(),
        y_grid.ravel(),
        c=np.ravel(values[2]),
        s=size,
        cmap=colormap,
        norm=norm,
        alpha=alpha,
    )


def default_levels(z_values: np.ndarray) -> np.ndarray:
    """Choose class bounds as Matplotlib does for filled contours.

    Args:
        z_values: Plotted values (NaN ignored).

    Returns:
        Rounded, increasing bounds covering the values.
    """
    locator = MaxNLocator(DEFAULT_CLASS_COUNT + 1, min_n_ticks=1)
    return locator.tick_values(float(np.nanmin(z_values)), float(np.nanmax(z_values)))


def surface_levels(surface: Any) -> Optional[np.ndarray]:
    """Return the class bounds of a surface.

    Args:
        surface: Artist drawn by :func:`draw_surface`.

    Returns:
        The bounds, or None when the artist has no classes.
    """
    levels = getattr(surface, "levels", None)
    if levels is not None:
        return np.asarray(levels)
    norm = getattr(surface, "norm", None)
    if isinstance(norm, BoundaryNorm):
        return np.asarray(norm.boundaries)
    return None


def set_surface_colormap(surface: Any, cmap: Any) -> None:
    """Change the colormap of a surface, keeping its classes.

    A :class:`BoundaryNorm` depends on the number of colors of the colormap,
    so it is rebuilt for meshes and scatter plots.

    Args:
        surface: Artist drawn by :func:`draw_surface`.
        cmap: Colormap name or instance.
    """
    surface.set_cmap(cmap)
    norm = getattr(surface, "norm", None)
    if isinstance(norm, BoundaryNorm):
        surface.set_norm(BoundaryNorm(norm.boundaries, surface.get_cmap().N))


def set_surface_size(surface: Any, kind: str, size: float) -> None:
    """Change the line width of contour lines or the marker area of a scatter plot.

    Args:
        surface: Artist drawn by :func:`draw_surface` with ``kind``.
        kind: Kind of the surface (kinds other than lines and scatter are ignored).
        size: Line width (points) or marker area (points²).
    """
    if kind == SURFACE_KIND_CONTOUR_LINES:
        surface.set_linewidth(size)
    elif kind == SURFACE_KIND_SCATTER:
        surface.set_sizes([size])

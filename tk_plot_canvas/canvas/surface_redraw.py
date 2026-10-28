"""Redrawing of a surface plot with new classes or another plot kind."""

from typing import Any

from .surface_kinds import draw_surface, set_surface_size, surface_levels


class SurfaceRedrawMixin:
    """Recreate the surface plots (requires the colorbar mixin).

    Requires the host canvas attributes ``axes``, ``lines``, ``colorbar``,
    ``surface_kind`` and ``surface_sizes``.
    """

    def replace_contour_levels(self, classes: Any, index: int = 0) -> None:
        """Redraw a surface plot with new classes.

        Matplotlib contour levels are immutable, so the surface (and its
        colorbar) is recreated.

        Args:
            classes: New class bounds (list or array, sorted in place).
            index: Index of the plot.
        """
        classes.sort()
        self._redraw_surface(index, classes)

    def set_surface_kind(self, kind: str, index: int = 0) -> None:
        """Redraw a surface plot with another kind, keeping its classes and style.

        Args:
            kind: One of ``SURFACE_KINDS``.
            index: Index of the plot.
        """
        self.surface_kind = kind
        self._redraw_surface(index, surface_levels(self.lines[index]))

    def set_surface_size(self, size: float, index: int = 0) -> None:
        """Change the line width or marker area of the current kind, if it has one.

        Args:
            size: Line width (points) or marker area (points²).
            index: Index of the plot.
        """
        if self.surface_kind in self.surface_sizes:
            self.surface_sizes[self.surface_kind] = size
            set_surface_size(self.lines[index], self.surface_kind, size)

    def _redraw_surface(self, index: int, levels: Any) -> None:
        """Recreate a surface with ``surface_kind``, its colormap, alpha, label and colorbar.

        Args:
            index: Index of the plot.
            levels: Class bounds of the new surface.
        """
        old_surface = self.lines[index]
        orientation, colorbar_label = self._colorbar_state()
        label_font = self._colorbar_label_font()
        new_surface = draw_surface(
            self.axes,
            self.surface_kind,
            self._contour_data(index),
            levels=levels,
            cmap=old_surface.get_cmap(),
            alpha=old_surface.get_alpha(),
            size=self.surface_sizes.get(self.surface_kind),
        )
        new_surface.set_label(old_surface.get_label())
        had_colorbar = self._try_remove_colorbar()
        old_surface.remove()
        self.lines[index] = new_surface
        if had_colorbar:
            self.create_colorbar(new_surface, orientation)
            self.colorbar.set_label(colorbar_label, **label_font)

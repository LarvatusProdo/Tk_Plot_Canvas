"""Axes settings of 3D plots: aspect ratio and grid."""

from typing import Any, Optional, Union

from ..config import ASPECT_CHOICES, SURFACE_AXES_STYLE_DEFAULT

Aspect = Optional[Union[str, float]]


def parse_aspect(value: Any) -> Aspect:
    """Validate an aspect value.

    Args:
        value: None, "equal", "auto" or a positive number (or numeric text).

    Returns:
        The aspect accepted by ``Axes.set_aspect`` (None for the default).

    Raises:
        ValueError: If the value is neither a known keyword nor a positive number.
    """
    if value is None or value in ASPECT_CHOICES.values():
        return value
    number = float(value)
    if number <= 0:
        raise ValueError(f"Aspect must be positive: {value}")
    return number


class SurfaceAxesMixin:
    """Keep the axes settings of 3D plots and re-apply them after each replot.

    Requires the host canvas attributes ``axes``, ``show_map``,
    ``surface_axes_style`` and ``figure_canvas``.
    """

    def set_surface_axes_style(self, style: dict[str, Any]) -> None:
        """Change some axes settings, apply them and redraw.

        Args:
            style: Entries of ``surface_axes_style`` to change.
        """
        self.surface_axes_style.update(style)
        self.apply_surface_axes_style()
        self.figure_canvas.draw()

    def apply_surface_axes_style(self) -> None:
        """Apply ``surface_axes_style`` to the current axes."""
        style = self.surface_axes_style
        aspect = style["aspect"]
        if aspect is None:
            # Cartopy maps are drawn with an equal aspect by default.
            aspect = "equal" if self.show_map else "auto"
        self.axes.set_aspect(aspect, adjustable="box")
        self.axes.grid(style["grid"])

    def get_surface_axes_style_parameter(self) -> dict[str, Any]:
        """Return the axes settings for persistence."""
        return dict(self.surface_axes_style)

    def load_surface_axes_style(self, saved: Optional[dict[str, Any]]) -> None:
        """Restore persisted axes settings, ignoring invalid entries.

        Args:
            saved: "axes_style" entry of the 3D view parameters, if any.
        """
        self.surface_axes_style = dict(SURFACE_AXES_STYLE_DEFAULT)
        if saved:
            self.surface_axes_style.update(self._valid_surface_axes_style(saved))
        self.apply_surface_axes_style()

    @staticmethod
    def _valid_surface_axes_style(saved: dict[str, Any]) -> dict[str, Any]:
        """Keep the known, well-typed entries of persisted axes settings.

        Args:
            saved: "axes_style" entry of the 3D view parameters.

        Returns:
            The usable entries.
        """
        valid: dict[str, Any] = {}
        try:
            valid["aspect"] = parse_aspect(saved.get("aspect"))
        except (TypeError, ValueError):
            pass
        if isinstance(saved.get("grid"), bool):
            valid["grid"] = saved["grid"]
        return valid

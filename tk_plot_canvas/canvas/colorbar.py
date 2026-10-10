"""Colorbar and contour-level operations for filled-contour plots."""

import logging
from typing import Any, Optional

import numpy as np
from matplotlib.axis import Axis
from matplotlib.colorbar import Colorbar

from ..compat import get_colormap
from ..config import (
    CLASS_MODE_AUTO,
    COLORBAR_VERTICAL,
    KEY_LEVELS_AUTO,
    KEY_LEVELS_MANUAL,
)

LOGGER = logging.getLogger(__name__)


def colorbar_label_axis(colorbar: Colorbar) -> Axis:
    """Return the colorbar axis carrying its label.

    Args:
        colorbar: A colorbar.

    Returns:
        The y axis of a vertical colorbar, the x axis of a horizontal one.
    """
    if colorbar.orientation == COLORBAR_VERTICAL:
        return colorbar.ax.yaxis
    return colorbar.ax.xaxis


class ColorbarMixin:
    """Manage the colorbar and the contour levels of the first 3D plot.

    Requires the host canvas attributes ``figure``, ``axes``, ``lines``,
    ``colorbar``, ``datasets``, ``xarray_variables`` and
    ``contour_class_mode``.
    """

    def remove_colorbar(self) -> None:
        """Remove the current colorbar, if any."""
        if self.colorbar is None:
            return
        try:
            self.colorbar.remove()
        except Exception:  # noqa: BLE001 - Matplotlib raises various errors
            pass  # when the colorbar was already removed from the figure.
        self.colorbar = None

    def recreate_colorbar(
        self,
        orientation: str,
        index: int = 0,
        label: Optional[str] = None,
        colorbar: Optional[Colorbar] = None,
    ) -> Optional[Colorbar]:
        """Replace a colorbar by a new one with another orientation.

        The label font (and, by default, the label text) is kept.

        Args:
            orientation: "vertical" or "horizontal".
            index: Index of the plot the colorbar describes.
            label: New label text (defaults to the current one).
            colorbar: Colorbar to replace (defaults to the current one).

        Returns:
            The new colorbar, or None when the old one could not be removed.
        """
        old_colorbar = colorbar if colorbar is not None else self.colorbar
        old_label = colorbar_label_axis(old_colorbar).label
        font = old_label.get_fontproperties()
        text = old_label.get_text() if label is None else label
        try:
            old_colorbar.remove()
        except Exception:  # noqa: BLE001 - see remove_colorbar
            return None
        self.colorbar = self.figure.colorbar(
            self.lines[index], ax=self.axes, orientation=orientation
        )
        self.colorbar.set_label(text, fontproperties=font)
        return self.colorbar

    @staticmethod
    def apply_font_to_colorbar(axis: Optional[Axis], font: dict[str, Any], color: Any) -> None:
        """Apply font properties to a colorbar label, ignoring invalid values.

        Args:
            axis: Colorbar axis carrying the label.
            font: "fontname", "fontsize", "fontstyle" and "fontweight" values.
            color: Label color (ignored when falsy).
        """
        if axis is None:
            return
        label = axis.label
        setters = (
            (label.set_fontname, "fontname"),
            (label.set_fontsize, "fontsize"),
            (label.set_fontstyle, "fontstyle"),
            (label.set_fontweight, "fontweight"),
        )
        for setter, key in setters:
            try:
                setter(font[key])
            except (KeyError, TypeError, ValueError):
                pass
        if color:
            try:
                label.set_color(color)
            except ValueError:
                pass

    def get_current_levels(self, index: int = 0) -> Optional[dict[str, Any]]:
        """Describe the contour levels of a plot for persistence.

        Args:
            index: Index of the plot.

        Returns:
            ``{"Auto": level_count}`` or ``{"Manuel": levels}`` depending on
            ``contour_class_mode``; None when the plot has no levels.
        """
        if index >= len(self.lines) or not hasattr(self.lines[index], "levels"):
            return None
        levels = self.lines[index].levels
        if levels is None:
            return None
        if self.contour_class_mode == CLASS_MODE_AUTO:
            return {KEY_LEVELS_AUTO: len(levels)}
        return {KEY_LEVELS_MANUAL: levels.tolist()}

    def replace_contour_levels(self, classes: Any, index: int = 0) -> None:
        """Redraw a filled-contour plot with new levels.

        Matplotlib contour levels are immutable, so the contour set (and its
        colorbar) is recreated.

        Args:
            classes: New level bounds (list or array, sorted in place).
            index: Index of the plot.
        """
        classes.sort()
        old_surface = self.lines[index]
        orientation, colorbar_label = self._colorbar_state()
        new_surface = self.axes.contourf(
            *self._contour_data(index),
            levels=classes,
            cmap=old_surface.get_cmap(),
            alpha=old_surface.get_alpha(),
            antialiased=False,
        )
        new_surface.set_label(old_surface.get_label())
        had_colorbar = self._try_remove_colorbar()
        old_surface.remove()
        self.lines[index] = new_surface
        if had_colorbar:
            self.colorbar = self.figure.colorbar(
                new_surface, ax=self.axes, orientation=orientation
            )
            self.colorbar.set_label(colorbar_label)

    def _colorbar_state(self) -> tuple[str, str]:
        """Return the orientation and label of the current colorbar.

        Returns:
            ``(orientation, label)``; ("vertical", "") without colorbar.
        """
        if self.colorbar is None:
            return COLORBAR_VERTICAL, ""
        return self.colorbar.orientation, colorbar_label_axis(self.colorbar).label.get_text()

    def _try_remove_colorbar(self) -> bool:
        """Remove the colorbar without forgetting it.

        Returns:
            True when a colorbar existed and was removed.
        """
        if self.colorbar is None:
            return False
        try:
            self.colorbar.remove()
        except Exception:  # noqa: BLE001 - see remove_colorbar
            return False
        return True

    def _contour_data(self, index: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return the x, y and z arrays of a registered dataset.

        Args:
            index: Index of the dataset.

        Returns:
            ``(x, y, z)`` with ``z`` transposed when stored as ``(x, y)``.
        """
        dataset = self.datasets[index]
        x_values = dataset[self.xarray_variables["x"]].values
        y_values = dataset[self.xarray_variables["y"]].values
        z_values = dataset[self.xarray_variables["z"]].values
        if (len(x_values), len(y_values)) == z_values.shape:
            z_values = z_values.T
        return x_values, y_values, z_values

    def apply_3d_parameters(self, parameters: dict[str, Any]) -> None:
        """Apply persisted colorbar, colormap and contour settings.

        Args:
            parameters: "xarray_3D" entry of the view parameters.
        """
        if len(self.lines) == 0:
            return
        self._apply_colorbar_parameters(parameters)
        self._apply_surface_appearance(parameters)
        self._apply_levels(parameters.get("levels"))

    def _apply_colorbar_parameters(self, parameters: dict[str, Any]) -> None:
        """Show or hide the colorbar and restore its orientation and font.

        Args:
            parameters: "xarray_3D" entry of the view parameters.
        """
        if not parameters.get("has_colorbar", False):
            self.remove_colorbar()
            return
        if self.colorbar is None and not self._try_create_colorbar():
            return
        orientation = parameters.get("colorbar_orientation")
        if orientation is not None and orientation != self.colorbar.orientation:
            self.recreate_colorbar(orientation)
        label_axis = colorbar_label_axis(self.colorbar)
        label = label_axis.label.get_text()
        if label:
            self.colorbar.set_label(label)
        font = parameters.get("colorbar_font", False)
        if label and font:
            self.apply_font_to_colorbar(
                label_axis, font, parameters.get("colorlabel_colorbar", False)
            )

    def _try_create_colorbar(self) -> bool:
        """Create a colorbar for the first plot.

        Returns:
            True when the colorbar was created.
        """
        try:
            self.colorbar = self.figure.colorbar(self.lines[0], ax=self.axes)
        except Exception:  # noqa: BLE001 - Matplotlib may refuse the mappable
            self.colorbar = None
            return False
        return True

    def _apply_surface_appearance(self, parameters: dict[str, Any]) -> None:
        """Restore the colormap, color limits and transparency of the first plot.

        Args:
            parameters: "xarray_3D" entry of the view parameters.
        """
        surface = self.lines[0]
        cmap_name = parameters.get("cmap")
        if cmap_name and hasattr(surface, "set_cmap"):
            try:
                surface.set_cmap(get_colormap(cmap_name))
            except (KeyError, ValueError):
                pass
        clim = parameters.get("clim")
        if clim and hasattr(surface, "set_clim"):
            surface.set_clim(clim)
        alpha = parameters.get("alpha")
        if alpha and hasattr(surface, "set_alpha"):
            surface.set_alpha(alpha)

    def _apply_levels(self, levels: Optional[dict[str, Any]]) -> None:
        """Restore the contour levels of the first plot.

        Args:
            levels: ``{"Auto": count}``, ``{"Manuel": bounds}`` or None.
        """
        if levels is None:
            return
        if levels.keys() == {KEY_LEVELS_AUTO}:
            self.contour_class_mode = KEY_LEVELS_AUTO
            surface = self.lines[0]
            if hasattr(surface, "get_array"):
                values = surface.get_array()
                bounds = np.linspace(values.min(), values.max(), levels[KEY_LEVELS_AUTO])
                self.replace_contour_levels(bounds, index=0)
        elif levels.keys() == {KEY_LEVELS_MANUAL}:
            self.contour_class_mode = KEY_LEVELS_MANUAL
            self.replace_contour_levels(levels[KEY_LEVELS_MANUAL], index=0)
        else:
            LOGGER.warning("Unexpected levels format in loaded parameters. Levels not updated.")

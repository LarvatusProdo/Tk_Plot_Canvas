"""Colorbar and contour-level operations for filled-contour plots."""

import logging
from typing import Any, Optional

import numpy as np
from matplotlib.axis import Axis
from matplotlib.colorbar import Colorbar

from ..compat import get_colormap
from ..config import (
    CLASS_MODE_AUTO,
    COLORBAR_LOCATIONS,
    COLORBAR_STYLE_DEFAULT,
    COLORBAR_VERTICAL,
    KEY_COLORBAR_STYLE,
    KEY_LEVELS_AUTO,
    KEY_LEVELS_MANUAL,
    KEY_SURFACE_AXES_STYLE,
    KEY_VALUE_RANGE,
    VALUE_RANGE_DEFAULT,
)
from .xarray_surfaces import surface_arrays

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
    ``colorbar``, ``hidden_colorbar_label``, ``datasets``, ``xarray_variables`` and
    ``contour_class_mode`` and ``contour_value_range``.
    """

    def get_data_range(self, index: int = 0) -> tuple[float, float]:
        """Return the bounds of the z variable of a plot.

        Args:
            index: Index of the dataset.

        Returns:
            ``(minimum, maximum)`` of the z values, ignoring NaN.
        """
        z_values = self._contour_data(index)[2]
        return float(np.nanmin(z_values)), float(np.nanmax(z_values))

    def get_value_range_parameter(self) -> Any:
        """Describe the chosen value range of the automatic classes for persistence.

        Returns:
            ``"valeur par défaut"`` or ``[minimum, maximum]``.
        """
        if self.contour_value_range is None:
            return VALUE_RANGE_DEFAULT
        return list(self.contour_value_range)

    def create_colorbar(self, mappable: Any, orientation: Optional[str] = None) -> Colorbar:
        """Create a colorbar using ``colorbar_style``.

        Args:
            mappable: Filled-contour set the colorbar describes.
            orientation: Forces the orientation (the location is adapted when
                it does not match); None keeps the styled location.

        Returns:
            The new colorbar, also stored in ``self.colorbar``.
        """
        style = self.colorbar_style
        if orientation is not None:
            vertical = style["location"] in ("left", "right")
            if vertical != (orientation == COLORBAR_VERTICAL):
                style["location"] = "right" if orientation == COLORBAR_VERTICAL else "bottom"
        self.colorbar = self.figure.colorbar(
            mappable,
            ax=self.axes,
            location=style["location"],
            shrink=style["shrink"],
            aspect=style["aspect"],
            pad=style["pad"],
            fraction=style["fraction"],
        )
        self.colorbar.ax.tick_params(labelsize=style["tick_labelsize"])
        self.colorbar.outline.set_linewidth(style["outline_width"])
        return self.colorbar

    def set_colorbar_style(self, style: dict[str, Any], index: int = 0) -> None:
        """Change the geometry of the colorbar and redraw it.

        Args:
            style: Entries of ``colorbar_style`` to change.
            index: Index of the plot the colorbar describes.
        """
        self.colorbar_style.update(style)
        if self.colorbar is None:
            return
        label_axis = colorbar_label_axis(self.colorbar)
        text, font = label_axis.label.get_text(), label_axis.label.get_fontproperties()
        color = label_axis.label.get_color()
        if not self._try_remove_colorbar():
            return
        self.create_colorbar(self.lines[index])
        self.colorbar.set_label(text, fontproperties=font, color=color)

    def get_colorbar_style_parameter(self) -> dict[str, Any]:
        """Return the colorbar geometry for persistence."""
        return dict(self.colorbar_style)

    def remove_colorbar(self) -> None:
        """Remove the current colorbar, if any."""
        if self.colorbar is None:
            return
        try:
            self.colorbar.remove()
        except Exception:  # noqa: BLE001 - Matplotlib raises various errors
            pass  # when the colorbar was already removed from the figure.
        self.colorbar = None

    def hide_colorbar(self) -> None:
        """Remove the colorbar, remembering its label text and font.

        The geometry is already kept in ``colorbar_style``.
        """
        if self.colorbar is None:
            return
        self.hidden_colorbar_label = (
            self._colorbar_state()[1],
            self._colorbar_label_font(),
        )
        self.remove_colorbar()

    def set_colorbar_visible(self, visible: bool, index: int = 0) -> None:
        """Show or hide the colorbar, then redraw.

        Args:
            visible: Whether the colorbar is displayed.
            index: Index of the plot the colorbar describes.
        """
        if visible:
            self.show_colorbar(index)
        else:
            self.hide_colorbar()
        self.figure_canvas.draw()

    def show_colorbar(self, index: int = 0) -> None:
        """Display the colorbar with the stored style and the remembered label.

        Args:
            index: Index of the plot the colorbar describes.
        """
        if self.colorbar is not None:
            return
        self.create_colorbar(self.lines[index])
        if self.hidden_colorbar_label is not None:
            text, label_font = self.hidden_colorbar_label
            self.colorbar.set_label(text, **label_font)

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
        self.create_colorbar(self.lines[index], orientation)
        self.colorbar.set_label(text, fontproperties=font, color=old_label.get_color())
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
        label_font = self._colorbar_label_font()
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
            self.create_colorbar(new_surface, orientation)
            self.colorbar.set_label(colorbar_label, **label_font)

    def _colorbar_state(self) -> tuple[str, str]:
        """Return the orientation and label of the current colorbar.

        Returns:
            ``(orientation, label)``; ("vertical", "") without colorbar.
        """
        if self.colorbar is None:
            return COLORBAR_VERTICAL, ""
        return self.colorbar.orientation, colorbar_label_axis(self.colorbar).label.get_text()

    def _colorbar_label_font(self) -> dict[str, Any]:
        """Return the font and color of the current colorbar label.

        Returns:
            ``set_label`` keyword arguments; empty without colorbar.
        """
        if self.colorbar is None:
            return {}
        label = colorbar_label_axis(self.colorbar).label
        return {"fontproperties": label.get_fontproperties().copy(), "color": label.get_color()}

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
            ``(x, y, z)`` with ``z`` shaped as ``(y, x)``.
        """
        selection = self.xarray_variables
        return surface_arrays(self.datasets[index], selection["x"], selection["y"], selection["z"])

    def apply_3d_parameters(self, parameters: dict[str, Any]) -> None:
        """Apply persisted colorbar, colormap and contour settings.

        Args:
            parameters: "xarray_3D" entry of the view parameters.
        """
        if len(self.lines) == 0:
            return
        self._apply_colorbar_parameters(parameters)
        self._apply_surface_appearance(parameters)
        value_range = parameters.get(KEY_VALUE_RANGE, VALUE_RANGE_DEFAULT)
        self.contour_value_range = (
            None if value_range == VALUE_RANGE_DEFAULT else tuple(float(v) for v in value_range)
        )
        self._apply_levels(parameters.get("levels"))
        self.load_surface_axes_style(parameters.get(KEY_SURFACE_AXES_STYLE))

    def _apply_colorbar_parameters(self, parameters: dict[str, Any]) -> None:
        """Show or hide the colorbar and restore its orientation and font.

        Args:
            parameters: "xarray_3D" entry of the view parameters.
        """
        if not parameters.get("has_colorbar", False):
            self.remove_colorbar()
            return
        saved_style = parameters.get(KEY_COLORBAR_STYLE)
        if saved_style:
            self.colorbar_style.update(self._valid_colorbar_style(saved_style))
        if self.colorbar is None:
            if not self._try_create_colorbar():
                return
        elif saved_style:
            self.set_colorbar_style({})
        orientation = parameters.get("colorbar_orientation")
        if not saved_style and orientation is not None and orientation != self.colorbar.orientation:
            self.recreate_colorbar(orientation)
        label_axis = colorbar_label_axis(self.colorbar)
        font = parameters.get("colorbar_font", False)
        if font:
            self.apply_font_to_colorbar(
                label_axis, font, parameters.get("colorlabel_colorbar", False)
            )

    @staticmethod
    def _valid_colorbar_style(saved: dict[str, Any]) -> dict[str, Any]:
        """Keep the known, well-typed entries of a persisted colorbar style.

        Args:
            saved: "colorbar_style" entry of the view parameters.

        Returns:
            The usable entries.
        """
        valid: dict[str, Any] = {}
        for key, default in COLORBAR_STYLE_DEFAULT.items():
            if key not in saved:
                continue
            if key == "location":
                if saved[key] in COLORBAR_LOCATIONS:
                    valid[key] = saved[key]
                continue
            try:
                value = float(saved[key])
            except (TypeError, ValueError):
                continue
            if value > 0:
                valid[key] = value
        return valid

    def _try_create_colorbar(self) -> bool:
        """Create a colorbar for the first plot.

        Returns:
            True when the colorbar was created.
        """
        try:
            self.create_colorbar(self.lines[0])
        except Exception:  # noqa: BLE001 - Matplotlib may refuse the mappable
            self.colorbar = None
            return False
        return True

    def _apply_surface_appearance(self, parameters: dict[str, Any]) -> None:
        """Restore the colormap and transparency of the first plot.

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
            if hasattr(self.lines[0], "levels"):
                v_min, v_max = self.contour_value_range or self.get_data_range(index=0)
                bounds = np.linspace(v_min, v_max, levels[KEY_LEVELS_AUTO])
                self.replace_contour_levels(bounds, index=0)
        elif levels.keys() == {KEY_LEVELS_MANUAL}:
            self.contour_class_mode = KEY_LEVELS_MANUAL
            self.replace_contour_levels(levels[KEY_LEVELS_MANUAL], index=0)
        else:
            LOGGER.warning("Unexpected levels format in loaded parameters. Levels not updated.")

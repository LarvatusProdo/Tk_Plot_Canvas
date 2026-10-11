"""Capture the current state of a plot canvas in the persisted view format.

The dictionary layout (keys and their order) is the JSON file format and
must stay unchanged so that existing view files keep working.
"""

from typing import TYPE_CHECKING, Any, Optional

from matplotlib.axes import Axes
from matplotlib.axis import Axis
from matplotlib.text import Text

from ..config import (
    COLORBAR_HORIZONTAL,
    COLORBAR_VERTICAL,
    CURVE_TYPE_CONTOUR,
    CURVE_TYPE_LINE,
    KEY_COLORBAR_STYLE,
    KEY_VALUE_RANGE,
    KEY_XARRAY_3D,
    PLOT_TYPE_3D,
    STYLE_CARTOUCHE_CELL,
    STYLE_CARTOUCHE_HEADER,
)

if TYPE_CHECKING:
    from ..canvas.plot_canvas import TkPlotCanvas

DEFAULT_LABEL_COLOR = "black"


def capture_view_parameters(canvas: "TkPlotCanvas") -> dict[str, Any]:
    """Capture every persisted setting of a canvas.

    Args:
        canvas: Canvas to inspect.

    Returns:
        The view parameters, ready to be written as JSON.
    """
    master = canvas.master
    parameters = {
        "background_color": canvas.graph_background_color,
        "window_size": (master.winfo_width(), master.winfo_height()),
        "window_position": (master.winfo_x(), master.winfo_y()),
        "X_axis": _capture_axis(canvas.axes, "x"),
        "Y_axis": _capture_axis(canvas.axes, "y"),
        "title": _capture_text_font(canvas.axes.title),
        "xlabel": _capture_text_font(canvas.axes.xaxis.label),
        "ylabel": _capture_text_font(canvas.axes.yaxis.label),
        "plot_type": canvas.plot_type,
        "curves": {str(index): _capture_curve(line) for index, line in enumerate(canvas.lines)},
        "cartouche": _capture_cartouche(canvas),
        "legend": _capture_legend(canvas),
        "xarray_data": dict(canvas.xarray_variables),
    }
    return add_3d_parameters(canvas, parameters)


def _capture_axis(axes: Axes, axis_name: str) -> dict[str, Any]:
    """Capture limits, scale and tick font of one axis.

    Args:
        axes: Matplotlib axes.
        axis_name: "x" or "y".

    Returns:
        The axis parameters.
    """
    axis = axes.xaxis if axis_name == "x" else axes.yaxis
    return {
        "lim": getattr(axes, f"get_{axis_name}lim")(),
        "scale": getattr(axes, f"get_{axis_name}scale")(),
        "autoscale": getattr(axes, f"get_autoscale{axis_name}_on")(),
        "inversion_axis": bool(getattr(axes, f"{axis_name}axis_inverted")()),
        "ticks": _capture_tick_font(axis),
    }


def _capture_tick_font(axis: Axis) -> dict[str, Any]:
    """Capture the font of the first tick label of an axis.

    Args:
        axis: Matplotlib axis.

    Returns:
        Font name, size, style, weight and color (None without ticks).
    """
    tick_labels = axis.get_ticklabels()
    first = tick_labels[0] if len(tick_labels) > 0 else None
    return {
        "name": first.get_fontname() if first is not None else None,
        "size": first.get_fontsize() if first is not None else None,
        "style": first.get_fontstyle() if first is not None else None,
        "weight": first.get_fontweight() if first is not None else None,
        "color": first.get_color() if first is not None else None,
    }


def _capture_text_font(text: Text) -> dict[str, Any]:
    """Capture the font of a title or axis label.

    Args:
        text: Matplotlib text artist.

    Returns:
        Keyword arguments accepted by ``Axes.set_title``/``set_xlabel``.
    """
    font = text.get_fontproperties()
    return {
        "fontname": font.get_name(),
        "fontsize": text.get_fontsize(),
        "fontstyle": font.get_style(),
        "fontweight": font.get_weight(),
        "color": text.get_color(),
    }


def _capture_curve(line: Any) -> dict[str, Any]:
    """Capture the appearance of a plotted line or contour set.

    Args:
        line: ``Line2D`` or contour set.

    Returns:
        The curve parameters, tagged with their "type".
    """
    if hasattr(line, "get_cmap"):
        return {
            "type": CURVE_TYPE_CONTOUR,
            "cmap": line.get_cmap().name,
        }
    return {
        "type": CURVE_TYPE_LINE,
        "color": line.get_color(),
        "linewidth": line.get_linewidth(),
        "linestyle": line.get_linestyle(),
        "marker": line.get_marker(),
        "markersize": line.get_markersize(),
    }


def _capture_cartouche(canvas: "TkPlotCanvas") -> dict[str, Any]:
    """Capture the cartouche columns, fonts and visibility.

    Args:
        canvas: Canvas to inspect.

    Returns:
        The cartouche parameters.
    """
    return {
        "cartouche_title_grid": [label.cget("text") for label in canvas.cartouche_headers],
        "cartouche_font_title": canvas.style.configure(STYLE_CARTOUCHE_HEADER),
        "cartouche_font_line": canvas.style.configure(STYLE_CARTOUCHE_CELL),
        "Is_cartouche_display": canvas.show_cartouche,
    }


def _capture_legend(canvas: "TkPlotCanvas") -> dict[str, Any]:
    """Capture the legend keys and visibility flags.

    Args:
        canvas: Canvas to inspect.

    Returns:
        The legend parameters.
    """
    return {
        "displayed_keys": [key for key in canvas.legend_keys if key != ""],
        "Is_legend_display": canvas.show_legend,
        "Is_title_display": canvas.show_legend_key_names,
    }


def add_3d_parameters(canvas: "TkPlotCanvas", parameters: dict[str, Any]) -> dict[str, Any]:
    """Add the colorbar, colormap and contour settings of a 3D plot.

    Args:
        canvas: Canvas to inspect.
        parameters: Parameters to complete in place.

    Returns:
        ``parameters`` with an "xarray_3D" entry (empty for 2D plots).
    """
    if canvas.plot_type == PLOT_TYPE_3D and len(canvas.lines) > 0:
        surface_parameters = _capture_surface(canvas)
        surface_parameters.update(_capture_colorbar_font(canvas.colorbar))
        parameters[KEY_XARRAY_3D] = surface_parameters
    if KEY_XARRAY_3D not in parameters:
        parameters[KEY_XARRAY_3D] = {}
    return parameters


def _capture_surface(canvas: "TkPlotCanvas") -> dict[str, Any]:
    """Capture the appearance of the first filled-contour plot.

    Args:
        canvas: Canvas to inspect.

    Returns:
        Colorbar presence/orientation, colormap, alpha and levels.
    """
    surface = canvas.lines[0]
    colorbar = canvas.colorbar
    return {
        "has_colorbar": colorbar is not None,
        "colorbar_orientation": getattr(colorbar, "orientation", None),
        "cmap": surface.get_cmap().name if hasattr(surface, "get_cmap") else None,
        "alpha": surface.get_alpha() if hasattr(surface, "get_alpha") else None,
        "levels": canvas.get_current_levels(index=0) if hasattr(surface, "levels") else None,
        KEY_VALUE_RANGE: canvas.get_value_range_parameter(),
        "affichage_map": canvas.show_map,
        KEY_COLORBAR_STYLE: canvas.get_colorbar_style_parameter(),
    }


def _capture_colorbar_font(colorbar: Optional[Any]) -> dict[str, Any]:
    """Capture the font and color of the colorbar label.

    Args:
        colorbar: Current colorbar, if any.

    Returns:
        "colorbar_font" and "colorlabel_colorbar" entries, or nothing.
    """
    label = _colorbar_label(colorbar)
    if label is None:
        return {}
    color = label.get_color()
    return {
        "colorbar_font": {
            "fontname": label.get_fontproperties().get_name(),
            "fontsize": label.get_fontsize(),
            "fontstyle": label.get_fontproperties().get_style(),
            "fontweight": label.get_fontproperties().get_weight(),
        },
        "colorlabel_colorbar": color if color is not None else DEFAULT_LABEL_COLOR,
    }


def _colorbar_label(colorbar: Optional[Any]) -> Optional[Text]:
    """Return the label artist of a colorbar according to its orientation.

    Args:
        colorbar: Colorbar, if any.

    Returns:
        The label text artist, or None.
    """
    if colorbar is None or not hasattr(colorbar, "ax"):
        return None
    if colorbar.orientation == COLORBAR_VERTICAL:
        return colorbar.ax.yaxis.label
    if colorbar.orientation == COLORBAR_HORIZONTAL:
        return colorbar.ax.xaxis.label
    return None

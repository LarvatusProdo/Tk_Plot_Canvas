"""Apply persisted view parameters to a plot canvas."""

import tkinter as tk
from typing import TYPE_CHECKING, Any, Optional

from ..compat import get_colormap
from ..config import (
    CURVE_TYPE_CONTOUR,
    CURVE_TYPE_LINE,
    KEY_CURVE_TYPE,
    KEY_CURVES,
    KEY_PLOT_TYPE,
    KEY_SUBPLOT_PARAMS,
    KEY_XARRAY_3D,
    PLOT_TYPE_2D,
    PLOT_TYPE_3D,
    STYLE_CARTOUCHE_CELL,
    STYLE_CARTOUCHE_HEADER,
    SUBPLOT_PARAM_NAMES,
)
from ..fonts import safe_tk_font_spec

if TYPE_CHECKING:
    from ..canvas.plot_canvas import TkPlotCanvas

Parameters = dict[str, Any]


def plot_type_of(parameters: Parameters) -> str:
    """Return the plot type stored in view parameters.

    Args:
        parameters: View parameters.

    Returns:
        "2D" (default) or "3D".
    """
    return parameters.get(KEY_PLOT_TYPE, PLOT_TYPE_2D)


def effective_plot_type(canvas: "TkPlotCanvas", parameters: Parameters) -> str:
    """Return the plot type to use when applying a view.

    Once data is plotted, the type comes from the data (set by the plotting
    methods) and the ``plot_type`` of the view is ignored. Without data, the
    view's type is used if it is valid.

    Args:
        canvas: Canvas the view is applied to.
        parameters: View parameters.

    Returns:
        "2D" or "3D".
    """
    if canvas.lines or canvas.datasets:
        return canvas.plot_type
    stored_type = plot_type_of(parameters)
    return stored_type if stored_type in (PLOT_TYPE_2D, PLOT_TYPE_3D) else canvas.plot_type


def restore_xarray_selection(canvas: "TkPlotCanvas", parameters: Parameters) -> None:
    """Restore the settings that drive the next xarray plots.

    Args:
        canvas: Canvas to update.
        parameters: View parameters.
    """
    if "xarray_data" in parameters:
        selection = parameters["xarray_data"]
        for axis_name in ("x", "y", "z"):
            canvas.xarray_variables[axis_name] = selection.get(axis_name, "")
    canvas.plot_type = effective_plot_type(canvas, parameters)
    if KEY_XARRAY_3D in parameters:
        canvas.show_map = parameters[KEY_XARRAY_3D].get("affichage_map", False)


def apply_view_parameters(canvas: "TkPlotCanvas", parameters: Parameters) -> None:
    """Apply every view setting to the canvas (without redrawing).

    Args:
        canvas: Canvas to update.
        parameters: View parameters; fonts unavailable on this system are
            replaced in place by the default font. Their ``plot_type`` is
            ignored when it does not match the plotted data.
    """
    plot_type = effective_plot_type(canvas, parameters)
    _apply_background(canvas, parameters, plot_type)
    _apply_plot_type_and_window(canvas, parameters, plot_type)
    _apply_subplot_parameters(canvas, parameters.get(KEY_SUBPLOT_PARAMS))
    if "X_axis" in parameters:
        apply_axis_parameters(canvas, "x", parameters["X_axis"])
    if "Y_axis" in parameters:
        apply_axis_parameters(canvas, "y", parameters["Y_axis"])
    _apply_text_fonts(canvas, parameters)
    if plot_type == PLOT_TYPE_2D:
        _apply_curves(canvas, parameters.get(KEY_CURVES))
    if "cartouche" in parameters:
        _apply_cartouche(canvas, parameters["cartouche"])
    if "legend" in parameters:
        _apply_legend(canvas, parameters["legend"])
    if KEY_XARRAY_3D in parameters and plot_type == PLOT_TYPE_3D:
        canvas.apply_3d_parameters(parameters[KEY_XARRAY_3D])


def _apply_background(canvas: "TkPlotCanvas", parameters: Parameters, plot_type: str) -> None:
    """Apply the background color (2D plots only).

    Args:
        canvas: Canvas to update.
        parameters: View parameters.
        plot_type: Effective plot type ("2D" or "3D").
    """
    if "background_color" not in parameters or plot_type != PLOT_TYPE_2D:
        return
    color = parameters["background_color"]
    canvas.graph_background_color = color
    canvas.figure.set_facecolor(color)
    canvas.axes.set_facecolor(color)
    for line in canvas.lines:
        if hasattr(line, "set_color"):
            line.set_color(color)
    canvas.figure_canvas.get_tk_widget().configure(background=color)
    canvas.figure_canvas.draw()


def _apply_subplot_parameters(canvas: "TkPlotCanvas", saved: Optional[Parameters]) -> None:
    """Restore the figure margins and spacing ("Configure subplots" dialog).

    Invalid entries are ignored; inconsistent values (e.g. left >= right)
    leave the layout unchanged.

    Args:
        canvas: Canvas to update.
        saved: "subplot_params" entry of the view parameters, if any.
    """
    if not saved:
        return
    values = {}
    for name in SUBPLOT_PARAM_NAMES:
        try:
            values[name] = float(saved[name])
        except (KeyError, TypeError, ValueError):
            continue
    try:
        canvas.figure.subplots_adjust(**values)
    except ValueError:
        pass


def _apply_plot_type_and_window(
    canvas: "TkPlotCanvas", parameters: Parameters, plot_type: str
) -> None:
    """Apply the plot type and the size/position of the main window.

    Args:
        canvas: Canvas to update.
        parameters: View parameters.
        plot_type: Effective plot type ("2D" or "3D").
    """
    canvas.plot_type = plot_type
    if "window_size" in parameters:
        width, height = parameters["window_size"]
        canvas.master.geometry(f"{width}x{height}")
    if "window_position" in parameters:
        x_position, y_position = parameters["window_position"]
        canvas.master.geometry(f"+{x_position}+{y_position}")


def apply_axis_parameters(
    canvas: "TkPlotCanvas", axis_name: str, parameters: Optional[Parameters]
) -> None:
    """Apply tick font, limits, scale and inversion to one axis.

    Args:
        canvas: Canvas to update.
        axis_name: "x" or "y".
        parameters: Axis parameters ("X_axis"/"Y_axis" entry), or None.
    """
    if parameters is None:
        return
    axes = canvas.axes
    if "ticks" in parameters:
        axis = axes.xaxis if axis_name == "x" else axes.yaxis
        _apply_tick_font(canvas, axis, parameters["ticks"])
    _apply_axis_limits(canvas, axis_name, parameters)
    is_date_axis = getattr(canvas, f"is_date_on_{axis_name}_axis")
    if "scale" in parameters and not is_date_axis:
        getattr(axes, f"set_{axis_name}scale")(parameters["scale"])
    if parameters.get("inversion_axis"):
        getattr(axes, f"invert_{axis_name}axis")()


def _apply_tick_font(canvas: "TkPlotCanvas", axis: Any, tick_parameters: Parameters) -> None:
    """Apply a font to every tick label of an axis.

    Args:
        canvas: Canvas providing the available fonts.
        axis: Matplotlib axis.
        tick_parameters: Tick font parameters.
    """
    font_name = tick_parameters.get("name")
    if font_name not in canvas.matplotlib_fonts:
        font_name = canvas.default_font
    for tick in axis.get_ticklabels():
        tick.set_fontname(font_name)
        tick.set_fontsize(tick_parameters.get("size"))
        tick.set_fontstyle(tick_parameters.get("style"))
        tick.set_fontweight(tick_parameters.get("weight"))
        tick.set_color(tick_parameters.get("color"))


def _apply_axis_limits(canvas: "TkPlotCanvas", axis_name: str, parameters: Parameters) -> None:
    """Apply automatic scaling or explicit limits to one axis.

    Args:
        canvas: Canvas to update.
        axis_name: "x" or "y".
        parameters: Axis parameters.
    """
    set_limits = getattr(canvas.axes, f"set_{axis_name}lim")
    if "autoscale" in parameters:
        if parameters["autoscale"]:
            canvas.axes.autoscale(axis=axis_name, tight=True)
        else:
            set_limits(parameters["lim"])
    elif "lim" in parameters:
        set_limits(parameters["lim"])


def _apply_text_fonts(canvas: "TkPlotCanvas", parameters: Parameters) -> None:
    """Apply the fonts of the title and of both axis labels.

    Args:
        canvas: Canvas to update.
        parameters: View parameters (unknown font names are replaced in place).
    """
    targets = (
        ("title", canvas.title_var, canvas.axes.set_title),
        ("xlabel", canvas.xlabel_var, canvas.axes.set_xlabel),
        ("ylabel", canvas.ylabel_var, canvas.axes.set_ylabel),
    )
    for key, text_var, setter in targets:
        if key not in parameters:
            continue
        if parameters[key].get("fontname") not in canvas.matplotlib_fonts:
            parameters[key]["fontname"] = canvas.default_font
        setter(text_var.get(), **parameters[key].copy())


def _apply_curves(canvas: "TkPlotCanvas", curves: Optional[Parameters]) -> None:
    """Apply the saved appearance of each 2D curve.

    Args:
        canvas: Canvas to update.
        curves: "curves" entry of the view parameters, or None.
    """
    if curves is None:
        return
    for index, line in enumerate(canvas.lines):
        curve = curves.get(str(index))
        if curve is None:
            continue
        if curve.get(KEY_CURVE_TYPE) == CURVE_TYPE_LINE and hasattr(line, "set_color"):
            _apply_line_style(line, curve)
        elif curve.get(KEY_CURVE_TYPE) == CURVE_TYPE_CONTOUR:
            _apply_contour_style(line, curve)


def _apply_line_style(line: Any, curve: Parameters) -> None:
    """Apply color, width, style and markers to a line.

    Args:
        line: Matplotlib ``Line2D``.
        curve: Curve parameters.
    """
    line.set_color(curve.get("color"))
    line.set_linewidth(curve.get("linewidth"))
    line.set_linestyle(curve.get("linestyle"))
    line.set_marker(curve.get("marker"))
    line.set_markersize(curve.get("markersize"))


def _apply_contour_style(contour: Any, curve: Parameters) -> None:
    """Apply the colormap to a contour set (errors ignored).

    Args:
        contour: Matplotlib contour set.
        curve: Curve parameters.
    """
    if hasattr(contour, "set_cmap") and curve.get("cmap"):
        try:
            contour.set_cmap(get_colormap(curve["cmap"]))
        except (KeyError, ValueError):
            pass


def _apply_cartouche(canvas: "TkPlotCanvas", cartouche: Parameters) -> None:
    """Apply cartouche visibility, column titles and fonts.

    Args:
        canvas: Canvas to update.
        cartouche: "cartouche" entry (fonts are sanitized in place).
    """
    header_font = cartouche["cartouche_font_title"]
    cell_font = cartouche["cartouche_font_line"]
    for font in (header_font, cell_font):
        font["font"] = safe_tk_font_spec(font["font"], canvas.default_font, canvas.tkinter_fonts)
    canvas.show_cartouche = cartouche.get("Is_cartouche_display", True)
    if not canvas.show_cartouche:
        try:
            canvas.panedwindow.forget(canvas.cartouche_frame)
        except tk.TclError:
            pass
    canvas.cartouche_keys = cartouche.get("cartouche_title_grid", [])
    titles = cartouche["cartouche_title_grid"]
    for index, label in enumerate(canvas.cartouche_headers[: len(titles)]):
        label.config(text=titles[index])
    canvas.style.configure(
        STYLE_CARTOUCHE_HEADER, font=header_font["font"], foreground=header_font["foreground"]
    )
    canvas.style.configure(
        STYLE_CARTOUCHE_CELL, font=cell_font["font"], foreground=cell_font["foreground"]
    )


def _apply_legend(canvas: "TkPlotCanvas", legend: Parameters) -> None:
    """Apply legend keys and visibility flags, then refresh the legend.

    Args:
        canvas: Canvas to update.
        legend: "legend" entry of the view parameters.
    """
    canvas.legend_keys = legend.get("displayed_keys", [])
    for index, line in enumerate(canvas.lines):
        label = canvas.line_labels[index]
        line.set_label(canvas.build_legend_label(label, show_keys=True))
    canvas.show_legend = legend.get("Is_legend_display", False)
    canvas.show_legend_key_names = legend.get("Is_title_display", False)
    canvas.refresh_legend()

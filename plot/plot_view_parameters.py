"""Capture and persist plotting view parameters."""

import json


def write_parameters(path, parameters):
    """Write plot parameters to a JSON file."""
    with open(path, "w") as file:
        json.dump(parameters, file, indent=4)


def read_parameters(path):
    """Read plot parameters from a JSON file."""
    with open(path, "r") as file:
        return json.load(file)


def get_current_parameters(canvas):
    """Capture the current plot state in the persisted view format."""
    parameters = {
        "background_color": canvas.bg_color_graph,
        "window_size": (canvas.master.winfo_width(), canvas.master.winfo_height()),
        "window_position": (canvas.master.winfo_x(), canvas.master.winfo_y()),
        "X_axis": {
            "lim": canvas.axes.get_xlim(),
            "scale": canvas.axes.get_xscale(),
            "autoscale": canvas.axes.get_autoscalex_on(),
            "inversion_axis": bool(canvas.axes.xaxis_inverted()),
            "ticks": {
                "name": canvas.axes.xaxis.get_ticklabels()[0].get_fontname() if len(canvas.axes.xaxis.get_ticklabels()) > 0 else None,
                "size": canvas.axes.xaxis.get_ticklabels()[0].get_fontsize() if len(canvas.axes.xaxis.get_ticklabels()) > 0 else None,
                "style": canvas.axes.xaxis.get_ticklabels()[0].get_fontstyle() if len(canvas.axes.xaxis.get_ticklabels()) > 0 else None,
                "weight": canvas.axes.xaxis.get_ticklabels()[0].get_fontweight() if len(canvas.axes.xaxis.get_ticklabels()) > 0 else None,
                "color": canvas.axes.xaxis.get_ticklabels()[0].get_color() if len(canvas.axes.xaxis.get_ticklabels()) > 0 else None,
            },
        },
        "Y_axis": {
            "lim": canvas.axes.get_ylim(),
            "scale": canvas.axes.get_yscale(),
            "autoscale": canvas.axes.get_autoscaley_on(),
            "inversion_axis": bool(canvas.axes.yaxis_inverted()),
            "ticks": {
                "name": canvas.axes.yaxis.get_ticklabels()[0].get_fontname() if len(canvas.axes.yaxis.get_ticklabels()) > 0 else None,
                "size": canvas.axes.yaxis.get_ticklabels()[0].get_fontsize() if len(canvas.axes.yaxis.get_ticklabels()) > 0 else None,
                "style": canvas.axes.yaxis.get_ticklabels()[0].get_fontstyle() if len(canvas.axes.yaxis.get_ticklabels()) > 0 else None,
                "weight": canvas.axes.yaxis.get_ticklabels()[0].get_fontweight() if len(canvas.axes.yaxis.get_ticklabels()) > 0 else None,
                "color": canvas.axes.yaxis.get_ticklabels()[0].get_color() if len(canvas.axes.yaxis.get_ticklabels()) > 0 else None,
            },
        },
        "title": {
            "fontname": canvas.axes.title.get_fontproperties().get_name(),
            "fontsize": canvas.axes.title.get_fontsize(),
            "fontstyle": canvas.axes.title.get_fontproperties().get_style(),
            "fontweight": canvas.axes.title.get_fontproperties().get_weight(),
            "color": canvas.axes.title.get_color(),
        },
        "xlabel": {
            "fontname": canvas.axes.xaxis.label.get_fontproperties().get_name(),
            "fontsize": canvas.axes.xaxis.label.get_fontsize(),
            "fontstyle": canvas.axes.xaxis.label.get_fontproperties().get_style(),
            "fontweight": canvas.axes.xaxis.label.get_fontproperties().get_weight(),
            "color": canvas.axes.xaxis.label.get_color(),
        },
        "ylabel": {
            "fontname": canvas.axes.yaxis.label.get_fontproperties().get_name(),
            "fontsize": canvas.axes.yaxis.label.get_fontsize(),
            "fontstyle": canvas.axes.yaxis.label.get_fontproperties().get_style(),
            "fontweight": canvas.axes.yaxis.label.get_fontproperties().get_weight(),
            "color": canvas.axes.yaxis.label.get_color(),
        },
        "plot_type": getattr(canvas, "type_plot", "2D"),
        "curves": {
            str(index): (
                {
                    "type": "contour",
                    "cmap": line.get_cmap().name if hasattr(line, "get_cmap") else None,
                    "clim": tuple(line.get_clim()) if hasattr(line, "get_clim") else None,
                }
                if hasattr(line, "get_cmap")
                else {
                    "type": "line",
                    "color": line.get_color(),
                    "linewidth": line.get_linewidth(),
                    "linestyle": line.get_linestyle(),
                    "marker": line.get_marker(),
                    "markersize": line.get_markersize(),
                }
            )
            for index, line in enumerate(canvas._lines)
        },
        "cartouche": {
            "cartouche_title_grid": [label.cget("text") for label in canvas._cartouche_title_grid],
            "cartouche_font_title": canvas.style.configure("Cartouche_titre.TLabel"),
            "cartouche_font_line": canvas.style.configure("Cartouche.TLabel"),
            "Is_cartouche_display": canvas.Is_cartouche_display,
        },
        "legend": {
            "displayed_keys": [key for key in canvas.legend_to_show if key != ""]
            if len(canvas.legend_to_show) > 0
            else [],
            "Is_legend_display": canvas.Is_legend_display,
            "Is_title_display": canvas.Is_title_display,
        },
        "xarray_data": {
            "x": canvas.xarray_data["x"],
            "y": canvas.xarray_data["y"],
            "z": canvas.xarray_data["z"] if "z" in canvas.xarray_data else None,
        },
    }
    return get_3D_parameters(canvas, parameters)


def get_3D_parameters(canvas, parameters):
    """Add colorbar, colormap, and contour settings for 3D plots."""
    if getattr(canvas, "type_plot", "") == "3D" and len(canvas._lines) > 0:
        parameters["xarray_3D"] = {
            "has_colorbar": canvas._colorbar is not None,
            "colorbar_orientation": canvas._colorbar.orientation
            if canvas._colorbar is not None and hasattr(canvas._colorbar, "orientation")
            else None,
            "cmap": canvas._lines[0].get_cmap().name
            if hasattr(canvas._lines[0], "get_cmap")
            else None,
            "clim": tuple(canvas._lines[0].get_clim())
            if hasattr(canvas._lines[0], "get_clim")
            else None,
            "alpha": canvas._lines[0].get_alpha()
            if hasattr(canvas._lines[0], "get_alpha")
            else None,
            "levels": canvas.get_current_levels(index=0)
            if hasattr(canvas._lines[0], "levels")
            else None,
            "affichage_map": canvas.plot_3D_map,
        }

        if canvas._colorbar is not None and hasattr(canvas._colorbar, "ax"):
            if canvas._colorbar.orientation == "vertical":
                colorbar_label = canvas._colorbar.ax.yaxis.label
            elif canvas._colorbar.orientation == "horizontal":
                colorbar_label = canvas._colorbar.ax.xaxis.label
            else:
                colorbar_label = None

            if colorbar_label is not None:
                parameters["xarray_3D"]["colorbar_font"] = {
                    "fontname": colorbar_label.get_fontproperties().get_name(),
                    "fontsize": colorbar_label.get_fontsize(),
                    "fontstyle": colorbar_label.get_fontproperties().get_style(),
                    "fontweight": colorbar_label.get_fontproperties().get_weight(),
                }
                color = colorbar_label.get_color()
                parameters["xarray_3D"]["colorlabel_colorbar"] = color if color is not None else "black"

    if "xarray_3D" not in parameters:
        parameters["xarray_3D"] = {}

    return parameters


def update_variables_from_parameters(canvas, parameters):
    """Restore plotting variables that affect subsequent xarray plots."""
    if "xarray_data" in parameters:
        canvas.xarray_data["x"] = parameters["xarray_data"].get("x", "")
        canvas.xarray_data["y"] = parameters["xarray_data"].get("y", "")
        canvas.xarray_data["z"] = parameters["xarray_data"].get("z", "")

    if "plot_type" in parameters:
        canvas.type_plot = parameters["plot_type"]

    if "xarray_3D" in parameters:
        canvas.plot_3D_map = parameters["xarray_3D"].get("affichage_map", False)

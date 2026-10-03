"""Colorbar and contour-level operations for the plot canvas."""

import matplotlib
from numpy import linspace


class ColorbarContourMixin:
    """Manage colorbar formatting and 3D contour levels."""

    def change_orientation_colorbar(self, colorbar, orientation, index=0):
        """Remove the previous colorbar and apply the new orientation."""
        current_font = colorbar.label.get_fontproperties()
        current_label = colorbar.ax.get_ylabel() if orientation == "vertical" else colorbar.ax.get_xlabel()

        try:
            colorbar.remove()
        except Exception:
            return

        colorbar = self.master.master.figure.colorbar(self._lines[index], ax=self.axes, orientation=orientation)
        if current_label is not None:
            colorbar.set_label(current_label, fontproperties=current_font)

        return colorbar

    def apply_font_to_the_colorbar(self, colorbar_axis, current_font, color):
        """Apply the selected font properties to the colorbar label."""
        if colorbar_axis is not None:
            try:
                colorbar_axis.label.set_fontname(current_font["fontname"])
            except Exception:
                pass
            try:
                colorbar_axis.label.set_fontsize(current_font["fontsize"])
            except Exception:
                pass
            try:
                colorbar_axis.label.set_fontstyle(current_font["fontstyle"])
            except Exception:
                pass
            try:
                colorbar_axis.label.set_fontweight(current_font["fontweight"])
            except Exception:
                pass

            try:
                if color:
                    colorbar_axis.label.set_color(color)
            except Exception:
                pass

        return colorbar_axis

    def get_current_levels(self, index=0):
        """Get the current contour levels of the contour set."""
        if index < len(self._lines):
            line = self._lines[index]
            if hasattr(line, "levels"):
                levels = line.levels

        if levels is not None:
            if self.plot_3D_classe == "Auto":
                return {"Auto": len(levels)}
            else:
                return {"Manuel": levels.tolist()}
        else:
            return None

    def _replace_contour_levels(self, classes, index=0):
        """Recreate the contour set because Matplotlib levels are not mutable."""
        classes.sort()
        dataset = self.list_data_xarray[index]
        line = self._lines[index]

        x_name = self.xarray_data["x"]
        y_name = self.xarray_data["y"]
        z_name = self.xarray_data["z"]

        x = dataset[x_name].values
        y = dataset[y_name].values
        z = dataset[z_name].values
        if (len(x), len(y)) == z.shape:
            z = z.T

        old_colorbar = getattr(self, "_colorbar", None)
        colorbar_label = ""
        colorbar_orientation = "vertical"
        if old_colorbar is not None:
            colorbar_orientation = old_colorbar.orientation
            colorbar_label = (
                old_colorbar.ax.get_ylabel()
                if colorbar_orientation == "vertical"
                else old_colorbar.ax.get_xlabel()
            )

        new_line = self.axes.contourf(
            x,
            y,
            z,
            levels=classes,
            cmap=line.get_cmap(),
            alpha=line.get_alpha(),
            antialiased=False,
        )
        new_line.set_label(line.get_label())
        is_colorbar_shown = False
        if old_colorbar is not None:
            try:
                old_colorbar.remove()
                is_colorbar_shown = True
            except Exception:
                pass
        line.remove()
        self._lines[index] = new_line

        if is_colorbar_shown:
            self._colorbar = self.figure.colorbar(
                new_line,
                ax=self.axes,
                orientation=colorbar_orientation,
            )
            self._colorbar.set_label(colorbar_label)

    def apply_3d_parameters(self, parameters):
        """Apply persisted colorbar and contour settings to a 3D plot."""
        if len(self._lines) == 0:
            return

        if parameters.get("has_colorbar", False):
            if self._colorbar is None:
                try:
                    self._colorbar = self.figure.colorbar(self._lines[0], ax=self.axes)
                except Exception:
                    self._colorbar = None

            if self._colorbar is not None:
                orientation = parameters.get("colorbar_orientation")
                if self._colorbar.orientation == "vertical":
                    colorbar_label = self._colorbar.ax.get_ylabel() if self._colorbar.ax.get_ylabel() is not None else ""
                    colorbar_axis = self._colorbar.ax.yaxis
                    if orientation == "horizontal":
                        self._colorbar = self.change_orientation_colorbar(colorbar_axis, orientation)
                else:
                    colorbar_label = self._colorbar.ax.get_xlabel() if self._colorbar.ax.get_xlabel() is not None else ""
                    colorbar_axis = self._colorbar.ax.xaxis
                    if orientation == "horizontal":
                        self._colorbar = self.change_orientation_colorbar(colorbar_axis, orientation)

                if colorbar_label:
                    self._colorbar.set_label(colorbar_label)

                font_colorbar = parameters.get("colorbar_font", False)
                if colorbar_label and font_colorbar:
                    colorlabel_colorbar = parameters.get("colorlabel_colorbar", False)
                    self.apply_font_to_the_colorbar(colorbar_axis, font_colorbar, colorlabel_colorbar)

        else:
            if self._colorbar is not None:
                try:
                    self._colorbar.remove()
                except Exception:
                    pass
                self._colorbar = None

        cmap_name = parameters.get("cmap")
        if cmap_name and hasattr(self._lines[0], "set_cmap"):
            try:
                self._lines[0].set_cmap(matplotlib.cm.get_cmap(cmap_name))
            except Exception:
                pass

        clim = parameters.get("clim")
        if clim and hasattr(self._lines[0], "set_clim"):
            self._lines[0].set_clim(clim)

        alpha = parameters.get("alpha")
        if alpha and hasattr(self._lines[0], "set_alpha"):
            self._lines[0].set_alpha(alpha)

        levels = parameters.get("levels")
        if levels is not None:
            if levels.keys() == {"Auto"}:
                self.plot_3D_classe = list(levels.keys())[0]
                vmax = self._lines[0].get_array().max() if hasattr(self._lines[0], "get_array") else None
                vmin = self._lines[0].get_array().min() if hasattr(self._lines[0], "get_array") else None
                if vmax is not None and vmin is not None:
                    num_levels = levels["Auto"]
                    auto_levels = linspace(vmin, vmax, num_levels)
                    self._replace_contour_levels(auto_levels, index=0)
            elif levels.keys() == {"Manuel"}:
                self.plot_3D_classe = list(levels.keys())[0]
                self._replace_contour_levels(levels["Manuel"], index=0)
            else:
                print("Warning: Unexpected levels format in loaded parameters. Levels not updated.")

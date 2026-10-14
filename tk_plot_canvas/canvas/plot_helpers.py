"""Helpers shared by the standard and xarray plotting mixins."""

import copy
from typing import Any, Optional, Sequence

from numpy import datetime64

from ..config import CURVE_TYPE_LINE, KEY_CURVE_TYPE, KEY_CURVES


class PlotHelpersMixin:
    """Common steps of every plotting method.

    Requires the host canvas attributes ``axes``, ``lines``, ``line_labels``,
    ``view_parameters``, ``cartouche_keys`` and ``show_legend``.
    """

    def _reset_plot_data(self) -> None:
        """Clear the axes and forget the plotted artists and their labels."""
        self.axes.cla()
        self.lines.clear()
        self.line_labels.clear()

    def _legend_label_for(self, label: Optional[dict]) -> Optional[str]:
        """Build the legend text of a new curve.

        Args:
            label: Curve metadata.

        Returns:
            The legend text, or None when no metadata is given.
        """
        if not label:
            return None
        return self.build_legend_label(label, show_keys=self.show_legend_key_names)

    def _curve_kwargs_from_view(self, plot_kwargs: dict[str, Any]) -> dict[str, Any]:
        """Complete plot keyword arguments with the loaded view's curve style.

        Arguments given explicitly by the caller always win. Saved styles that
        are not line styles (e.g. contours of a 3D view) are ignored.

        Args:
            plot_kwargs: Keyword arguments given by the caller.

        Returns:
            Keyword arguments for ``Axes.plot``.
        """
        merged_kwargs = copy.copy(plot_kwargs)
        if self.view_parameters:
            curves = self.view_parameters.get(KEY_CURVES, {})
            saved_curve = curves.get(str(len(self.lines)), {})
            if saved_curve.get(KEY_CURVE_TYPE, CURVE_TYPE_LINE) != CURVE_TYPE_LINE:
                saved_curve = {}
            for key, value in saved_curve.items():
                if key not in plot_kwargs:
                    merged_kwargs[key] = value
        merged_kwargs.pop(KEY_CURVE_TYPE, None)
        return merged_kwargs

    def _detect_date_axis(self, values: Sequence[Any], axis_name: str) -> None:
        """Switch an axis to date formatting when its values are dates.

        Args:
            values: Values plotted along the axis.
            axis_name: "x" or "y".
        """
        if type(values[0]) is not datetime64:
            return
        if axis_name == "x":
            self.is_date_on_x_axis = True
            self.axes.xaxis_date()
        else:
            self.is_date_on_y_axis = True
            self.axes.yaxis_date()

    def _register_plot(self, artist: Any, label: Optional[dict]) -> None:
        """Remember a plotted artist and its metadata.

        Args:
            artist: ``Line2D`` or contour set.
            label: Curve metadata.
        """
        self.lines.append(artist)
        self.line_labels.append(label)

    def _update_cartouche_for_new_plot(self, label: Optional[dict], replot: bool) -> None:
        """Show the metadata of the newest plot in the cartouche.

        Args:
            label: Metadata of the newest plot.
            replot: True when re-plotting existing data (all rows refreshed).
        """
        if replot:
            self.refresh_cartouche()
            return
        displayed = {
            key: label[key] for key in self.cartouche_keys if label is not None and key in label
        }
        self.fill_cartouche_row(displayed, line_index=len(self.lines) - 1, line_display=True)

    def _show_legend_if_requested(self, legend: bool, legend_label: Optional[str]) -> None:
        """Display a draggable legend when requested and enabled.

        Args:
            legend: Whether the caller asked for a legend.
            legend_label: Legend text of the new curve.
        """
        if legend and legend_label is not None and self.show_legend:
            self.show_draggable_legend()

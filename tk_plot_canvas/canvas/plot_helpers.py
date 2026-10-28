"""Helpers shared by the standard and xarray plotting mixins."""

import copy
from typing import Any, Optional, Sequence

from numpy import asarray, datetime64, issubdtype

from ..config import CURVE_TYPE_LINE, KEY_CURVE_TYPE, KEY_CURVES


class PlotHelpersMixin:
    """Common steps of every plotting method.

    Requires the host canvas attributes ``axes``, ``lines``, ``line_labels``,
    ``view_parameters``, ``cartouche_keys``, ``legend_keys``, ``show_legend``,
    ``title_var``, ``xlabel_var`` and ``ylabel_var``.
    """

    def _reset_plot_data(self) -> None:
        """Clear the axes and forget the plotted artists and their labels."""
        self.axes.cla()
        self.lines.clear()
        self.line_labels.clear()

    def _apply_default_metadata_keys(self, label: Optional[dict], legend: bool) -> None:
        """Choose the displayed metadata keys when no view defines them.

        The cartouche then shows every key of the metadata, and a requested
        legend is displayed with the first key.

        Args:
            label: Metadata of the new plot.
            legend: Whether the caller asked for a legend.
        """
        view = self.view_parameters or {}
        if not label:
            return
        if not self.cartouche_keys and "cartouche" not in view:
            self.cartouche_keys = list(label)
        if legend and not self.legend_keys and "legend" not in view:
            self.legend_keys = list(label)[:1]
            self.show_legend = True

    def _set_axes_text(self, key: str, text: str) -> None:
        """Set the title or an axis label, with the font of the loaded view if any.

        Args:
            key: "title", "xlabel" or "ylabel".
            text: Text to display.
        """
        targets = {
            "title": (self.axes.set_title, self.title_var),
            "xlabel": (self.axes.set_xlabel, self.xlabel_var),
            "ylabel": (self.axes.set_ylabel, self.ylabel_var),
        }
        setter, text_var = targets[key]
        setter(text, (self.view_parameters or {}).get(key))
        text_var.set(text)

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
        """Remember whether an axis shows dates, and format it as dates if so.

        The flag is reset for non-date values, so that the axis limits are
        edited as numbers once another (non-date) variable is plotted.

        Args:
            values: Values plotted along the axis.
            axis_name: "x" or "y".
        """
        is_date = issubdtype(asarray(values).dtype, datetime64)
        setattr(self, f"is_date_on_{axis_name}_axis", is_date)
        if is_date:
            getattr(self.axes, f"{axis_name}axis_date")()

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

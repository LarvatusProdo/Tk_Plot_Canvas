"""Plotting of ordinary x/y sequences."""

from typing import Any, Iterable, Optional

from ..config import PLOT_TYPE_2D
from ..view import apply_axis_parameters


class StandardPlotMixin:
    """Plot x/y sequences on the canvas (requires :class:`PlotHelpersMixin`)."""

    def plot(
        self,
        x: Iterable[float],
        y: Iterable[float],
        *,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        grid: bool = True,
        clear: bool = True,
        legend: bool = False,
        label: Optional[dict] = None,
        **plot_kwargs: Any,
    ) -> None:
        """Plot a curve in the embedded canvas.

        Args:
            x: X data values.
            y: Y data values.
            title: Plot title (with the font of the loaded view, if any).
            xlabel: X-axis label (with the font of the loaded view, if any).
            ylabel: Y-axis label (with the font of the loaded view, if any).
            grid: Whether to show a grid.
            clear: Whether to clear the previous plot first.
            legend: Whether to show a legend (when labels are provided). Without
                a view defining it, the legend shows the first metadata key.
            label: Curve metadata shown in the legend and the cartouche,
                e.g. ``{"name": "curve", "value": 42}``. Without a view defining
                them, the cartouche shows every key.
            **plot_kwargs: Passed to ``Axes.plot``.
        """
        if clear:
            self._reset_plot_data()
        self.plot_type = PLOT_TYPE_2D
        self._apply_default_metadata_keys(label, legend)
        legend_label = self._legend_label_for(label)
        line_kwargs = self._curve_kwargs_from_view(plot_kwargs)
        self._detect_date_axis(x, "x")
        (line,) = self.axes.plot(x, y, label=legend_label, **line_kwargs)
        self._register_plot(line, label)
        self._update_cartouche_for_new_plot(label, replot=False)
        self._apply_texts(title, xlabel, ylabel)
        self.axes.grid(grid)
        if self.view_parameters != {}:
            apply_axis_parameters(self, "x", self.view_parameters.get("X_axis"))
            apply_axis_parameters(self, "y", self.view_parameters.get("Y_axis"))
        self._show_legend_if_requested(legend, legend_label)
        self.figure_canvas.draw()

    def _apply_texts(
        self, title: Optional[str], xlabel: Optional[str], ylabel: Optional[str]
    ) -> None:
        """Set the given title and axis labels (None leaves a text unchanged).

        Args:
            title: Plot title.
            xlabel: X-axis label.
            ylabel: Y-axis label.
        """
        for key, text in (("title", title), ("xlabel", xlabel), ("ylabel", ylabel)):
            if text is not None:
                self._set_axes_text(key, text)

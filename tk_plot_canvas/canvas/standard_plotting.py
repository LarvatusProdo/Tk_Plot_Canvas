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
            title: Plot title (applied only when a view has been loaded).
            xlabel: X-axis label (applied only when a view has been loaded).
            ylabel: Y-axis label (applied only when a view has been loaded).
            grid: Whether to show a grid.
            clear: Whether to clear the previous plot first.
            legend: Whether to show a legend (when labels are provided).
            label: Curve metadata shown in the legend and the cartouche,
                e.g. ``{"name": "curve", "value": 42}``.
            **plot_kwargs: Passed to ``Axes.plot``.
        """
        if clear:
            self._reset_plot_data()
        self.plot_type = PLOT_TYPE_2D
        legend_label = self._legend_label_for(label)
        line_kwargs = self._curve_kwargs_from_view(plot_kwargs)
        self._detect_date_axis(x, "x")
        (line,) = self.axes.plot(x, y, label=legend_label, **line_kwargs)
        self._register_plot(line, label)
        self._update_cartouche_for_new_plot(label, replot=False)
        self._apply_view_texts(title, xlabel, ylabel)
        self.axes.grid(grid)
        if self.view_parameters != {}:
            apply_axis_parameters(self, "x", self.view_parameters.get("X_axis"))
            apply_axis_parameters(self, "y", self.view_parameters.get("Y_axis"))
        self._show_legend_if_requested(legend, legend_label)
        self.figure_canvas.draw()

    def _apply_view_texts(
        self, title: Optional[str], xlabel: Optional[str], ylabel: Optional[str]
    ) -> None:
        """Set title and axis labels using the fonts of the loaded view.

        A text is only applied when it is given and the loaded view defines
        its font.

        Args:
            title: Plot title.
            xlabel: X-axis label.
            ylabel: Y-axis label.
        """
        targets = (
            ("title", title, self.axes.set_title, self.title_var),
            ("xlabel", xlabel, self.axes.set_xlabel, self.xlabel_var),
            ("ylabel", ylabel, self.axes.set_ylabel, self.ylabel_var),
        )
        for key, text, setter, text_var in targets:
            if text is not None and key in self.view_parameters:
                setter(text, self.view_parameters[key])
                text_var.set(text)

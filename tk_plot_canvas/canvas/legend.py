"""Legend management: legend texts are built from curve metadata."""

from typing import Optional


class LegendMixin:
    """Build legend texts and keep the Matplotlib legend in sync.

    Requires the host canvas attributes ``legend_keys``, ``lines``,
    ``line_labels``, ``show_legend``, ``show_legend_key_names``, ``axes`` and
    ``figure_canvas``.
    """

    def build_legend_label(self, label: Optional[dict], show_keys: bool = False) -> str:
        """Build the legend text of a curve from its metadata.

        Args:
            label: Curve metadata.
            show_keys: Whether to prefix each value with its key ("key: value").

        Returns:
            The selected values (``legend_keys``) joined by ", ".
        """
        if label is None:
            return ""
        parts = []
        for key in self.legend_keys:
            if key in label:
                parts.append(f"{key}: {label[key]}" if show_keys else f"{label[key]}")
        return ", ".join(parts)

    def set_legend_visible(self, visible: bool) -> None:
        """Show or hide the legend (showing the first metadata key when none is chosen).

        Args:
            visible: Whether the legend is displayed.
        """
        labels = [label for label in self.line_labels if label]
        if visible and not self.legend_keys and labels:
            self.legend_keys = list(labels[0])[:1]
        self.show_legend = visible
        self.refresh_legend()

    def refresh_legend(self) -> None:
        """Rebuild every legend text, then show or hide the legend."""
        for index, line in enumerate(self.lines):
            label = self.line_labels[index]
            line.set_label(self.build_legend_label(label, show_keys=self.show_legend_key_names))
        if len(self.lines) > 0:
            if self.show_legend and len(self.legend_keys) > 0:
                self.show_draggable_legend()
            else:
                self._remove_legend()
        self.figure_canvas.draw()

    def show_draggable_legend(self, location: Optional[str] = None) -> None:
        """Display a draggable legend, or remove it when no curve has a label.

        Curves whose label is empty or starts with an underscore are ignored by
        Matplotlib; calling ``legend()`` without any labeled curve would emit a
        ``UserWarning``.

        Args:
            location: Matplotlib legend location (``None`` keeps the default).
        """
        _, labels = self.axes.get_legend_handles_labels()
        if labels:
            self.axes.legend(loc=location, draggable=True)
        else:
            self._remove_legend()

    def _remove_legend(self) -> None:
        """Remove the Matplotlib legend if one is displayed."""
        legend = self.axes.get_legend()
        if legend:
            legend.remove()

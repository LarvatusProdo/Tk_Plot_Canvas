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

    def refresh_legend(self) -> None:
        """Rebuild every legend text, then show or hide the legend."""
        for index, line in enumerate(self.lines):
            label = self.line_labels[index]
            line.set_label(self.build_legend_label(label, show_keys=self.show_legend_key_names))
        if len(self.lines) > 0:
            if self.show_legend and len(self.legend_keys) > 0:
                self.axes.legend(draggable=True)
            else:
                self._remove_legend()
        self.figure_canvas.draw()

    def _remove_legend(self) -> None:
        """Remove the Matplotlib legend if one is displayed."""
        legend = self.axes.get_legend()
        if legend:
            legend.remove()

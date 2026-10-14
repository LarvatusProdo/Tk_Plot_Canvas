"""Double-click shortcuts on the figure.

A double click on the title, an axis label or the colorbar label edits it in
place; on the legend, a curve, the axes ticks or the colorbar, it opens the
matching tab of the settings window.
"""

from functools import partial
from typing import Any, Optional

from matplotlib.backend_bases import MouseEvent
from matplotlib.text import Text

from ..config import PLOT_TYPE_2D, TAB_3D, TAB_AXES, TAB_CURVES, TAB_LEGEND
from ..widgets.inline_text_editor import InlineTextEditor
from .colorbar import colorbar_label_axis

LEFT_BUTTON = 1


class DoubleClickMixin:
    """React to double clicks on the figure.

    Requires the host canvas attributes ``figure_canvas``, ``axes``,
    ``colorbar``, ``lines``, ``plot_type``, ``title_var``, ``xlabel_var``,
    ``ylabel_var`` and the methods ``open_settings_window``,
    ``_reopen_settings_window`` and ``_selected_settings_tab``.
    """

    def _connect_double_click(self) -> None:
        """Listen to the mouse clicks of the figure."""
        self.figure_canvas.mpl_connect("button_press_event", self._on_figure_click)

    def _on_figure_click(self, event: MouseEvent) -> None:
        """Edit the double-clicked text, or open the matching settings tab.

        Args:
            event: Matplotlib mouse event.
        """
        if not event.dblclick or event.button != LEFT_BUTTON:
            return
        for text, variable in self._editable_texts():
            if text.get_text() and text.contains(event)[0]:
                InlineTextEditor(
                    self.figure_canvas.get_tk_widget(),
                    text,
                    partial(self._commit_text, text, variable),
                )
                return
        tab_name = self._tab_under(event)
        if tab_name is not None:
            self.open_settings_window(tab_name)

    def _editable_texts(self) -> list[tuple[Text, Optional[Any]]]:
        """List the texts editable in place, with the Tk variable mirroring each one.

        Returns:
            ``(text, variable)`` pairs; the colorbar label has no variable.
        """
        texts = [
            (self.axes.title, self.title_var),
            (self.axes.xaxis.label, self.xlabel_var),
            (self.axes.yaxis.label, self.ylabel_var),
        ]
        if self.colorbar is not None:
            texts.append((colorbar_label_axis(self.colorbar).label, None))
        return texts

    def _commit_text(self, text: Text, variable: Optional[Any], new_text: str) -> None:
        """Display an edited text (its font is kept) and refresh the settings window.

        Args:
            text: Edited Matplotlib text.
            variable: Tk variable mirroring the text, if any.
            new_text: Typed text.
        """
        text.set_text(new_text)
        if variable is not None:
            variable.set(new_text)
        self.figure_canvas.draw_idle()
        self._reopen_settings_window(self._selected_settings_tab())

    def _tab_under(self, event: MouseEvent) -> Optional[str]:
        """Return the settings tab matching the double-clicked element.

        Args:
            event: Matplotlib mouse event.

        Returns:
            A tab name, or None when nothing relevant was clicked.
        """
        if self.colorbar is not None and event.inaxes is self.colorbar.ax:
            return TAB_3D
        legend = self.axes.get_legend()
        if self.plot_type == PLOT_TYPE_2D:
            if legend is not None and legend.contains(event)[0]:
                return TAB_LEGEND
            if any(line.contains(event)[0] for line in self.lines):
                return TAB_CURVES
        if self.axes.xaxis.contains(event)[0] or self.axes.yaxis.contains(event)[0]:
            return TAB_AXES
        return None

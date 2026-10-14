"""Dialog editing the contour classes (and their value range) of a surface plot.

Unlike the other dialogs, the classes are only applied on request, because
they form a whole list validated at once: "Appliquer" applies and keeps the
dialog open, "OK" applies and closes it, "Annuler" (or Escape) restores the
classes shown when the dialog opened.
"""

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any

from ..config import CLASS_MODE_AUTO, STYLE_BUTTON, STYLE_LABELFRAME, VALUE_RANGE_DIALOG_SIZE
from ..widgets import ClassSelectionFrame
from .window_placement import setup_dialog

if TYPE_CHECKING:
    from ..canvas.plot_canvas import TkPlotCanvas

FRAME_PADDING = (10, 10)
BUTTON_SPACING = 10


class ValueRangeDialog(tk.Toplevel):
    """Edit the contour classes of a filled-contour plot."""

    def __init__(self, parent: tk.Misc, canvas: "TkPlotCanvas", surface: Any, index: int) -> None:
        """Create the dialog.

        Args:
            parent: Window the dialog is positioned against.
            canvas: The plot canvas being edited.
            surface: Filled-contour set to edit.
            index: Index of the plot.
        """
        super().__init__(parent)
        self.title("Classes de valeurs")
        setup_dialog(self, parent, VALUE_RANGE_DIALOG_SIZE, on_escape=self.cancel)
        self.canvas = canvas
        self.surface = surface
        self.index = index
        self._initial_state = (
            canvas.contour_class_mode,
            canvas.contour_value_range,
            [float(level) for level in surface.levels],
        )
        self._is_applied = False
        self._build_buttons()
        self._build_class_selection()

    def _build_buttons(self) -> None:
        """Create the "Annuler", "Appliquer" and "OK" buttons."""
        frame = ttk.Frame(self)
        frame.pack(fill=tk.X, padx=10, pady=10, side=tk.BOTTOM)
        for text, command in (
            ("OK", self.confirm),
            ("Appliquer", self.apply_changes),
            ("Annuler", self.cancel),
        ):
            ttk.Button(frame, text=text, style=STYLE_BUTTON, command=command).pack(
                side="right", padx=(BUTTON_SPACING, 0)
            )

    def _build_class_selection(self) -> None:
        """Create the contour class selector initialized from the plot."""
        frame = ttk.LabelFrame(
            self, text="Classes", padding=FRAME_PADDING, style=STYLE_LABELFRAME
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10, side=tk.TOP)
        levels = [float(level) for level in self.surface.levels]
        default_range = self.canvas.get_data_range(self.index)
        saved_range = self.canvas.contour_value_range
        v_min, v_max = saved_range or (min(levels), max(levels))
        self.class_selection = ClassSelectionFrame(
            frame,
            v_max=v_max,
            v_min=v_min,
            nb_classes=len(levels) - 1,
            classes=levels,
            default_range=default_range,
            use_default_range=saved_range is None,
            type_class=self.canvas.contour_class_mode,
        )
        self.class_selection.pack(fill=tk.BOTH)

    def apply_changes(self) -> bool:
        """Apply the contour classes (the min/max of the "Auto" mode set the value range).

        Returns:
            False when the typed classes are invalid (nothing is applied).
        """
        selection = self.class_selection.get_classes()
        if selection is None:
            return False
        self.canvas.contour_class_mode, classes = selection
        if self.canvas.contour_class_mode == CLASS_MODE_AUTO:
            self.canvas.contour_value_range = self.class_selection.get_value_range()
        if classes != []:
            self.canvas.replace_contour_levels(classes, index=self.index)
            self.canvas.figure_canvas.draw()
        self._is_applied = True
        return True

    def confirm(self) -> None:
        """Apply the classes and close the dialog (it stays open when they are invalid)."""
        if self.apply_changes():
            self.destroy()

    def cancel(self) -> None:
        """Restore the classes shown when the dialog opened, then close the dialog."""
        if self._is_applied:
            mode, value_range, levels = self._initial_state
            self.canvas.contour_class_mode = mode
            self.canvas.contour_value_range = value_range
            self.canvas.replace_contour_levels(list(levels), index=self.index)
            self.canvas.figure_canvas.draw()
        self.destroy()

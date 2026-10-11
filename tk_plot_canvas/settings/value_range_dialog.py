"""Dialog editing the contour classes (and their value range) of a 3D plot."""

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any

from ..config import CLASS_MODE_AUTO, STYLE_LABELFRAME, VALUE_RANGE_DIALOG_SIZE
from ..widgets import ClassSelectionFrame
from .window_placement import place_window

if TYPE_CHECKING:
    from ..canvas.plot_canvas import TkPlotCanvas

FRAME_PADDING = (10, 10)


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
        self.title("Paramètres de la plage de valeurs")
        place_window(self, parent, VALUE_RANGE_DIALOG_SIZE)
        self.canvas = canvas
        self.surface = surface
        self.index = index
        apply_frame = ttk.Frame(self)
        apply_frame.pack(fill=tk.BOTH, padx=10, pady=10, side=tk.BOTTOM)
        ttk.Button(apply_frame, text="Appliquer", command=self.apply_changes).pack(
            expand=True, fill=tk.X
        )
        self._build_class_selection()

    def _build_class_selection(self) -> None:
        """Create the contour class selector initialized from the plot."""
        frame = ttk.LabelFrame(
            self, text="Choix des classes :", padding=FRAME_PADDING, style=STYLE_LABELFRAME
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

    def apply_changes(self) -> None:
        """Apply the contour classes (the min/max of the "Auto" mode set the value range)."""
        selection = self.class_selection.get_classes()
        if selection is None:
            return
        self.canvas.contour_class_mode, classes = selection
        if self.canvas.contour_class_mode == CLASS_MODE_AUTO:
            self.canvas.contour_value_range = self.class_selection.get_value_range()
        if classes != []:
            self.canvas.replace_contour_levels(classes, index=self.index)
            self.canvas.figure_canvas.draw()
        self.destroy()

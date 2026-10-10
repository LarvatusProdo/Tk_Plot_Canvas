"""Dialog editing the value limits and contour classes of a 3D plot."""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, Any

from ..config import (
    STYLE_ENTRY,
    STYLE_LABEL,
    STYLE_LABELFRAME,
    VALUE_RANGE_DIALOG_SIZE,
)
from ..widgets import ClassSelectionFrame
from .window_placement import place_window

if TYPE_CHECKING:
    from ..canvas.plot_canvas import TkPlotCanvas

PADDING = 5
FRAME_PADDING = (10, 10)


class ValueRangeDialog(tk.Toplevel):
    """Edit the color limits or the contour classes of a filled-contour plot."""

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
        self._build_limits()
        apply_frame = ttk.Frame(self)
        apply_frame.pack(fill=tk.BOTH, padx=10, pady=10, side=tk.BOTTOM)
        ttk.Button(apply_frame, text="Appliquer", command=self.apply_changes).pack(
            expand=True, fill=tk.X
        )
        self._build_class_selection()

    def _build_limits(self) -> None:
        """Create the minimum and maximum value entries."""
        frame = ttk.LabelFrame(
            self, text="Plage de valeurs", padding=FRAME_PADDING, style=STYLE_LABELFRAME
        )
        frame.pack(fill=tk.BOTH, padx=10, pady=10, side=tk.TOP)
        minimum, maximum = self.surface.get_clim()
        self.vmin_var = self._add_limit_entry(frame, "Valeur min:", 0, minimum)
        self.vmax_var = self._add_limit_entry(frame, "Valeur max:", 1, maximum)

    @staticmethod
    def _add_limit_entry(frame: ttk.LabelFrame, text: str, row: int, value: float) -> tk.StringVar:
        """Add a labelled limit entry.

        Args:
            frame: Parent frame.
            text: Label text.
            row: Grid row.
            value: Initial value.

        Returns:
            The variable bound to the entry.
        """
        ttk.Label(frame, text=text, style=STYLE_LABEL).grid(
            row=row, column=0, sticky="e", padx=PADDING, pady=PADDING
        )
        variable = tk.StringVar(value=str(value))
        ttk.Entry(frame, textvariable=variable, width=15, style=STYLE_ENTRY).grid(
            row=row, column=1, sticky="w", padx=PADDING, pady=PADDING
        )
        return variable

    def _build_class_selection(self) -> None:
        """Create the contour class selector initialized from the plot."""
        frame = ttk.LabelFrame(
            self, text="Choix des classes :", padding=FRAME_PADDING, style=STYLE_LABELFRAME
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10, side=tk.TOP)
        levels = [float(level) for level in self.surface.levels]
        self.class_selection = ClassSelectionFrame(
            frame,
            v_max=self.vmax_var.get(),
            v_min=self.vmin_var.get(),
            nb_classes=len(levels) - 1,
            classes=levels,
            type_class=self.canvas.contour_class_mode,
        )
        self.class_selection.pack(fill=tk.BOTH)

    def apply_changes(self) -> None:
        """Apply the contour classes, or the color limits in "Aucune" mode."""
        selection = self.class_selection.get_classes()
        if selection is None:
            return
        self.canvas.contour_class_mode, classes = selection
        if classes != []:
            self.canvas.replace_contour_levels(classes, index=self.index)
            self.canvas.figure_canvas.draw()
            self.destroy()
            return
        try:
            vmin = float(self.vmin_var.get())
            vmax = float(self.vmax_var.get())
        except ValueError:
            messagebox.showerror(
                "Invalid input", "Please enter valid numeric values for vmin and vmax."
            )
            return
        self.surface.set_clim(vmin=vmin, vmax=vmax)
        self.canvas.figure_canvas.draw()
        self.destroy()

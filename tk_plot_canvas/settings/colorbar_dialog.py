"""Dialog editing the colorbar label, its font and its orientation."""

import tkinter as tk
from functools import partial
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, Any

from ..config import (
    COLORBAR_LOCATIONS,
    COLORBAR_VERTICAL,
    STYLE_BUTTON,
    STYLE_ENTRY,
    STYLE_LABEL,
    STYLE_LABELFRAME,
)
from .font_dialogs import ColorbarFontDialog
from .window_placement import setup_dialog

if TYPE_CHECKING:
    from ..canvas.plot_canvas import TkPlotCanvas

PADDING = 5
SEPARATOR_PADY = (10, 10)
DIALOG_SIZE_COLORBAR = "420x640"
# (style key, label, minimum, maximum, step)
SPIN_FIELDS = [
    ("shrink", "Longueur (fraction):", 0.1, 1.0, 0.05),
    ("aspect", "Finesse (longueur/épaisseur):", 1, 100, 1),
    ("pad", "Distance au graphique:", 0.0, 0.5, 0.01),
    ("fraction", "Espace occupé:", 0.02, 0.5, 0.01),
    ("tick_labelsize", "Taille des graduations:", 4, 40, 1),
    ("outline_width", "Épaisseur du contour:", 0.1, 5, 0.1),
]


class ColorbarDialog(tk.Toplevel):
    """Edit the label (live), font and orientation of the colorbar."""

    def __init__(
        self, parent: tk.Misc, canvas: "TkPlotCanvas", colorbar: Any, index: int = 0
    ) -> None:
        """Create the dialog.

        Args:
            parent: Window the dialog is positioned against.
            canvas: The plot canvas being edited.
            colorbar: Colorbar to edit.
            index: Index of the plot described by the colorbar.
        """
        super().__init__(parent)
        self.title("Paramètres de la colorbar")
        setup_dialog(self, parent, DIALOG_SIZE_COLORBAR)
        self.canvas = canvas
        self.colorbar = colorbar
        self.index = index
        frame = ttk.LabelFrame(
            self, text="Paramètres de la colorbar", padding=(10, 10), style=STYLE_LABELFRAME
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._build_label_controls(frame, parent)
        self._build_orientation_controls(frame)

    def _current_label(self) -> str:
        """Return the label of the edited colorbar.

        Returns:
            The y label of a vertical colorbar, the x label otherwise.
        """
        if self.colorbar.orientation == COLORBAR_VERTICAL:
            return self.colorbar.ax.get_ylabel()
        return self.colorbar.ax.get_xlabel()

    def _add_label(self, frame: ttk.LabelFrame, text: str, row: int) -> None:
        """Add a right-aligned field label in column 0.

        Args:
            frame: Parent frame.
            text: Label text.
            row: Grid row.
        """
        ttk.Label(frame, text=text, style=STYLE_LABEL).grid(
            row=row, column=0, sticky="e", padx=PADDING, pady=PADDING
        )

    def _build_label_controls(self, frame: ttk.LabelFrame, parent: tk.Misc) -> None:
        """Create the label entry (updated live) and the font button.

        Args:
            frame: Parent frame.
            parent: Window owning the font dialog.
        """
        self._add_label(frame, "Label:", 0)
        self.label_var = tk.StringVar(value=self._current_label())
        ttk.Entry(frame, textvariable=self.label_var, width=30, style=STYLE_ENTRY).grid(
            row=0, column=1, sticky="w", padx=PADDING, pady=PADDING
        )
        self.label_var.trace_add("write", self._on_label_changed)
        ttk.Button(
            frame,
            text="Modifier la police",
            style=STYLE_BUTTON,
            command=partial(
                self.canvas.dialogs.show,
                "font:colorbar",
                partial(ColorbarFontDialog, parent, self.canvas),
            ),
        ).grid(row=10, column=0, columnspan=3, sticky="we", padx=PADDING, pady=PADDING)

    def _build_orientation_controls(self, frame: ttk.LabelFrame) -> None:
        """Create the orientation combobox and the apply button.

        Args:
            frame: Parent frame.
        """
        ttk.Separator(frame, orient="horizontal").grid(
            row=20, column=0, columnspan=3, sticky="we", pady=SEPARATOR_PADY
        )
        style = self.canvas.colorbar_style
        self._add_label(frame, "Position:", 30)
        self.location_var = tk.StringVar(value=style["location"])
        ttk.Combobox(
            frame,
            values=COLORBAR_LOCATIONS,
            textvariable=self.location_var,
            state="readonly",
            width=15,
        ).grid(row=30, column=1, sticky="w", padx=PADDING, pady=PADDING)
        self.style_vars: dict[str, tk.StringVar] = {}
        for row, (key, text, low, high, step) in enumerate(SPIN_FIELDS, start=31):
            self._add_label(frame, text, row)
            self.style_vars[key] = tk.StringVar(value=str(style[key]))
            ttk.Spinbox(
                frame,
                textvariable=self.style_vars[key],
                from_=low,
                to=high,
                increment=step,
                width=8,
            ).grid(row=row, column=1, sticky="w", padx=PADDING, pady=PADDING)
        ttk.Separator(frame, orient="horizontal").grid(
            row=99, column=0, columnspan=3, sticky="we", pady=SEPARATOR_PADY
        )
        ttk.Button(frame, text="Appliquer", command=self.apply_changes).grid(
            row=100, column=0, columnspan=2, sticky="we", pady=SEPARATOR_PADY
        )

    def apply_changes(self) -> None:
        """Apply the label and the geometry (position, size, thickness...)."""
        new_label = self.label_var.get()
        new_style: dict[str, Any] = {"location": self.location_var.get()}
        for key, var in self.style_vars.items():
            try:
                value = float(var.get().replace(",", "."))
            except ValueError:
                messagebox.showerror("Erreur", f"Valeur invalide pour « {key} ».", parent=self)
                return
            if value <= 0:
                messagebox.showerror("Erreur", f"« {key} » doit être positif.", parent=self)
                return
            new_style[key] = value
        self.canvas.set_colorbar_style(new_style, self.index)
        if self.canvas.colorbar is None:
            return
        self.canvas.colorbar.set_label(new_label)
        self.canvas.figure_canvas.draw()
        self.destroy()

    def _on_label_changed(self, *_trace_args: Any) -> None:
        """Update the colorbar label while the user types.

        Args:
            *_trace_args: Tk variable trace arguments (unused).
        """
        self.colorbar.ax.set_ylabel(self.label_var.get())
        self.canvas.figure_canvas.draw()

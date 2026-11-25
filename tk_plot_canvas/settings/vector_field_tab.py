"""Settings tab "Vecteurs" and the checkbutton of the "Surface" tab enabling it.

The arrows (e.g. wind direction) are drawn over the surface while the
checkbutton is checked; the "Vecteurs" tab is shown at the same time.
"""

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from ..widgets import ToolTip
from .base_tab import SettingsTab
from .vector_field_frame import VectorFieldFrame

if TYPE_CHECKING:
    from .surface_tab import SurfaceTab

VECTOR_HELP = (
    "Dessiner un champ de vecteurs (ex. direction du vent) par-dessus la surface.\n"
    "Ses réglages sont dans l'onglet « Vecteurs »."
)


class VectorFieldTab(SettingsTab):
    """Edit the components and the style of the arrows."""

    def build(self) -> None:
        """Create the frame of the arrow settings."""
        VectorFieldFrame(self.canvas, self.frame, row=0)


class VectorToggle:
    """Checkbutton of the "Surface" tab showing the arrows and the "Vecteurs" tab."""

    def __init__(self, tab: "SurfaceTab", row: int, column: int) -> None:
        """Create the checkbutton.

        Args:
            tab: The "Surface" tab.
            row: Grid row in the tab.
            column: Grid column in the tab.
        """
        self._tab = tab
        self.variable = tk.BooleanVar(value=tab.canvas.vector_field["enabled"])
        checkbutton = ttk.Checkbutton(
            tab.frame,
            text="Champ de vecteurs (flèches)",
            variable=self.variable,
            command=self._toggle,
        )
        checkbutton.grid(row=row, column=column, columnspan=40, sticky="w", padx=5, pady=10)
        ToolTip(checkbutton, VECTOR_HELP)

    def _toggle(self) -> None:
        """Show or hide the arrows, add or remove the "Vecteurs" tab."""
        self._tab.canvas.set_vector_field({"enabled": self.variable.get()})
        self._tab.window.update_optional_tabs()

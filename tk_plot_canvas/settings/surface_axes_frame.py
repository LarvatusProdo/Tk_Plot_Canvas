"""Label frame of the "Axes et titre" tab editing the axes settings of 3D plots."""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, Any

from ..canvas.surface_axes import Aspect, parse_aspect
from ..config import (
    ASPECT_CHOICES,
    STYLE_CHECKBUTTON,
    STYLE_COMBOBOX,
    STYLE_LABEL,
    STYLE_LABELFRAME,
)
from .axis_frame import FRAME_PADDING, PADDING

if TYPE_CHECKING:
    from .axes_tab import AxesTab

ASPECT_EVENTS = ("<<ComboboxSelected>>", "<Return>", "<FocusOut>")


def choice_text(choices: dict[str, Any], value: Any) -> str:
    """Return the displayed name of a value.

    Args:
        choices: Displayed names mapped to values.
        value: Value to look up.

    Returns:
        The first matching name ("" when none matches).
    """
    return next((text for text, choice in choices.items() if choice == value), "")


def aspect_text(aspect: Aspect) -> str:
    """Return the combobox text of an aspect value.

    Args:
        aspect: None, "equal", "auto" or a number.

    Returns:
        The French choice name, or the number as text.
    """
    return choice_text(ASPECT_CHOICES, aspect) or str(aspect)


class SurfaceAxesFrame:
    """Edit the aspect ratio and grid of a 3D plot (applied live)."""

    def __init__(self, tab: "AxesTab", row: int, column: int) -> None:
        """Create the label frame in the tab.

        Args:
            tab: The "Axes et titre" tab.
            row: Grid row of the label frame.
            column: First grid column of the label frame.
        """
        self._canvas = tab.canvas
        self._frame = ttk.LabelFrame(
            tab.frame,
            text="Paramètres du graphique 3D",
            padding=FRAME_PADDING,
            style=STYLE_LABELFRAME,
        )
        self._frame.grid(
            row=row, column=column, columnspan=2, sticky="nwe", padx=PADDING, pady=PADDING
        )
        style = self._canvas.surface_axes_style
        self.aspect_var = tk.StringVar(value=aspect_text(style["aspect"]))
        self.grid_var = tk.BooleanVar(value=style["grid"])
        self._build()

    def _build(self) -> None:
        """Create the aspect combobox and the grid checkbutton."""
        ttk.Label(self._frame, text="Aspect (y/x) :", style=STYLE_LABEL).grid(
            row=0, column=0, sticky="e", padx=PADDING, pady=PADDING
        )
        aspect_combobox = ttk.Combobox(
            self._frame,
            textvariable=self.aspect_var,
            values=list(ASPECT_CHOICES),
            width=15,
            style=STYLE_COMBOBOX,
        )
        aspect_combobox.grid(row=0, column=1, sticky="w", padx=PADDING, pady=PADDING)
        for sequence in ASPECT_EVENTS:
            aspect_combobox.bind(sequence, lambda _event: self._apply_aspect())
        ttk.Checkbutton(
            self._frame,
            text="Afficher la grille",
            variable=self.grid_var,
            style=STYLE_CHECKBUTTON,
            command=self._apply_grid,
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=PADDING, pady=PADDING)

    def _apply_aspect(self) -> None:
        """Apply the selected aspect, or the typed y/x ratio."""
        text = self.aspect_var.get().strip()
        try:
            aspect = ASPECT_CHOICES[text] if text in ASPECT_CHOICES else parse_aspect(text)
        except ValueError:
            messagebox.showerror(
                "Invalid input",
                "Choisissez un aspect dans la liste ou saisissez un nombre positif (rapport y/x).",
                parent=self._frame,
            )
            self.aspect_var.set(aspect_text(self._canvas.surface_axes_style["aspect"]))
            return
        if aspect != self._canvas.surface_axes_style["aspect"]:
            self._canvas.set_surface_axes_style({"aspect": aspect})

    def _apply_grid(self) -> None:
        """Show or hide the grid."""
        self._canvas.set_surface_axes_style({"grid": self.grid_var.get()})

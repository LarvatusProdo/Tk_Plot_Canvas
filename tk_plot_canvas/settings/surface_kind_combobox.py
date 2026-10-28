"""Combobox choosing the kind of a surface plot (filled contours, lines...)."""

import tkinter as tk
from tkinter import ttk
from typing import Callable

from ..config import DEFAULT_SURFACE_KIND, STYLE_COMBOBOX, SURFACE_KIND_NAMES
from ..widgets import ToolTip

KIND_HELP = "Type de tracé : les classes, la palette et l'opacité sont conservées."
COMBOBOX_WIDTH = 18


class SurfaceKindCombobox(ttk.Combobox):
    """Read-only combobox showing the plot kinds by their displayed names."""

    def __init__(self, parent: tk.Misc, kind: str, on_change: Callable[[], None]) -> None:
        """Create the combobox.

        Args:
            parent: Parent widget.
            kind: Kind selected initially (one of ``SURFACE_KINDS``).
            on_change: Called when the user selects a kind.
        """
        super().__init__(
            parent,
            values=list(SURFACE_KIND_NAMES.values()),
            state="readonly",
            width=COMBOBOX_WIDTH,
            style=STYLE_COMBOBOX,
        )
        self.set(SURFACE_KIND_NAMES.get(kind, SURFACE_KIND_NAMES[DEFAULT_SURFACE_KIND]))
        self.bind("<<ComboboxSelected>>", lambda _event: on_change())
        ToolTip(self, KIND_HELP)

    @property
    def kind(self) -> str:
        """Return the selected kind (one of ``SURFACE_KINDS``)."""
        name = self.get()
        for kind, kind_name in SURFACE_KIND_NAMES.items():
            if kind_name == name:
                return kind
        return DEFAULT_SURFACE_KIND

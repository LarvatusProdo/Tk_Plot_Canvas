"""Label frame of the "Vecteurs" tab editing the vector field (arrows) drawn over the surface."""

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any, Callable

from matplotlib.colors import is_color_like

from ..config import (
    STYLE_CHECKBUTTON,
    STYLE_COMBOBOX,
    STYLE_LABEL,
    STYLE_LABELFRAME,
    VECTOR_COLORS,
    VECTOR_LENGTH_RANGE,
    VECTOR_NONE_CHOICE,
    VECTOR_STEP_RANGE,
)
from ..widgets import CheckedSpinbox, ToolTip
from .axis_frame import FRAME_PADDING, PADDING

if TYPE_CHECKING:
    from ..canvas.plot_canvas import TkPlotCanvas

COMPONENT_HELP = (
    "Variables des composantes du vecteur (ex. vent_u vers l'est, vent_v vers le nord).\n"
    "Choisir « Aucune » pour masquer les flèches."
)
STEP_HELP = "Une flèche tous les N points de grille (0 = automatique)."
LENGTH_HELP = (
    "Facteur de longueur des flèches : à 1, une flèche de la vitesse de référence\n"
    "(la plus grande de toute la variable) couvre l'écart entre deux flèches."
)
KEY_HELP = (
    "Afficher une flèche de référence avec sa valeur au-dessus du graphique.\n"
    "Sans objet quand les vecteurs sont normalisés."
)
NORMALIZE_HELP = (
    "Ramener tous les vecteurs à une norme de 1 : les flèches ont toutes la même\n"
    "longueur et n'indiquent que la direction."
)
COMPONENT_LABELS = (("u", "Composante x (u) :"), ("v", "Composante y (v) :"))
COMBOBOX_WIDTH = 15


class VectorFieldFrame:
    """Choose the vector components and the style of the arrows (applied live)."""

    def __init__(self, canvas: "TkPlotCanvas", parent: tk.Misc, row: int) -> None:
        """Create the label frame on a grid row of ``parent``.

        Args:
            canvas: The plot canvas.
            parent: Widget receiving the label frame.
            row: Grid row of the label frame.
        """
        self._canvas = canvas
        self._frame = ttk.LabelFrame(
            parent,
            text="Flèches",
            padding=FRAME_PADDING,
            style=STYLE_LABELFRAME,
        )
        self._frame.grid(row=row, column=0, columnspan=60, sticky="nw", padx=PADDING, pady=PADDING)
        self.component_vars: dict[str, tk.StringVar] = {}
        self._build_components()
        self._build_style_controls()

    def _build_components(self) -> None:
        """Create the comboboxes choosing the variables of both components."""
        choices = [VECTOR_NONE_CHOICE] + self._canvas.vector_variable_names()
        for column, (component, text) in enumerate(COMPONENT_LABELS):
            current = self._canvas.vector_field[component] or VECTOR_NONE_CHOICE
            variable = tk.StringVar(value=current if current in choices else VECTOR_NONE_CHOICE)
            self.component_vars[component] = variable
            self._add_label(0, 2 * column, text)
            combobox = ttk.Combobox(
                self._frame,
                textvariable=variable,
                values=choices,
                state="readonly",
                width=COMBOBOX_WIDTH,
                style=STYLE_COMBOBOX,
            )
            combobox.grid(row=0, column=2 * column + 1, sticky="w", padx=PADDING, pady=PADDING)
            combobox.bind("<<ComboboxSelected>>", lambda _event: self._apply_components())
            ToolTip(combobox, COMPONENT_HELP)

    def _build_style_controls(self) -> None:
        """Create the step and length spinboxes, the color combobox and the key toggle."""
        style = self._canvas.vector_field
        self._add_spinbox(1, 0, ("Pas :", STEP_HELP), self._apply_step).set_range(
            VECTOR_STEP_RANGE, style["step"]
        )
        self._add_spinbox(1, 2, ("Longueur :", LENGTH_HELP), self._apply_length).set_range(
            VECTOR_LENGTH_RANGE, style["length"]
        )
        self._add_label(1, 4, "Couleur :")
        self.color_var = tk.StringVar(value=style["color"])
        color_combobox = ttk.Combobox(
            self._frame,
            textvariable=self.color_var,
            values=VECTOR_COLORS,
            width=COMBOBOX_WIDTH,
            style=STYLE_COMBOBOX,
        )
        color_combobox.grid(row=1, column=5, sticky="w", padx=PADDING, pady=PADDING)
        for sequence in ("<<ComboboxSelected>>", "<Return>", "<FocusOut>"):
            color_combobox.bind(sequence, lambda _event: self._apply_color())
        self._build_toggles()

    def _add_label(self, row: int, column: int, text: str) -> None:
        """Add a right-aligned label.

        Args:
            row: Grid row.
            column: Grid column.
            text: Label text.
        """
        ttk.Label(self._frame, text=text, style=STYLE_LABEL).grid(
            row=row, column=column, sticky="e", padx=PADDING, pady=PADDING
        )

    def _add_spinbox(
        self, row: int, column: int, texts: tuple[str, str], on_change: Callable[[float], None]
    ) -> CheckedSpinbox:
        """Add a labelled spinbox (its range is set by the caller).

        Args:
            row: Grid row.
            column: Grid column of the label (the spinbox is on its right).
            texts: Label text and tooltip text.
            on_change: Called with each new valid value.

        Returns:
            The created spinbox.
        """
        label, help_text = texts
        self._add_label(row, column, label)
        spinbox = CheckedSpinbox(self._frame, on_change)
        spinbox.grid(row=row, column=column + 1, sticky="w", padx=PADDING, pady=PADDING)
        ToolTip(spinbox, help_text)
        return spinbox

    def _build_toggles(self) -> None:
        """Create the "normalize" and "reference arrow" checkbuttons."""
        style = self._canvas.vector_field
        self.normalize_var = tk.BooleanVar(value=style["normalize"])
        self.key_var = tk.BooleanVar(value=style["key"])
        normalize_checkbutton = self._add_checkbutton(
            (2, 0), "Normaliser les vecteurs (norme 1)", self.normalize_var, self._apply_normalize
        )
        ToolTip(normalize_checkbutton, NORMALIZE_HELP)
        self._key_checkbutton = self._add_checkbutton(
            (2, 2), "Flèche de référence", self.key_var, self._apply_key
        )
        ToolTip(self._key_checkbutton, KEY_HELP)
        self._sync_key_checkbutton()

    def _add_checkbutton(
        self,
        position: tuple[int, int],
        text: str,
        variable: tk.BooleanVar,
        command: Callable[[], None],
    ) -> ttk.Checkbutton:
        """Add a checkbutton spanning two grid columns.

        Args:
            position: Grid row and column.
            text: Checkbutton text.
            variable: Variable bound to the checkbutton.
            command: Called when the checkbutton is toggled.

        Returns:
            The created checkbutton.
        """
        checkbutton = ttk.Checkbutton(
            self._frame, text=text, variable=variable, style=STYLE_CHECKBUTTON, command=command
        )
        row, column = position
        checkbutton.grid(
            row=row, column=column, columnspan=2, sticky="w", padx=PADDING, pady=PADDING
        )
        return checkbutton

    def _sync_key_checkbutton(self) -> None:
        """Disable the reference arrow toggle while the vectors are normalized."""
        disabled = self._canvas.vector_field["normalize"]
        self._key_checkbutton.state(["disabled"] if disabled else ["!disabled"])

    def _apply_normalize(self) -> None:
        """Normalize the vectors (or not) and update the reference arrow toggle."""
        self._apply({"normalize": self.normalize_var.get()})
        self._sync_key_checkbutton()

    def _apply_key(self) -> None:
        """Show or hide the reference arrow."""
        self._apply({"key": self.key_var.get()})

    def _apply(self, changes: dict[str, Any]) -> None:
        """Apply new settings to the canvas.

        Args:
            changes: Entries of ``vector_field`` to change.
        """
        self._canvas.set_vector_field(changes)

    def _apply_components(self) -> None:
        """Apply the selected components ("Aucune" removes the arrows)."""
        changes = {}
        for component, variable in self.component_vars.items():
            name = variable.get()
            changes[component] = "" if name == VECTOR_NONE_CHOICE else name
        self._apply(changes)

    def _apply_step(self, step: float) -> None:
        """Apply a sub-sampling step.

        Args:
            step: One arrow every ``step`` grid nodes (rounded; 0 = automatic).
        """
        self._apply({"step": int(round(step))})

    def _apply_length(self, length: float) -> None:
        """Apply an arrow length factor.

        Args:
            length: Length factor (positive).
        """
        self._apply({"length": length})

    def _apply_color(self) -> None:
        """Apply the typed or selected color (an invalid one is restored)."""
        color = self.color_var.get().strip()
        if not is_color_like(color):
            self._frame.bell()
            self.color_var.set(self._canvas.vector_field["color"])
            return
        if color != self._canvas.vector_field["color"]:
            self._apply({"color": color})

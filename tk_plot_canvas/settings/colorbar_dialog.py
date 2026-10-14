"""Dialog editing the colorbar label, its font, its position and its geometry.

Every change is applied immediately; "Annuler" (or Escape) restores the
colorbar shown when the dialog opened, "Fermer" keeps the changes.
"""

import tkinter as tk
from functools import partial
from tkinter import ttk
from typing import TYPE_CHECKING, Any, Optional

from ..config import (
    COLORBAR_LOCATION_NAMES,
    STYLE_BUTTON,
    STYLE_ENTRY,
    STYLE_LABEL,
    STYLE_LABELFRAME,
)
from ..widgets import ToolTip
from .choices import displayed_names, name_of, value_of
from .font_dialogs import ColorbarFontDialog
from .window_placement import setup_dialog

if TYPE_CHECKING:
    from ..canvas.plot_canvas import TkPlotCanvas

PADDING = 5
SEPARATOR_PADY = (10, 10)
DIALOG_SIZE_COLORBAR = "440x520"
SPIN_TYPING_EVENTS = ("<Return>", "<FocusOut>")
# (style key, label, minimum, maximum, step, help)
SPIN_FIELDS = [
    ("shrink", "Longueur :", 0.1, 1.0, 0.05, "Longueur de la colorbar, en fraction (0 à 1)."),
    (
        "aspect",
        "Finesse :",
        1,
        100,
        1,
        "Rapport longueur / épaisseur : plus la valeur est grande, plus la colorbar est fine.",
    ),
    ("pad", "Distance au graphique :", 0.0, 0.5, 0.01, "Écart entre le graphique et la colorbar."),
    (
        "fraction",
        "Espace réservé :",
        0.02,
        0.5,
        0.01,
        "Part de la figure réservée à la colorbar (0 à 1).",
    ),
    ("tick_labelsize", "Taille des graduations :", 4, 40, 1, "Taille du texte des graduations."),
    ("outline_width", "Épaisseur du contour :", 0.1, 5, 0.1, "Épaisseur du cadre (en points)."),
]


class ColorbarDialog(tk.Toplevel):
    """Edit the label, font, position and geometry of the colorbar (applied live)."""

    def __init__(
        self, parent: tk.Misc, canvas: "TkPlotCanvas", colorbar: Any = None, index: int = 0
    ) -> None:
        """Create the dialog.

        Args:
            parent: Window the dialog is positioned against.
            canvas: The plot canvas being edited.
            colorbar: Unused; the colorbar displayed by ``canvas`` is edited.
            index: Index of the plot described by the colorbar.
        """
        super().__init__(parent)
        self.title("Colorbar")
        setup_dialog(self, parent, DIALOG_SIZE_COLORBAR, on_escape=self.cancel)
        self.canvas = canvas
        self.index = index
        self._initial_style = dict(canvas.colorbar_style)
        self._initial_label = self._current_label()
        frame = ttk.LabelFrame(self, text="Colorbar", padding=(10, 10), style=STYLE_LABELFRAME)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._build_label_controls(frame, parent)
        self._build_geometry_controls(frame)
        self._build_buttons()

    def _label_text(self) -> Optional[Any]:
        """Return the label of the displayed colorbar.

        Returns:
            The Matplotlib label, or None without colorbar.
        """
        from ..canvas.colorbar import colorbar_label_axis

        if self.canvas.colorbar is None:
            return None
        return colorbar_label_axis(self.canvas.colorbar).label

    def _current_label(self) -> str:
        """Return the label text of the displayed colorbar.

        Returns:
            The label text ("" without colorbar).
        """
        label = self._label_text()
        return label.get_text() if label is not None else ""

    def _add_label(self, frame: ttk.LabelFrame, text: str, row: int) -> ttk.Label:
        """Add a right-aligned field label in column 0.

        Args:
            frame: Parent frame.
            text: Label text.
            row: Grid row.

        Returns:
            The created label.
        """
        label = ttk.Label(frame, text=text, style=STYLE_LABEL)
        label.grid(row=row, column=0, sticky="e", padx=PADDING, pady=PADDING)
        return label

    def _build_label_controls(self, frame: ttk.LabelFrame, parent: tk.Misc) -> None:
        """Create the label entry (applied while typing) and the font button.

        Args:
            frame: Parent frame.
            parent: Window owning the font dialog.
        """
        self._add_label(frame, "Libellé :", 0)
        self.label_var = tk.StringVar(value=self._initial_label)
        ttk.Entry(frame, textvariable=self.label_var, width=30, style=STYLE_ENTRY).grid(
            row=0, column=1, sticky="w", padx=PADDING, pady=PADDING
        )
        self.label_var.trace_add("write", self._on_label_changed)
        ttk.Button(
            frame,
            text="Police du libellé…",
            style=STYLE_BUTTON,
            command=partial(
                self.canvas.dialogs.show,
                "font:colorbar",
                partial(ColorbarFontDialog, parent, self.canvas),
            ),
        ).grid(row=10, column=0, columnspan=3, sticky="we", padx=PADDING, pady=PADDING)

    def _build_geometry_controls(self, frame: ttk.LabelFrame) -> None:
        """Create the position combobox and the geometry spinboxes.

        Args:
            frame: Parent frame.
        """
        ttk.Separator(frame, orient="horizontal").grid(
            row=20, column=0, columnspan=3, sticky="we", pady=SEPARATOR_PADY
        )
        style = self.canvas.colorbar_style
        self._add_label(frame, "Position :", 30)
        self.location_var = tk.StringVar(value=name_of(COLORBAR_LOCATION_NAMES, style["location"]))
        location_combobox = ttk.Combobox(
            frame,
            values=displayed_names(COLORBAR_LOCATION_NAMES),
            textvariable=self.location_var,
            state="readonly",
            width=15,
        )
        location_combobox.grid(row=30, column=1, sticky="w", padx=PADDING, pady=PADDING)
        location_combobox.bind("<<ComboboxSelected>>", lambda _event: self.apply_geometry())
        self.style_vars: dict[str, tk.StringVar] = {}
        for row, field in enumerate(SPIN_FIELDS, start=31):
            self._add_spinbox(frame, row, *field)

    def _add_spinbox(
        self,
        frame: ttk.LabelFrame,
        row: int,
        key: str,
        text: str,
        low: float,
        high: float,
        step: float,
        help_text: str,
    ) -> None:
        """Create one labeled geometry spinbox, applied by its arrows, Enter or on leaving.

        Args:
            frame: Parent frame.
            row: Grid row.
            key: ``colorbar_style`` key.
            text: Field label.
            low: Minimum of the arrows.
            high: Maximum of the arrows.
            step: Arrow increment.
            help_text: Tooltip text.
        """
        ToolTip(self._add_label(frame, text, row), help_text)
        self.style_vars[key] = tk.StringVar(value=str(self.canvas.colorbar_style[key]))
        spinbox = ttk.Spinbox(
            frame,
            textvariable=self.style_vars[key],
            from_=low,
            to=high,
            increment=step,
            width=8,
            command=self.apply_geometry,
        )
        spinbox.grid(row=row, column=1, sticky="w", padx=PADDING, pady=PADDING)
        for sequence in SPIN_TYPING_EVENTS:
            spinbox.bind(sequence, lambda _event: self.apply_geometry())
        ToolTip(spinbox, help_text)

    def _build_buttons(self) -> None:
        """Create the "Annuler" and "Fermer" buttons."""
        frame = ttk.Frame(self)
        frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(frame, text="Fermer", style=STYLE_BUTTON, command=self.destroy).pack(
            side="right"
        )
        ttk.Button(frame, text="Annuler", style=STYLE_BUTTON, command=self.cancel).pack(
            side="right", padx=10
        )

    def _typed_style(self) -> dict[str, Any]:
        """Read the position and geometry; invalid values are replaced by the current ones.

        Returns:
            The ``colorbar_style`` entries to apply.
        """
        style: dict[str, Any] = {
            "location": value_of(COLORBAR_LOCATION_NAMES, self.location_var.get())
        }
        for key, variable in self.style_vars.items():
            current = self.canvas.colorbar_style[key]
            try:
                value = float(variable.get().strip().replace(",", "."))
            except ValueError:
                value = -1.0
            if value < 0 or (value == 0 and key != "pad"):
                variable.set(str(current))
                self.bell()
                value = current
            style[key] = value
        return style

    def apply_geometry(self) -> None:
        """Apply the position and geometry when they changed (the colorbar is rebuilt)."""
        style = self._typed_style()
        current = {key: self.canvas.colorbar_style[key] for key in style}
        if style == current:
            return
        self.canvas.set_colorbar_style(style, self.index)
        self.canvas.figure_canvas.draw_idle()

    def cancel(self) -> None:
        """Restore the colorbar shown when the dialog opened, then close the dialog."""
        self.canvas.set_colorbar_style(dict(self._initial_style), self.index)
        label = self._label_text()
        if label is not None:
            label.set_text(self._initial_label)
        self.canvas.figure_canvas.draw_idle()
        self.destroy()

    def _on_label_changed(self, *_trace_args: Any) -> None:
        """Update the colorbar label while the user types.

        Args:
            *_trace_args: Tk variable trace arguments (unused).
        """
        label = self._label_text()
        if label is not None:
            label.set_text(self.label_var.get())
            self.canvas.figure_canvas.draw_idle()

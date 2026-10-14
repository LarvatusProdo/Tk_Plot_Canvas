"""Group of widgets editing one font: family, size, style, bold and color."""

import tkinter as tk
from dataclasses import dataclass
from functools import partial
from tkinter import colorchooser, ttk

from ..config import (
    DEFAULT_FONT_SIZE,
    FONT_SIZE_RANGE,
    FONT_STYLES,
    STYLE_CHECKBUTTON,
    STYLE_LABEL,
)

LABEL_PADDING = (5, 5)
FIELD_PADDING = 5


@dataclass
class FontChoice:
    """Font selected by the user.

    Attributes:
        family: Font family.
        size: Font size, as typed in the spinbox.
        style: "normal", "italic" or "oblique".
        weight: "bold" or "normal".
        color: Font color.
    """

    family: str
    size: str
    style: str
    weight: str
    color: str


class FontControls:
    """Font editing widgets laid out in a label frame."""

    def __init__(self, frame: ttk.LabelFrame, font_families: list[str], dialog: tk.Misc) -> None:
        """Create the widgets.

        Args:
            frame: Label frame receiving the widgets.
            font_families: Choices of the font family combobox.
            dialog: Window owning the color chooser.
        """
        self._frame = frame
        self._font_families = font_families
        self._dialog = dialog
        self._build_family_and_size_rows()
        self._build_style_row()
        self._add_label("Couleur de la police:", 3)
        self.color_button = tk.Button(frame, width=3)
        self.color_button.grid(row=3, column=1, sticky="w", padx=FIELD_PADDING, pady=FIELD_PADDING)
        self.color_button.configure(command=partial(self._choose_color, self.color_button))

    def _build_family_and_size_rows(self) -> None:
        """Create the font family combobox and the (empty) size spinbox."""
        self._add_label("Police :", 0)
        self.family_combobox = ttk.Combobox(
            self._frame, values=self._font_families, state="readonly", width=20
        )
        self.family_combobox.grid(
            row=0, column=1, sticky="w", columnspan=2, padx=FIELD_PADDING, pady=FIELD_PADDING
        )
        self._add_label("Taille de la police :", 1)
        self.size_spinbox = ttk.Spinbox(
            self._frame, from_=FONT_SIZE_RANGE[0], to=FONT_SIZE_RANGE[1], increment=1, width=10
        )
        self.size_spinbox.grid(
            row=1, column=1, columnspan=2, sticky="w", padx=FIELD_PADDING, pady=FIELD_PADDING
        )
        self.size_spinbox.delete(0, "end")

    def _add_label(self, text: str, row: int) -> None:
        """Add a right-aligned field label in column 0.

        Args:
            text: Label text.
            row: Grid row.
        """
        ttk.Label(self._frame, text=text, style=STYLE_LABEL).grid(
            row=row, column=0, sticky="e", padx=LABEL_PADDING, pady=LABEL_PADDING
        )

    def _build_style_row(self) -> None:
        """Create the font style combobox and the bold checkbutton."""
        self._add_label("Styles de la police:", 2)
        self.style_combobox = ttk.Combobox(
            self._frame, values=FONT_STYLES, state="readonly", width=10
        )
        self.style_combobox.grid(
            row=2, column=1, sticky="w", padx=FIELD_PADDING, pady=FIELD_PADDING
        )
        self.style_combobox.current(0)
        self.bold_var = tk.BooleanVar(value=False)
        self.bold_checkbutton = ttk.Checkbutton(
            self._frame, text="Gras", variable=self.bold_var, style=STYLE_CHECKBUTTON
        )
        self.bold_checkbutton.grid(
            row=2, column=2, sticky="w", padx=FIELD_PADDING, pady=FIELD_PADDING
        )
        self.bold_checkbutton.configure(state=["selected"])

    def _choose_color(self, button: tk.Button) -> None:
        """Ask for a color and show it on the color button.

        Args:
            button: Button whose background displays the color.
        """
        color_code = colorchooser.askcolor(
            button.cget("bg"), parent=self._dialog, title="Choisir une couleur de police"
        )
        if color_code and color_code[1]:
            button.configure(bg=color_code[1])

    def set_family(self, family: str) -> None:
        """Select a font family (the first one when unknown).

        Args:
            family: Font family.
        """
        families = self._font_families
        self.family_combobox.current(families.index(family) if family in families else 0)

    def set_size(self, size: int) -> None:
        """Insert a font size in the spinbox.

        Args:
            size: Font size.
        """
        self.size_spinbox.insert(0, size)

    def set_style(self, style: str) -> None:
        """Show a font style.

        Args:
            style: "normal", "italic" or "oblique".
        """
        self.style_combobox.set(style)

    def set_bold(self, is_bold: bool) -> None:
        """Check or uncheck the bold checkbutton.

        Args:
            is_bold: Whether the font is bold.
        """
        self.bold_checkbutton.state(["selected"] if is_bold else ["!selected"])
        self.bold_var.set(is_bold)

    def set_color(self, color: str) -> None:
        """Show a font color on the color button.

        Args:
            color: Font color.
        """
        self.color_button.configure(bg=color)

    def _typed_size(self) -> str:
        """Return the typed font size, clamped to the allowed range.

        Returns:
            The whole size as text (the default size when the entry is not a number).
        """
        minimum, maximum = FONT_SIZE_RANGE
        try:
            size = float(self.size_spinbox.get().strip().replace(",", "."))
        except ValueError:
            return str(DEFAULT_FONT_SIZE)
        return str(round(min(max(size, minimum), maximum)))

    def read(self) -> FontChoice:
        """Return the font currently selected in the widgets.

        Returns:
            The selected font.
        """
        return FontChoice(
            family=self.family_combobox.get(),
            size=self._typed_size(),
            style=self.style_combobox.get(),
            weight="bold" if self.bold_var.get() else "normal",
            color=self.color_button.cget("bg"),
        )

"""Settings tab "Cartouche": visibility, displayed columns and their values."""

import tkinter as tk
from functools import partial
from tkinter import ttk

from ..config import (
    STYLE_BUTTON,
    STYLE_CARTOUCHE_CELL,
    STYLE_CARTOUCHE_HEADER,
    STYLE_CHECKBUTTON,
    STYLE_ENTRY,
    STYLE_SECTION_TITLE,
)
from .base_tab import SettingsTab
from .font_dialogs import CartoucheFontDialog

FIELD_WIDTH = 15
CELL_PADDING = 5
NO_KEY = "None"


class CartoucheTab(SettingsTab):
    """Choose the metadata columns of the cartouche and edit their values.

    Attributes:
        key_comboboxes: One combobox per cartouche column (metadata key).
        value_entries: Per curve, one entry per cartouche column.
    """

    def build(self) -> None:
        """Create the header widgets and the column grid."""
        self._build_header()
        self.key_comboboxes: list[ttk.Combobox] = []
        self.value_entries: list[list[ttk.Entry]] = [[] for _ in self.canvas.lines]
        for index in range(len(self.canvas.lines)):
            label = self._label_of(index)
            if index == 0:
                self._build_key_selectors(label)
            self._build_value_row(index, label)

    def _build_header(self) -> None:
        """Create the title, the visibility toggle and the font button."""
        self.show_var = tk.BooleanVar(value=self.canvas.show_cartouche)
        show_checkbutton = ttk.Checkbutton(
            self.frame,
            text="Afficher le cartouche",
            variable=self.show_var,
            style=STYLE_CHECKBUTTON,
            command=self._toggle_cartouche,
        )
        show_checkbutton.grid(row=0, column=0, sticky="w", padx=5, pady=10, columnspan=3)
        ttk.Button(
            self.frame,
            text="Polices…",
            style=STYLE_BUTTON,
            command=self._open_font_dialog,
        ).grid(row=0, column=4, sticky="w", padx=5, pady=10, columnspan=2)

    def _open_font_dialog(self) -> None:
        """Open the dialog editing the cartouche fonts (or bring it back to the front)."""
        self.canvas.dialogs.show(
            "font:cartouche", partial(CartoucheFontDialog, self.window, self.canvas)
        )

    def _label_of(self, index: int) -> dict:
        """Return the metadata of a curve ({} when it has none).

        Args:
            index: Curve index.

        Returns:
            The curve metadata.
        """
        return self.canvas.line_labels[index] or {}

    def _build_key_selectors(self, label: dict) -> None:
        """Create one key combobox per metadata entry of the first curve.

        Args:
            label: Metadata of the first curve.
        """
        if label:
            ttk.Label(self.frame, text="Colonne :", style=STYLE_SECTION_TITLE).grid(
                row=1, column=0, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING
            )
        choices = [""] + list(label.keys())
        headers = self.canvas.cartouche_headers
        for column in range(1, len(label) + 1):
            combobox = ttk.Combobox(
                self.frame, values=choices, state="readonly", width=FIELD_WIDTH
            )
            combobox.grid(row=1, column=column, padx=CELL_PADDING, pady=CELL_PADDING)
            shown_key = headers[column - 1].cget("text") if column - 1 < len(headers) else NO_KEY
            combobox.current(choices.index(shown_key) if shown_key in choices else 0)
            combobox.bind(
                "<<ComboboxSelected>>",
                partial(self._on_key_selected, combobox=combobox, column_index=column - 1),
            )
            self.key_comboboxes.append(combobox)

    def _build_value_row(self, index: int, label: dict) -> None:
        """Create the value entries of one curve.

        Args:
            index: Curve index.
            label: Curve metadata.
        """
        ttk.Label(self.frame, text=str(index + 1), style=STYLE_SECTION_TITLE).grid(
            row=index + 2, column=0, sticky="e", padx=CELL_PADDING, pady=CELL_PADDING
        )
        for column, combobox in enumerate(self.key_comboboxes, start=1):
            shown_key = combobox.get()
            entry = ttk.Entry(self.frame, width=FIELD_WIDTH, style=STYLE_ENTRY)
            entry.bind(
                "<KeyRelease>",
                partial(self._on_value_edited, line_index=index, column_index=column - 1),
            )
            entry.grid(
                row=index + 2, column=column, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING
            )
            self.value_entries[index].append(entry)
            if shown_key in label:
                entry.insert(0, label[shown_key])

    def _on_value_edited(self, event: tk.Event, line_index: int, column_index: int) -> None:
        """Store an edited value in the curve metadata and in the cartouche.

        Args:
            event: Key event of the edited entry.
            line_index: Curve index.
            column_index: Cartouche column index (0-based, without symbol).
        """
        new_value = event.widget.get()
        key = self.key_comboboxes[column_index].get()
        if key:
            self.canvas.line_labels[line_index][key] = new_value
            self._replace_cell(line_index, column_index + 1, new_value)

    def _replace_cell(self, line_index: int, column: int, value: object) -> None:
        """Replace one cartouche cell by a new label.

        Args:
            line_index: Curve index.
            column: Grid column (column 0 is the line symbol).
            value: Value to display.
        """
        row = self.canvas.cartouche_rows[line_index]
        try:
            row[column].destroy()
        except (IndexError, AttributeError, tk.TclError):
            pass
        row[column] = ttk.Label(
            self.canvas.cartouche_frame, text=str(value), style=STYLE_CARTOUCHE_CELL
        )
        row[column].grid(
            row=line_index + 1, column=column, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING
        )

    def _on_key_selected(self, event: tk.Event, combobox: ttk.Combobox, column_index: int) -> None:
        """Show another metadata key in a cartouche column.

        Args:
            event: Combobox event (unused).
            combobox: Combobox whose key changed.
            column_index: Cartouche column index (0-based, without symbol).
        """
        key = combobox.get()
        self._replace_header(column_index, key)
        for index in range(len(self.canvas.lines)):
            label = self._label_of(index)
            value = label[key] if key in label else ""
            row = self.canvas.cartouche_rows[index]
            while len(row) < column_index + 2:
                row.append(
                    ttk.Label(self.canvas.cartouche_frame, text="", style=STYLE_CARTOUCHE_HEADER)
                )
            self._replace_cell(index, column_index + 1, value)
        for index in range(len(self.canvas.lines)):
            if len(self.value_entries[index]) > 0:
                label = self._label_of(index)
                entry = self.value_entries[index][column_index]
                entry.delete(0, tk.END)
                entry.insert(0, str(label[key]) if key in label else "")

    def _replace_header(self, column_index: int, key: str) -> None:
        """Replace the title of a cartouche column.

        Args:
            column_index: Cartouche column index (0-based, without symbol).
            key: New column title.
        """
        headers = self.canvas.cartouche_headers
        try:
            headers[column_index].destroy()
        except (IndexError, tk.TclError):
            pass
        while len(headers) < column_index + 1:
            headers.append(
                ttk.Label(self.canvas.cartouche_frame, text="", style=STYLE_CARTOUCHE_HEADER)
            )
        headers[column_index] = ttk.Label(
            self.canvas.cartouche_frame, text=key, style=STYLE_CARTOUCHE_HEADER
        )
        headers[column_index].grid(
            row=0, column=column_index + 1, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING
        )

    def _toggle_cartouche(self) -> None:
        """Show or hide the cartouche below the plot."""
        self.canvas.set_cartouche_visible(self.show_var.get())

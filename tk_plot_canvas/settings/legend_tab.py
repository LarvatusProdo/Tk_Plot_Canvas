"""Settings tab "Légende": legend visibility, displayed keys and values."""

import tkinter as tk
from functools import partial
from tkinter import ttk
from typing import Optional

from ..config import STYLE_BUTTON, STYLE_CHECKBUTTON, STYLE_ENTRY, STYLE_SECTION_TITLE
from .base_tab import SettingsTab

FIELD_WIDTH = 15
CELL_PADDING = 5


class LegendTab(SettingsTab):
    """Choose which metadata keys form the legend and edit their values.

    Attributes:
        key_comboboxes: One combobox per legend key.
        value_entries: Per curve, one entry per legend key.
    """

    def build(self) -> None:
        """Create the header widgets and the key/value grid."""
        self._build_header()
        self.key_comboboxes: list[ttk.Combobox] = []
        self.value_entries: list[list[ttk.Entry]] = [[] for _ in self.canvas.lines]
        for index in range(len(self.canvas.lines)):
            label = self.canvas.line_labels[index] or {}
            if len(self.key_comboboxes) == 0:
                self._build_key_selectors(label)
            self._build_value_row(index, label)

    def _build_header(self) -> None:
        """Create the title, the toggles and the position button."""
        self.show_legend_var = tk.BooleanVar(value=self.canvas.axes.get_legend() is not None)
        self._add_checkbutton("Afficher la légende", self.show_legend_var, column=0)
        self.show_key_names_var = tk.BooleanVar(value=self.canvas.show_legend_key_names)
        self._add_checkbutton(
            "Afficher le nom des clés (clé : valeur)", self.show_key_names_var, column=2
        )
        ttk.Button(
            self.frame,
            text="Replacer automatiquement",
            command=self._reset_legend_position,
            style=STYLE_BUTTON,
        ).grid(row=0, column=4, columnspan=2, sticky="we", padx=CELL_PADDING, pady=CELL_PADDING)

    def _add_checkbutton(self, text: str, variable: tk.BooleanVar, column: int) -> None:
        """Add a checkbutton refreshing the legend when toggled.

        Args:
            text: Checkbutton text.
            variable: Variable bound to the checkbutton.
            column: Grid column (row 1).
        """
        ttk.Checkbutton(
            self.frame,
            text=text,
            variable=variable,
            command=self.apply_legend_settings,
            style=STYLE_CHECKBUTTON,
        ).grid(
            row=1, column=column, columnspan=2, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING
        )

    def _build_key_selectors(self, label: dict) -> None:
        """Create one key combobox per metadata entry of a curve.

        Args:
            label: Curve metadata.
        """
        ttk.Label(self.frame, text="Clé :", style=STYLE_SECTION_TITLE).grid(
            row=2, column=0, sticky="w", padx=CELL_PADDING, pady=CELL_PADDING
        )
        choices = [""] + list(label.keys())
        legend_keys = self.canvas.legend_keys
        for column_index in range(len(label)):
            combobox = ttk.Combobox(
                self.frame, values=choices, state="readonly", width=FIELD_WIDTH
            )
            combobox.grid(row=2, column=column_index + 1, padx=CELL_PADDING, pady=CELL_PADDING)
            shown_key = legend_keys[column_index] if column_index < len(legend_keys) else ""
            combobox.current(choices.index(shown_key) if shown_key in choices else 0)
            combobox.bind(
                "<<ComboboxSelected>>",
                partial(self._on_key_selected, combobox=combobox, column_index=column_index),
            )
            self.key_comboboxes.append(combobox)

    def _build_value_row(self, index: int, label: dict) -> None:
        """Create the value entries of one curve.

        Args:
            index: Curve index.
            label: Curve metadata.
        """
        ttk.Label(self.frame, text=str(index + 1), style=STYLE_SECTION_TITLE).grid(
            row=index + 3, column=0, sticky="e", padx=CELL_PADDING, pady=CELL_PADDING
        )
        for column_index, combobox in enumerate(self.key_comboboxes):
            shown_key = combobox.get()
            entry = ttk.Entry(self.frame, width=FIELD_WIDTH, style=STYLE_ENTRY)
            entry.grid(
                row=index + 3,
                column=column_index + 1,
                sticky="w",
                padx=CELL_PADDING,
                pady=CELL_PADDING,
            )
            entry.bind(
                "<KeyRelease>", partial(self._on_value_edited, row=index, column=column_index)
            )
            self.value_entries[index].append(entry)
            if shown_key in label and shown_key in self.canvas.legend_keys:
                entry.insert(0, label[shown_key])

    def _on_key_selected(self, event: tk.Event, combobox: ttk.Combobox, column_index: int) -> None:
        """Show the values of the newly selected key and refresh the legend.

        Args:
            event: Combobox event (unused).
            combobox: Combobox whose key changed.
            column_index: Legend column index.
        """
        key = combobox.get()
        for index in range(len(self.canvas.lines)):
            if len(self.value_entries[index]) == 0:
                continue
            label = self.canvas.line_labels[index] or {}
            entry = self.value_entries[index][column_index]
            entry.delete(0, tk.END)
            entry.insert(0, str(label[key]) if key in label else "")
        self.apply_legend_settings()

    def apply_legend_settings(self, event: Optional[tk.Event] = None) -> None:
        """Push the selected keys and toggles to the canvas and refresh the legend.

        Args:
            event: Tk event (unused).
        """
        self.canvas.legend_keys = self.selected_keys()
        self.canvas.show_legend_key_names = self.show_key_names_var.get()
        self.canvas.show_legend = self.show_legend_var.get()
        self.canvas.refresh_legend()

    def selected_keys(self) -> list[str]:
        """Return the non-empty keys selected in the comboboxes.

        Returns:
            The legend keys, in column order.
        """
        return [combobox.get() for combobox in self.key_comboboxes if combobox.get() != ""]

    def _on_value_edited(
        self, event: Optional[tk.Event] = None, row: int = 0, column: int = 0
    ) -> None:
        """Store an edited legend value in the curve metadata.

        Args:
            event: Key event (unused).
            row: Curve index.
            column: Legend column index.
        """
        legend_keys = self.canvas.legend_keys
        key = legend_keys[column] if column < len(legend_keys) else ""
        if key != "":
            self.canvas.line_labels[row][key] = self.value_entries[row][column].get()
        self.apply_legend_settings()

    def _reset_legend_position(self) -> None:
        """Move the legend back to its automatic position."""
        location = "best" if self.show_legend_var.get() else None
        self.canvas.show_draggable_legend(location)
        self.redraw()

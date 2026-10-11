"""Editor of manual contour classes: one ``[left ; right]`` row per class.

The left bound of every row except the first is disabled and mirrors the
right bound of the previous row. Hovering a row highlights it and reveals a
button that removes the row.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, NamedTuple, Optional, Sequence

from ..config import (
    CLASS_EDITOR_WIDTH,
    STYLE_BUTTON,
    STYLE_HOVER_ENTRY,
    STYLE_HOVER_FRAME,
    STYLE_HOVER_LABEL,
    STYLE_SECTION_TITLE,
)
from .scrolled_frame import VerticalScrolledFrame

DEFAULT_MANUAL_CLASSES = [0, 1, 2]
ROW_PADY = (5, 5)
NUMBER_LABEL_PADX = (10, 5)
REMOVE_BUTTON_PADX = (20, 100)
ROW_SPACER_TEXT = " " * 19
ENTRY_WIDTH = 10


class ClassRow(NamedTuple):
    """Widgets and variables of one manual class row."""

    left_entry: ttk.Entry
    right_entry: ttk.Entry
    left_var: tk.StringVar
    right_var: tk.StringVar


class ManualClassesEditor(ttk.Frame):
    """Frame listing editable class intervals.

    Attributes:
        rows: The class rows, from first to last.
    """

    def __init__(self, master: tk.Misc, classes: Sequence[float]) -> None:
        """Build the editor.

        Args:
            master: Parent widget.
            classes: Class bounds; ``n`` bounds produce ``n - 1`` rows.
        """
        super().__init__(master)
        self.rows: list[ClassRow] = []
        self._is_updating_link = False
        self._row_frames: set[ttk.Frame] = set()
        self._row_buttons: dict[ttk.Frame, list[tuple[ttk.Button, dict]]] = {}
        if len(classes) == 0:
            classes = DEFAULT_MANUAL_CLASSES
        self._build(list(classes))

    def _build(self, classes: list[float]) -> None:
        """Create the header, the "add row" button and the initial rows.

        Args:
            classes: Class bounds.
        """
        self.rows_container = VerticalScrolledFrame(self, width=CLASS_EDITOR_WIDTH)
        ttk.Label(self, text="Paramètres pour la classe : Manuel", style=STYLE_SECTION_TITLE).pack(
            side="top", fill="x", padx=5, pady=5
        )
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(side="top", fill="x", padx=5, pady=(5, 0))
        ttk.Button(
            buttons_frame,
            text="Ajout d'une ligne",
            style=STYLE_BUTTON,
            command=self.append_row,
        ).pack(side="left", padx=10)
        self.rows_container.pack(side="bottom", fill="both", expand=True)
        for index in range(len(classes) - 1):
            self._add_row(index, classes[index], classes[index + 1])
        self._configure_row_states()

    def append_row(self) -> None:
        """Append a row whose left bound copies the previous right bound."""
        index = len(self.rows)
        left_value = self.rows[index - 1].right_var.get() if index > 0 else ""
        self._add_row(index, left_value, "")
        self._configure_row_states()

    def first_left_value(self) -> Optional[str]:
        """Return the left bound of the first row.

        Returns:
            The raw text of the first left bound, or None without rows.
        """
        return self.rows[0].left_var.get() if self.rows else None

    def _add_row(self, index: int, left_value: Any, right_value: Any) -> None:
        """Create and display one class row.

        Args:
            index: Zero-based row number (displayed as ``index + 1``).
            left_value: Initial left bound.
            right_value: Initial right bound.
        """
        row = ttk.Frame(self.rows_container, style=STYLE_HOVER_FRAME)
        self._row_frames.add(row)
        self.bind_hover(row, row)
        self._add_label(row, f"n°{index + 1} :", 0, "e", NUMBER_LABEL_PADX)
        left_var = tk.StringVar(value=str(left_value))
        right_var = tk.StringVar(value=str(right_value))
        self._add_label(row, "[", 1, "e", 0)
        left_entry = self._add_entry(row, left_var, 2)
        self._add_label(row, "; ", 3, "w", 0)
        right_entry = self._add_entry(row, right_var, 4)
        self._add_label(row, "]", 5, "w", 0)
        self._add_remove_button(row)
        self._add_label(row, ROW_SPACER_TEXT, 10, "we", 0)
        self.rows.append(ClassRow(left_entry, right_entry, left_var, right_var))
        row.pack(side="top", fill="x", padx=5, pady=2, expand=True)

    def _add_label(self, row: ttk.Frame, text: str, column: int, sticky: str, padx: Any) -> None:
        """Add a hover-aware label to a row.

        Args:
            row: Row frame.
            text: Label text.
            column: Grid column.
            sticky: Grid sticky option.
            padx: Horizontal padding.
        """
        label = ttk.Label(row, text=text, style=STYLE_HOVER_LABEL)
        label.grid(row=0, column=column, sticky=sticky, padx=padx, pady=ROW_PADY)
        self.bind_hover(label, row)

    def _add_entry(self, row: ttk.Frame, variable: tk.StringVar, column: int) -> ttk.Entry:
        """Add a hover-aware centered entry to a row.

        Args:
            row: Row frame.
            variable: Variable bound to the entry.
            column: Grid column.

        Returns:
            The created entry.
        """
        entry = ttk.Entry(
            row,
            width=ENTRY_WIDTH,
            style=STYLE_HOVER_ENTRY,
            textvariable=variable,
            justify="center",
        )
        entry.grid(row=0, column=column, sticky="w", pady=ROW_PADY)
        self.bind_hover(entry, row)
        return entry

    def _add_remove_button(self, row: ttk.Frame) -> None:
        """Add the (initially hidden) button that removes a row.

        Args:
            row: Row frame.
        """
        button = ttk.Button(
            row,
            text="x",
            width=3,
            style=STYLE_BUTTON,
            command=lambda: self._remove_row(row),
        )
        button.grid(row=0, column=8, sticky="w", padx=REMOVE_BUTTON_PADX, pady=0)
        self.bind_hover(button, row)
        self._row_buttons[row] = [(button, button.grid_info())]
        button.grid_forget()

    def _configure_row_states(self) -> None:
        """Disable linked left bounds and link each right bound to the next row."""
        for index, row in enumerate(self.rows):
            row.left_entry.configure(state="disabled" if index > 0 else "normal")
            row.right_var.trace_add("write", self._make_link_callback(index))

    def _make_link_callback(self, index: int) -> Any:
        """Build a variable-trace callback bound to a row index.

        Args:
            index: Row whose right bound is traced.

        Returns:
            A callback accepting the Tk trace arguments.
        """
        return lambda *_trace_args: self._on_right_changed(index)

    def _on_right_changed(self, index: int) -> None:
        """Copy a right bound into the left bound of the following row.

        Args:
            index: Row whose right bound changed.
        """
        if self._is_updating_link or index + 1 >= len(self.rows):
            return
        self._is_updating_link = True
        try:
            value = self.rows[index].right_var.get()
            self.rows[index + 1].left_var.set(value)
        finally:
            self._is_updating_link = False

    def bind_hover(self, widget: tk.Misc, row: Optional[ttk.Frame] = None) -> None:
        """Highlight ``row`` when the pointer enters or leaves ``widget``.

        Args:
            widget: Widget receiving the pointer events.
            row: Row to highlight (defaults to the widget's row frame).
        """
        if row is None and widget.master in self._row_frames:
            row = widget.master
        if row is not None:
            widget.bind("<Enter>", lambda _event: self._on_row_hover(row))
            widget.bind("<Leave>", lambda _event: self._on_row_hover(row))

    def _on_row_hover(self, row: ttk.Frame) -> None:
        """Update the highlight and the remove button of a row.

        Args:
            row: Row frame under or leaving the pointer.
        """
        is_inside = self._is_pointer_inside(row)
        state = ["active"] if is_inside else ["!active"]
        buttons = self._row_buttons.get(row, [])
        button_widgets = [button for button, _ in buttons]
        for widget in [row] + [c for c in row.winfo_children() if c not in button_widgets]:
            try:
                widget.state(state)
            except tk.TclError:
                pass
        for button, grid_info in buttons:
            if is_inside:
                button.grid(**grid_info)
            else:
                button.grid_forget()

    @staticmethod
    def _is_pointer_inside(row: ttk.Frame) -> bool:
        """Tell whether the mouse pointer is over ``row`` or one of its children.

        Args:
            row: Row frame.

        Returns:
            True when the widget under the pointer belongs to ``row``.
        """
        try:
            toplevel = row.winfo_toplevel()
            widget = toplevel.winfo_containing(
                toplevel.winfo_pointerx(), toplevel.winfo_pointery()
            )
            while widget is not None and widget is not row:
                widget = widget.master
        except tk.TclError:
            return False
        return widget is not None

    def _remove_row(self, row_frame: ttk.Frame) -> None:
        """Remove a class row.

        Args:
            row_frame: Frame of the row to remove.
        """
        for index, row in enumerate(self.rows):
            if row.left_entry.master == row_frame:
                self.rows.pop(index)
                self._row_buttons.pop(row_frame, None)
                self._row_frames.discard(row_frame)
                row_frame.destroy()
                break

"""Spinbox applying a typed number as soon as it is valid.

Typing applies valid values silently; leaving the field (or pressing Return)
with an invalid value restores the last applied one.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from ..config import STYLE_SPINBOX

CHECK_EVENTS = ("<Return>", "<FocusOut>")
SPINBOX_WIDTH = 5


class CheckedSpinbox(ttk.Spinbox):
    """Numeric spinbox bounded to a range, reporting each new valid value.

    Its range and value are set with :meth:`set_range` after creation.

    Attributes:
        variable: Text shown in the spinbox.
    """

    def __init__(self, parent: tk.Misc, on_change: Callable[[float], None]) -> None:
        """Create the spinbox (empty until :meth:`set_range` is called).

        Args:
            parent: Parent widget.
            on_change: Called with each new valid value.
        """
        self.variable = tk.StringVar()
        super().__init__(
            parent,
            width=SPINBOX_WIDTH,
            style=STYLE_SPINBOX,
            textvariable=self.variable,
            command=self._apply,
        )
        self._on_change = on_change
        self._range = (0.0, 0.0)
        self._value = 0.0
        self.bind("<KeyRelease>", lambda _event: self._apply())
        for sequence in CHECK_EVENTS:
            self.bind(sequence, lambda _event: self._validate())

    def set_range(self, value_range: tuple[float, float, float], value: float) -> None:
        """Change the allowed range and show a new value (without reporting it).

        Args:
            value_range: ``(minimum, maximum, increment)``.
            value: Value to show.
        """
        minimum, maximum, increment = value_range
        self.configure(from_=minimum, to=maximum, increment=increment)
        self._range = (minimum, maximum)
        self._value = value
        self.variable.set(str(value))

    def typed_value(self) -> Optional[float]:
        """Read the typed number (a comma is accepted as decimal separator).

        Returns:
            The number, or None when it is not a number within the range.
        """
        text = self.variable.get().strip().replace(",", ".")
        try:
            value = float(text)
        except ValueError:
            return None
        minimum, maximum = self._range
        return value if minimum <= value <= maximum else None

    def _apply(self) -> None:
        """Report the typed value when it is valid and new (the user may still be typing)."""
        value = self.typed_value()
        if value is not None and value != self._value:
            self._value = value
            self._on_change(value)

    def _validate(self) -> None:
        """Apply the typed value, or restore the last applied one when it is invalid."""
        if self.typed_value() is not None:
            self._apply()
            return
        self.variable.set(str(self._value))
        self.bell()

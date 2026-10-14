"""Registry keeping at most one open dialog per edited element."""

import tkinter as tk
from typing import Callable


def is_window_open(window: tk.Misc) -> bool:
    """Tell whether a window still exists.

    Args:
        window: Window to check.

    Returns:
        True when the window has not been destroyed.
    """
    try:
        return bool(window.winfo_exists())
    except tk.TclError:
        return False


class DialogManager:
    """Open dialogs by key, bringing back an already open one instead of duplicating it."""

    def __init__(self) -> None:
        """Create an empty registry."""
        self._dialogs: dict[str, tk.Toplevel] = {}

    def show(self, key: str, factory: Callable[[], tk.Toplevel]) -> tk.Toplevel:
        """Bring the dialog of ``key`` to the front, creating it when needed.

        Args:
            key: Identifier of the edited element, e.g. "font:xlabel".
            factory: Creates the dialog when none is open for ``key``.

        Returns:
            The open dialog.
        """
        dialog = self._dialogs.get(key)
        if dialog is not None and is_window_open(dialog):
            dialog.deiconify()
            dialog.lift()
            dialog.focus_set()
            return dialog
        dialog = factory()
        self._dialogs[key] = dialog
        return dialog

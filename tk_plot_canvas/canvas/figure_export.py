"""Export of the figure to an image file and copy to the clipboard."""

from tkinter import filedialog, messagebox
from typing import Any

import numpy as np

from ..clipboard import copy_image_to_clipboard, is_image_copy_supported
from ..config import (
    EXPORT_DEFAULT_EXTENSION,
    EXPORT_DPI,
    EXPORT_FILE_TYPES,
    FILE_DIALOG_INITIAL_DIR,
)


class FigureExportMixin:
    """Save the figure as an image, or copy it to the clipboard.

    Requires the host canvas attributes ``figure`` and ``figure_canvas`` and
    the method ``_dialog_parent``.
    """

    def export_image(self, *_args: Any) -> None:
        """Ask for a file name and save the figure (PNG, PDF, SVG or JPEG).

        Args:
            *_args: Ignored (Tk event when used as a key binding).
        """
        path = filedialog.asksaveasfilename(
            parent=self._dialog_parent(),
            initialdir=FILE_DIALOG_INITIAL_DIR,
            title="Exporter l'image",
            defaultextension=EXPORT_DEFAULT_EXTENSION,
            filetypes=EXPORT_FILE_TYPES,
        )
        if not path:
            return
        try:
            self.figure.savefig(path, dpi=EXPORT_DPI, facecolor=self.figure.get_facecolor())
        except (OSError, ValueError) as error:
            messagebox.showerror(
                "Erreur", f"Impossible d'exporter l'image :\n{error}", parent=self._dialog_parent()
            )

    def copy_image(self, *_args: Any) -> None:
        """Copy the figure, as displayed, to the clipboard (Windows only).

        Args:
            *_args: Ignored (Tk event when used as a key binding).
        """
        if not is_image_copy_supported():
            return
        self.figure_canvas.draw()
        rgba = np.asarray(self.figure_canvas.buffer_rgba())
        try:
            copy_image_to_clipboard(rgba)
        except OSError as error:
            messagebox.showerror(
                "Erreur", f"Impossible de copier l'image :\n{error}", parent=self._dialog_parent()
            )

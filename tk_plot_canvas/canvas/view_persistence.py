"""Saving and loading of plot views (JSON files) from the canvas."""

from tkinter import filedialog, messagebox
from typing import Any, Optional

from ..config import FILE_DIALOG_INITIAL_DIR, JSON_EXTENSION, JSON_FILE_TYPES
from ..view import (
    apply_view_parameters,
    capture_view_parameters,
    read_parameters,
    restore_xarray_selection,
    write_parameters,
)

Parameters = dict[str, Any]


class ViewPersistenceMixin:
    """Save the current view to JSON and restore views from JSON.

    Requires the host canvas methods ``_dialog_parent``, ``update_plot``,
    ``_selected_settings_tab`` and ``_reopen_settings_window``.
    """

    def save_parameters(self, *_args: Any) -> None:
        """Ask for a file name and save the current view to it.

        Args:
            *_args: Ignored (Tk event when used as a key binding).
        """
        path = self._ask_save_path()
        if not path:
            return
        parameters = self.get_current_parameters()
        try:
            write_parameters(path, parameters)
        except Exception as error:  # noqa: BLE001 - reported to the user
            messagebox.showerror(
                "Erreur",
                f"Impossible d'enregistrer la vue :\n{error}",
                parent=self._dialog_parent(),
            )

    def _ask_save_path(self) -> Optional[str]:
        """Ask the user where to save the view.

        Returns:
            The chosen path ("" if cancelled), or None when the dialog failed
            (the error is reported to the user).
        """
        try:
            return filedialog.asksaveasfilename(
                parent=self._dialog_parent(),
                initialdir=FILE_DIALOG_INITIAL_DIR,
                title="Enregistrer la vue",
                defaultextension=JSON_EXTENSION,
                filetypes=JSON_FILE_TYPES,
            )
        except Exception as error:  # noqa: BLE001 - reported to the user
            messagebox.showerror(
                "Erreur",
                f"Impossible d'ouvrir la fenêtre d'enregistrement :\n{error}",
                parent=self._dialog_parent(),
            )
            return None

    def get_current_parameters(self) -> Parameters:
        """Return the current view settings in the persisted JSON format.

        Returns:
            The view parameters.
        """
        return capture_view_parameters(self)

    def restore_xarray_selection(self, parameters: Parameters) -> None:
        """Restore the settings that drive the next xarray plots.

        Args:
            parameters: View parameters.
        """
        restore_xarray_selection(self, parameters)

    def load_parameters(
        self,
        *_args: Any,
        path_to_load: Optional[str] = None,
        parameters_to_load: Optional[Parameters] = None,
        reload_plot: bool = False,
    ) -> Optional[Parameters]:
        """Apply a saved view to the plot.

        Args:
            *_args: Ignored (Tk event when used as a key binding).
            path_to_load: JSON file to read; a file dialog is shown when both
                this and ``parameters_to_load`` are None.
            parameters_to_load: Parameters applied directly (no file read).
            reload_plot: Whether to re-plot the xarray datasets first.

        Returns:
            The applied parameters, or None if the file dialog was cancelled.
        """
        parameters = parameters_to_load
        if parameters is None:
            parameters = self._read_view_file(path_to_load)
            if parameters is None:
                return None
            self.restore_xarray_selection(parameters)
        if reload_plot:
            self.update_plot()
        apply_view_parameters(self, parameters)
        self.figure_canvas.draw()
        self._reopen_settings_window(self._selected_settings_tab())
        return parameters

    def _read_view_file(self, path: Optional[str]) -> Optional[Parameters]:
        """Read a view file, asking the user for it when ``path`` is None.

        Args:
            path: JSON file to read.

        Returns:
            The parameters ({} when the file is unreadable), or None when the
            file dialog was cancelled.
        """
        if path is None:
            path = filedialog.askopenfilename(
                parent=self._dialog_parent(),
                initialdir=FILE_DIALOG_INITIAL_DIR,
                title="Charger une vue",
                defaultextension=JSON_EXTENSION,
                filetypes=JSON_FILE_TYPES,
            )
            if not path:
                return None
        try:
            return read_parameters(path)
        except (OSError, ValueError):
            return {}

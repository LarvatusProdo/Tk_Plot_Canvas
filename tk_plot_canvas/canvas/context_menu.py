"""Right-click menu of the figure and keyboard shortcuts.

The menu is rebuilt each time it opens, so that it matches the current plot
(2D curves or surface) and shows which elements are displayed.
"""

import tkinter as tk
from functools import partial
from typing import Any

from ..clipboard import is_image_copy_supported
from ..config import (
    PLOT_TYPE_2D,
    SHORTCUT_COPY_IMAGE,
    SHORTCUT_EXPORT_IMAGE,
    SHORTCUT_LOAD_VIEW,
    SHORTCUT_SAVE_VIEW,
    TAB_3D,
    TAB_AXES,
    TAB_CARTOUCHE,
    TAB_CURVES,
    TAB_LEGEND,
)


def bind_sequences(widget: tk.Misc, sequences: tuple[str, ...], command: Any) -> None:
    """Bind several Tk sequences (e.g. lower and upper case shortcuts) to one command.

    Args:
        widget: Widget receiving the bindings.
        sequences: Tk event sequences.
        command: Callback receiving the Tk event.
    """
    for sequence in sequences:
        widget.bind(sequence, command)


class ContextMenuMixin:
    """Build the context menu and bind the keyboard shortcuts.

    Requires the host canvas attributes and methods used by the menu
    entries: ``figure_canvas``, ``toolbar``, ``plot_type``, ``colorbar``,
    ``lines``, ``line_labels``, ``show_legend``, ``show_cartouche``,
    ``save_parameters``, ``load_parameters``, ``export_image``,
    ``copy_image``, ``open_settings_window`` and the visibility setters.
    """

    def _build_context_menu(self) -> None:
        """Create the right-click menu and the keyboard shortcuts of the figure."""
        self.context_menu = tk.Menu(self, tearoff=0)
        widget = self.figure_canvas.get_tk_widget()
        widget.bind("<Button-3>", self._show_context_menu)
        self.bind_view_shortcuts(widget)
        bind_sequences(widget, SHORTCUT_EXPORT_IMAGE, self.export_image)
        if is_image_copy_supported():
            bind_sequences(widget, SHORTCUT_COPY_IMAGE, self.copy_image)

    def bind_view_shortcuts(self, widget: tk.Misc) -> None:
        """Bind Ctrl+S (save the view) and Ctrl+O (load a view) on a widget.

        Args:
            widget: Figure widget or settings window.
        """
        bind_sequences(widget, SHORTCUT_SAVE_VIEW, self.save_parameters)
        bind_sequences(widget, SHORTCUT_LOAD_VIEW, self.load_view_file)

    def load_view_file(self, *_args: Any) -> None:
        """Ask for a view file and apply it, re-plotting the xarray datasets if any.

        Args:
            *_args: Ignored (Tk event when used as a key binding).
        """
        self.load_parameters(reload_plot=bool(self.datasets))

    def _show_context_menu(self, event: tk.Event) -> None:
        """Rebuild the context menu for the current plot and show it at the mouse.

        Args:
            event: Tk mouse event.
        """
        menu = self.context_menu
        menu.delete(0, tk.END)
        self._add_view_entries(menu)
        menu.add_separator()
        self._add_settings_entries(menu)
        menu.add_separator()
        self._add_display_entries(menu)
        menu.add_separator()
        self._add_image_entries(menu)
        menu.tk_popup(event.x_root, event.y_root)

    def _add_view_entries(self, menu: tk.Menu) -> None:
        """Add the "save / load view" entries.

        Args:
            menu: Menu being built.
        """
        menu.add_command(
            label="Enregistrer la vue…", command=self.save_parameters, accelerator="Ctrl+S"
        )
        menu.add_command(
            label="Charger une vue…", command=self.load_view_file, accelerator="Ctrl+O"
        )

    def _add_settings_entries(self, menu: tk.Menu) -> None:
        """Add one entry per tab of the settings window.

        Args:
            menu: Menu being built.
        """
        tabs = [TAB_AXES]
        tabs += [TAB_CURVES, TAB_LEGEND] if self.plot_type == PLOT_TYPE_2D else [TAB_3D]
        tabs.append(TAB_CARTOUCHE)
        for tab_name in tabs:
            menu.add_command(
                label=f"{tab_name}…", command=partial(self.open_settings_window, tab_name)
            )

    def _add_display_entries(self, menu: tk.Menu) -> None:
        """Add the check entries showing or hiding the legend, colorbar and cartouche.

        Args:
            menu: Menu being built.
        """
        if self.plot_type == PLOT_TYPE_2D:
            has_labels = any(self.line_labels)
            self._add_check_entry(
                menu, "Afficher la légende", self.show_legend, self.set_legend_visible, has_labels
            )
        elif self.lines:
            has_colorbar = self.colorbar is not None
            self._add_check_entry(
                menu, "Afficher la colorbar", has_colorbar, self.set_colorbar_visible, True
            )
        self._add_check_entry(
            menu, "Afficher le cartouche", self.show_cartouche, self.set_cartouche_visible, True
        )

    def _add_check_entry(
        self, menu: tk.Menu, label: str, is_on: bool, command: Any, enabled: bool
    ) -> None:
        """Add a check entry calling ``command`` with its new state.

        Args:
            menu: Menu being built.
            label: Entry text.
            is_on: Current state.
            command: Called with the new state (bool).
            enabled: Whether the entry can be used.
        """
        variable = tk.BooleanVar(master=menu, value=is_on)
        menu.add_checkbutton(
            label=label,
            variable=variable,
            command=lambda: self._after_display_toggle(command, variable.get()),
            state=tk.NORMAL if enabled else tk.DISABLED,
        )

    def _after_display_toggle(self, command: Any, visible: bool) -> None:
        """Apply a display toggle, then refresh the settings window if it is open.

        Args:
            command: Visibility setter.
            visible: New state.
        """
        command(visible)
        self._reopen_settings_window(self._selected_settings_tab())

    def _add_image_entries(self, menu: tk.Menu) -> None:
        """Add the zoom reset, image copy and image export entries.

        Args:
            menu: Menu being built.
        """
        menu.add_command(label="Réinitialiser le zoom", command=self.toolbar.home)
        if is_image_copy_supported():
            menu.add_command(label="Copier l'image", command=self.copy_image, accelerator="Ctrl+C")
        menu.add_command(
            label="Exporter l'image…", command=self.export_image, accelerator="Ctrl+E"
        )

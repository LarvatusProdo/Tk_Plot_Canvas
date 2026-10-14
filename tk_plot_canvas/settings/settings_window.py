"""Settings window: a notebook with one tab per group of plot settings."""

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Optional

from ..config import (
    PLOT_TYPE_2D,
    PLOT_TYPE_3D,
    SETTINGS_WINDOW_OFFSET,
    SETTINGS_WINDOW_SIZE,
    STYLE_BUTTON,
    STYLE_FRAME,
    STYLE_NOTEBOOK,
    TAB_3D,
    TAB_AXES,
    TAB_CARTOUCHE,
    TAB_CURVES,
    TAB_LEGEND,
)
from .axes_tab import AxesTab
from .base_tab import SettingsTab
from .cartouche_tab import CartoucheTab
from .curves_tab import CurvesTab
from .legend_tab import LegendTab
from .surface_tab import SurfaceTab
from .window_placement import place_window, setup_secondary_window

if TYPE_CHECKING:
    from ..canvas.plot_canvas import TkPlotCanvas


class SettingsWindow(tk.Toplevel):
    """Window editing axes, cartouche, curves, legend and 3D settings.

    Attributes:
        canvas: The plot canvas being edited.
        notebook: Notebook holding the tabs.
        tabs: Tabs indexed by their title.
    """

    def __init__(
        self, canvas: "TkPlotCanvas", initial_tab: str = "", geometry: Optional[str] = None
    ) -> None:
        """Create the window and its tabs.

        Args:
            canvas: The plot canvas to edit.
            initial_tab: Title of the tab selected on opening.
            geometry: Tk geometry to reuse (e.g. of a replaced window); by
                default the window is placed next to the main window.
        """
        super().__init__(canvas)
        self.canvas = canvas
        self.title("Réglages du graphique")
        self._place(geometry)
        self._build_buttons()
        self.notebook = ttk.Notebook(self, style=STYLE_NOTEBOOK)
        self.notebook.pack(side="bottom", fill="both", expand=True)
        self.tabs: dict[str, SettingsTab] = {}
        self._build_tabs()
        self.select_tab(initial_tab)

    def _place(self, geometry: Optional[str]) -> None:
        """Size and place the window, keep it above the main window, close it with Escape.

        Args:
            geometry: Tk geometry to reuse, or None to place it next to the main window.
        """
        if geometry:
            self.geometry(geometry)
        else:
            place_window(self, self.canvas.master, SETTINGS_WINDOW_SIZE, SETTINGS_WINDOW_OFFSET)
        setup_secondary_window(self, self.canvas)
        self.canvas.bind_view_shortcuts(self)

    def _build_buttons(self) -> None:
        """Create the "save" and "load" view buttons."""
        buttons_frame = ttk.Frame(self, style=STYLE_FRAME)
        buttons_frame.pack(side="top", fill="x")
        ttk.Button(
            buttons_frame,
            text="Enregistrer la vue…",
            command=self.canvas.save_parameters,
            style=STYLE_BUTTON,
        ).pack(side="right", pady=5, padx=10)
        ttk.Button(
            buttons_frame,
            text="Charger une vue…",
            command=self.canvas.load_view_file,
            style=STYLE_BUTTON,
        ).pack(side="right", pady=5, padx=10)

    def _build_tabs(self) -> None:
        """Create the tabs matching the current plot type."""
        self.tabs[TAB_AXES] = AxesTab(self, TAB_AXES)
        self.tabs[TAB_CARTOUCHE] = CartoucheTab(self, TAB_CARTOUCHE)
        if self.canvas.plot_type == PLOT_TYPE_2D:
            self.tabs[TAB_CURVES] = CurvesTab(self, TAB_CURVES)
            self.tabs[TAB_LEGEND] = LegendTab(self, TAB_LEGEND)
        elif self.canvas.plot_type == PLOT_TYPE_3D:
            self.tabs[TAB_3D] = SurfaceTab(self, TAB_3D)

    def select_tab(self, tab_name: str) -> None:
        """Select a tab by title (unknown titles are ignored).

        Args:
            tab_name: Tab title.
        """
        tab: Optional[SettingsTab] = self.tabs.get(tab_name)
        if tab is not None:
            self.notebook.select(tab.frame)

    def selected_tab_name(self) -> str:
        """Return the title of the selected tab.

        Returns:
            The selected tab title.
        """
        return self.notebook.tab(self.notebook.select(), "text")

    def title_text(self) -> str:
        """Return the plot title typed in the "Axes et titre" tab.

        Returns:
            The title entry content.
        """
        return self.tabs[TAB_AXES].title_var.get()

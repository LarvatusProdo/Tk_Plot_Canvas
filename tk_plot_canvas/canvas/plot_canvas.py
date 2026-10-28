"""TkPlotCanvas: a Tkinter frame embedding a customizable Matplotlib figure.

The frame contains the figure (with the Matplotlib toolbar) and, below it,
a resizable "cartouche" listing the metadata of every curve. A right click on
the figure opens a context menu (views, settings tabs, display toggles, image
export); a double click edits a text in place or opens the matching settings tab.
"""

import os
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from typing import Any, Optional, Union

import matplotlib
from matplotlib import font_manager
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from ..config import (
    CARTOUCHE_HEIGHT,
    CLASS_MODE_AUTO,
    COLORBAR_STYLE_DEFAULT,
    DEFAULT_BACKGROUND_COLOR,
    DEFAULT_DPI,
    DEFAULT_FIGSIZE,
    DEFAULT_SURFACE_KIND,
    MATPLOTLIB_BACKEND,
    PLOT_TYPE_2D,
    STYLE_CARTOUCHE_FRAME,
    STYLE_FRAME,
    SURFACE_AXES_STYLE_DEFAULT,
    SURFACE_SIZE_DEFAULTS,
)
from ..fonts import default_font_name
from ..settings import DialogManager, SettingsWindow
from ..settings.dialog_manager import is_window_open
from ..widgets import VerticalScrolledFrame
from .cartouche import CartoucheMixin
from .colorbar import ColorbarMixin
from .context_menu import ContextMenuMixin
from .double_click import DoubleClickMixin
from .figure_export import FigureExportMixin
from .legend import LegendMixin
from .plot_helpers import PlotHelpersMixin
from .standard_plotting import StandardPlotMixin
from .styles import configure_canvas_styles
from .surface_axes import SurfaceAxesMixin
from .surface_redraw import SurfaceRedrawMixin
from .view_persistence import ViewPersistenceMixin
from .xarray_curves import XarrayCurvePlotMixin
from .xarray_surfaces import XarraySurfacePlotMixin


class TkPlotCanvas(
    ttk.Frame,
    StandardPlotMixin,
    XarrayCurvePlotMixin,
    XarraySurfacePlotMixin,
    PlotHelpersMixin,
    LegendMixin,
    CartoucheMixin,
    ColorbarMixin,
    SurfaceRedrawMixin,
    SurfaceAxesMixin,
    ViewPersistenceMixin,
    ContextMenuMixin,
    DoubleClickMixin,
    FigureExportMixin,
):
    """A Tkinter frame that embeds a Matplotlib figure.

    Attributes:
        figure: The Matplotlib figure.
        axes: The Matplotlib axes used for plotting.
        figure_canvas: The Tk widget wrapper of the figure.
        lines: Plotted artists (``Line2D`` or contour sets).
        line_labels: Metadata dictionary of each plotted artist.
        datasets: xarray datasets plotted with :meth:`plot_xarray`.
        view_parameters: Parameters of the loaded view ({} if none).
        settings_window: The open settings window, if any.
    """

    def __init__(
        self,
        master: Optional[tk.Misc] = None,
        dpi: int = DEFAULT_DPI,
        figsize: tuple[float, float] = DEFAULT_FIGSIZE,
        bg_color: str = DEFAULT_BACKGROUND_COLOR,
        load_view: Optional[Union[str, "os.PathLike[str]"]] = None,
        **kwargs: Any,
    ) -> None:
        """Create the canvas.

        Args:
            master: Parent widget (its window is resized by loaded views).
            dpi: Dots per inch of the Matplotlib figure.
            figsize: Figure size in inches (width, height).
            bg_color: Background color of the plot.
            load_view: JSON file of a previously saved view to apply.
            **kwargs: Passed to ``ttk.Frame``.
        """
        super().__init__(master, **kwargs)
        self._setup_styles(bg_color)
        self._init_state()
        self._build_layout()
        self._build_figure(figsize, dpi, bg_color)
        self._build_context_menu()
        self._connect_double_click()
        self._load_initial_view(load_view)

    def _setup_styles(self, background_color: str) -> None:
        """Configure ttk styles and collect the available fonts.

        Args:
            background_color: Background color of the plot and cartouche.
        """
        self.style = ttk.Style()
        self.graph_background_color = background_color
        frame_background = self.style.lookup("TFrame", "background")
        self.default_font = default_font_name()
        self.matplotlib_fonts = sorted(set(font_manager.FontManager().get_font_names()))
        self.tkinter_fonts = list(tkfont.families())
        configure_canvas_styles(self.style, self.default_font, background_color, frame_background)

    def _init_state(self) -> None:
        """Initialize the plot state shared with the settings window."""
        self.title_var = tk.StringVar(value="")
        self.xlabel_var = tk.StringVar(value="")
        self.ylabel_var = tk.StringVar(value="")
        self.legend_keys: list[str] = []
        self.cartouche_keys: list[str] = []
        self.show_legend = False
        self.show_legend_key_names = False
        self.show_cartouche = True
        self.show_map = True
        self.is_date_on_x_axis = False
        self.is_date_on_y_axis = False
        self.plot_type = PLOT_TYPE_2D
        self.contour_class_mode = CLASS_MODE_AUTO
        self.contour_value_range: Optional[tuple[float, float]] = None
        self.surface_kind = DEFAULT_SURFACE_KIND
        self.surface_sizes: dict[str, float] = dict(SURFACE_SIZE_DEFAULTS)
        self.colorbar: Optional[Any] = None
        self.colorbar_style: dict[str, Any] = dict(COLORBAR_STYLE_DEFAULT)
        self.hidden_colorbar_label: Optional[tuple[str, dict[str, Any]]] = None
        self.surface_axes_style: dict[str, Any] = dict(SURFACE_AXES_STYLE_DEFAULT)
        self.lines: list[Any] = []
        self.line_labels: list[Optional[dict]] = []
        self.xarray_variables = {"x": "", "y": "", "z": ""}
        self.datasets: list[Any] = []
        self.view_parameters: dict[str, Any] = {}
        self.settings_window: Optional[SettingsWindow] = None
        self.dialogs = DialogManager()

    def _build_layout(self) -> None:
        """Create the resizable plot area and cartouche area."""
        self.panedwindow = ttk.Panedwindow(self, orient=tk.VERTICAL)
        self.panedwindow.pack(fill=tk.BOTH, expand=True)
        self.plot_frame = ttk.Frame(self.panedwindow, style=STYLE_FRAME)
        self.panedwindow.add(self.plot_frame, weight=1)
        self.cartouche_frame = VerticalScrolledFrame(
            self.panedwindow,
            x_bar=True,
            bg_canvas="",
            height_canvas=CARTOUCHE_HEIGHT,
            style_frame=STYLE_CARTOUCHE_FRAME,
        )
        self.panedwindow.add(self.cartouche_frame, weight=0)
        self.cartouche_initialized = False
        self.cartouche_rows: list[list[Any]] = []
        self.cartouche_headers: list[ttk.Label] = []

    def _build_figure(self, figsize: tuple[float, float], dpi: int, background_color: str) -> None:
        """Create the Matplotlib figure, its Tk canvas and its toolbar.

        Args:
            figsize: Figure size in inches.
            dpi: Dots per inch.
            background_color: Figure and axes background color.
        """
        matplotlib.use(MATPLOTLIB_BACKEND)
        self.figure = Figure(figsize=figsize, dpi=dpi)
        self.figure.set_facecolor(background_color)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_facecolor(background_color)
        self.figure_canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.figure_canvas.draw()
        self.toolbar = NavigationToolbar2Tk(
            self.figure_canvas, self.plot_frame, pack_toolbar=False
        )
        self.toolbar.update()
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.figure_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _load_initial_view(self, load_view: Optional[Union[str, "os.PathLike[str]"]]) -> None:
        """Apply the view file given to the constructor, if it exists.

        Args:
            load_view: Path of the view file, or None.
        """
        if load_view is not None and os.path.isfile(load_view):
            self.view_parameters = self.load_parameters(path_to_load=load_view)
            self.restore_xarray_selection(self.view_parameters)
        else:
            self.view_parameters = {}

    def open_settings_window(self, tab_name: str = "") -> None:
        """Open the settings window, replacing any previous one at the same place.

        Args:
            tab_name: Title of the tab to select (e.g. "Axes et titre").
        """
        geometry = None
        if self._is_settings_window_open():
            # A window not yet mapped reports a "1x1" size: map it before reading it.
            self.settings_window.update_idletasks()
            geometry = self.settings_window.geometry()
            self.settings_window.destroy()
        self.settings_window = SettingsWindow(self, initial_tab=tab_name, geometry=geometry)

    def _is_settings_window_open(self) -> bool:
        """Tell whether the settings window is currently displayed.

        Returns:
            True when the window exists and has not been closed.
        """
        window = self.settings_window
        return window is not None and is_window_open(window)

    def _dialog_parent(self) -> tk.Misc:
        """Return the widget file dialogs should be attached to.

        Returns:
            The settings window when open, otherwise the canvas.
        """
        return self.settings_window if self._is_settings_window_open() else self

    def _selected_settings_tab(self) -> str:
        """Return the title of the tab selected in the settings window.

        Returns:
            The tab title, or "" when the window is not open.
        """
        if not self._is_settings_window_open():
            return ""
        return self.settings_window.selected_tab_name()

    def _reopen_settings_window(self, tab_name: str) -> None:
        """Rebuild the settings window so it reflects the current plot.

        Args:
            tab_name: Tab to select; nothing happens when empty.
        """
        if tab_name != "":
            self.open_settings_window(tab_name)

    def update_plot(self, **kwargs: Any) -> None:
        """Clear the figure and re-plot every registered xarray dataset.

        Args:
            **kwargs: Passed to :meth:`plot_xarray`.
        """
        self.clear_plot()
        title = None
        if self._is_settings_window_open():
            title = self.settings_window.title_text()
        tab_name = self._selected_settings_tab()
        for index, dataset in enumerate(self.datasets):
            self.plot_xarray(
                dataset,
                clear=False,
                replot=True,
                label=self.line_labels[index],
                title=title if index == 0 else None,
                legend=True,
                **kwargs,
            )
        self._reopen_settings_window(tab_name)

    def clear_plot(self) -> None:
        """Remove every plot and the colorbar, then redraw."""
        self.remove_colorbar()
        self.axes.cla()
        self.lines.clear()
        self.figure_canvas.draw()

"""Base class of the tabs of the settings window."""

from typing import TYPE_CHECKING

from ..config import NOTEBOOK_PADDING, STYLE_FRAME
from ..widgets import VerticalScrolledFrame

if TYPE_CHECKING:
    from ..canvas.plot_canvas import TkPlotCanvas
    from .settings_window import SettingsWindow


class SettingsTab:
    """A scrollable notebook tab bound to a plot canvas.

    Attributes:
        window: The settings window owning the tab.
        canvas: The plot canvas being edited.
        frame: Scrollable frame receiving the tab widgets.
    """

    def __init__(self, window: "SettingsWindow", title: str) -> None:
        """Create the tab, add it to the window notebook and fill it.

        Args:
            window: The settings window.
            title: Tab title.
        """
        self.window = window
        self.canvas: "TkPlotCanvas" = window.canvas
        self.frame = VerticalScrolledFrame(window.notebook, x_bar=True, style_frame=STYLE_FRAME)
        window.notebook.add(self.frame, text=title, padding=NOTEBOOK_PADDING)
        self.build()

    def build(self) -> None:
        """Create the widgets of the tab.

        Raises:
            NotImplementedError: Always; subclasses must implement it.
        """
        raise NotImplementedError

    def redraw(self) -> None:
        """Redraw the Matplotlib figure of the canvas."""
        self.canvas.figure_canvas.draw()

    def redraw_idle(self) -> None:
        """Redraw the figure once Tk is idle (cheap enough to call while typing)."""
        self.canvas.figure_canvas.draw_idle()

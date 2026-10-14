"""TkPlotCanvas: Matplotlib figures embedded in Tkinter, with interactive settings.

Example:
    >>> import tkinter as tk
    >>> from tk_plot_canvas import TkPlotCanvas
    >>> root = tk.Tk()
    >>> canvas = TkPlotCanvas(root)
    >>> canvas.pack(fill="both", expand=True)
    >>> canvas.plot([0, 1, 2], [0, 1, 4], label={"curve": "square"})
"""

from .dpi import enable_high_dpi

# Before any Tk window exists, so that the application is sharp on scaled screens.
enable_high_dpi()

from .canvas.plot_canvas import TkPlotCanvas  # noqa: E402
from .widgets import ClassSelectionFrame, VerticalScrolledFrame  # noqa: E402

__all__ = ["ClassSelectionFrame", "TkPlotCanvas", "VerticalScrolledFrame", "enable_high_dpi"]

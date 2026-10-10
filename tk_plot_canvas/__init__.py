"""TkPlotCanvas: Matplotlib figures embedded in Tkinter, with interactive settings.

Example:
    >>> import tkinter as tk
    >>> from tk_plot_canvas import TkPlotCanvas
    >>> root = tk.Tk()
    >>> canvas = TkPlotCanvas(root)
    >>> canvas.pack(fill="both", expand=True)
    >>> canvas.plot([0, 1, 2], [0, 1, 4], label={"curve": "square"})
"""

from .canvas.plot_canvas import TkPlotCanvas
from .widgets import ClassSelectionFrame, VerticalScrolledFrame

__all__ = ["ClassSelectionFrame", "TkPlotCanvas", "VerticalScrolledFrame"]

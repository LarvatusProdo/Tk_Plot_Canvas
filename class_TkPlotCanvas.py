"""Backward-compatible import path for existing scripts.

``from class_TkPlotCanvas import TkPlotCanvas`` keeps working; new code
should use ``from tk_plot_canvas import TkPlotCanvas``.
"""

from tk_plot_canvas import TkPlotCanvas

__all__ = ["TkPlotCanvas"]

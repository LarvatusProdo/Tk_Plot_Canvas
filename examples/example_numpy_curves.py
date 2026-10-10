"""Example: plot NumPy arrays with TkPlotCanvas.

Run from the project root::

    python -m examples.example_numpy_curves
"""

import tkinter as tk

import numpy as np

from tk_plot_canvas import TkPlotCanvas

POINT_COUNT = 100
X_MAX = 10


def main() -> None:
    """Plot a sine and a cosine wave in the same canvas."""
    root = tk.Tk()
    plot_canvas = TkPlotCanvas(root)
    plot_canvas.pack(fill=tk.BOTH, expand=True)
    x_values = np.linspace(0, X_MAX, POINT_COUNT)
    plot_canvas.plot(x_values, np.sin(x_values), label={"curve": "Sine wave", "comment": ""})
    plot_canvas.plot(
        x_values, np.cos(x_values), label={"curve": "Cosine wave", "comment": ""}, clear=False
    )
    root.mainloop()


if __name__ == "__main__":
    main()

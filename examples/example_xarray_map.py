"""Example: plot a two-dimensional xarray dataset as a map with a saved view.

Coastlines and borders are drawn when cartopy is installed. Run from the
project root::

    python -m examples.example_xarray_map
"""

import tkinter as tk

import xarray as xr

from examples.config import MAP_FILE, MAP_VIEW
from tk_plot_canvas import TkPlotCanvas

TEST_VARIABLE_SCALE = 10
TEST_VARIABLE_OFFSET = 10


def main() -> None:
    """Plot the 2024 2 m temperature map, plus a derived test variable."""
    root = tk.Tk()
    plot_canvas = TkPlotCanvas(root, load_view=MAP_VIEW)
    plot_canvas.pack(fill=tk.BOTH, expand=True)
    temperature = xr.open_dataset(MAP_FILE)
    temperature["temperature_test"] = (
        temperature["temperature"] * TEST_VARIABLE_SCALE + TEST_VARIABLE_OFFSET
    )
    plot_canvas.plot_xarray(temperature, clear=False, label=temperature.attrs, legend=True)
    root.mainloop()


if __name__ == "__main__":
    main()

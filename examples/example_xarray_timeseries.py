"""Example: plot a one-dimensional xarray dataset (time series) with a saved view.

Run from the project root::

    python -m examples.example_xarray_timeseries
"""

import tkinter as tk

import xarray as xr

from examples.config import TIME_SERIES_FILE, TIME_SERIES_VIEW
from tk_plot_canvas import TkPlotCanvas

METADATA = dict(
    description="Weather data", base="", source="", history="", references="1", comment=""
)


def main() -> None:
    """Plot the 2024 mean 2 m temperature time series."""
    root = tk.Tk()
    plot_canvas = TkPlotCanvas(root, load_view=TIME_SERIES_VIEW)
    plot_canvas.pack(fill=tk.BOTH, expand=True)
    temperature = xr.open_dataset(TIME_SERIES_FILE)
    plot_canvas.plot_xarray(
        temperature, clear=False, title="Temperature 2m", label=dict(METADATA), legend=True
    )
    root.mainloop()


if __name__ == "__main__":
    main()

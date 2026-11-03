"""Example: browse a three-dimensional xarray variable (monthly maps) with the slice players.

The variable ``t2m`` has the dimensions ``(valid_time, latitude, longitude)``:
the map shows the first month, and the "Autres dimensions" frame of the
"Axes et titre" settings tab (right click on the figure) steps through the
months. Run from the project root::

    python -m examples.example_xarray_slices
"""

import tkinter as tk

import xarray as xr

from examples.config import MAP_VIEW, MONTHLY_MAPS_FILE
from tk_plot_canvas import TkPlotCanvas

# One grid node out of GRID_STEP along each axis, so that playing stays smooth.
GRID_STEP = 4


def main() -> None:
    """Plot the 2024 monthly 2 m temperature maps and open the slice players."""
    root = tk.Tk()
    plot_canvas = TkPlotCanvas(root, load_view=MAP_VIEW)
    plot_canvas.pack(fill=tk.BOTH, expand=True)
    temperature = xr.open_dataset(MONTHLY_MAPS_FILE).isel(
        latitude=slice(None, None, GRID_STEP), longitude=slice(None, None, GRID_STEP)
    )
    plot_canvas.plot_xarray(temperature, clear=False, label=temperature.attrs)
    plot_canvas.open_settings_window("Axes et titre")
    root.mainloop()


if __name__ == "__main__":
    main()

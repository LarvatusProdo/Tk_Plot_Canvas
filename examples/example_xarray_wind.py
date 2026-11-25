"""Example: wind speed map with the wind direction drawn as arrows.

A synthetic dataset with the dimensions ``(time, latitude, longitude)`` holds
``vent_u`` (eastward), ``vent_v`` (northward) and ``norme_vent``. The surface
shows ``norme_vent`` (variable chosen in the "Surface" tab, right click on the
figure); the arrows are shown with the "Champ de vecteurs (flèches)" checkbutton
of the same tab, set in the "Vecteurs" tab, and follow the time chosen in the
"Axes et titre" tab. Run from the project root::

    python -m examples.example_xarray_wind
"""

import tkinter as tk

import numpy as np
import pandas as pd
import xarray as xr

from tk_plot_canvas import TkPlotCanvas

LONGITUDES = np.arange(-10.0, 10.25, 0.5)
LATITUDES = np.arange(40.0, 55.25, 0.5)
TIME_COUNT = 24
WIND_UNITS = "m s-1"
VORTEX_SPEED = 15.0
VORTEX_RADIUS = 4.0
VORTEX_DRIFT = 0.4


def build_wind_dataset() -> xr.Dataset:
    """Build a vortex drifting eastward over France, hour by hour.

    Returns:
        Dataset with ``vent_u``, ``vent_v`` and ``norme_vent`` on
        ``(time, latitude, longitude)``.
    """
    times = pd.date_range("2024-01-01", periods=TIME_COUNT, freq="h")
    hours = np.arange(TIME_COUNT)[:, None, None]
    latitude = LATITUDES[None, :, None]
    longitude = LONGITUDES[None, None, :]
    east = longitude - (-5.0 + VORTEX_DRIFT * hours)
    north = latitude - 47.5
    radius = np.hypot(east, north)
    speed = VORTEX_SPEED * (radius / VORTEX_RADIUS) * np.exp(1 - radius / VORTEX_RADIUS)
    angle = np.arctan2(north, east)
    dimensions = ("time", "latitude", "longitude")
    dataset = xr.Dataset(
        {
            "vent_u": (dimensions, -speed * np.sin(angle)),
            "vent_v": (dimensions, speed * np.cos(angle)),
        },
        coords={"time": times, "latitude": LATITUDES, "longitude": LONGITUDES},
        attrs={"source": "Exemple synthétique", "variable": "Vent à 10 m"},
    )
    dataset["norme_vent"] = np.hypot(dataset["vent_u"], dataset["vent_v"])
    for name in dataset.data_vars:
        dataset[name].attrs["units"] = WIND_UNITS
    return dataset


def main() -> None:
    """Plot the wind speed with arrows and open the "Vecteurs" settings tab."""
    root = tk.Tk()
    plot_canvas = TkPlotCanvas(root)
    plot_canvas.pack(fill=tk.BOTH, expand=True)
    wind = build_wind_dataset()
    plot_canvas.xarray_variables["z"] = "norme_vent"
    plot_canvas.vector_field.update(enabled=True, u="vent_u", v="vent_v")
    plot_canvas.plot_xarray(wind, clear=False, label=wind.attrs)
    plot_canvas.open_settings_window("Vecteurs")
    root.mainloop()


if __name__ == "__main__":
    main()

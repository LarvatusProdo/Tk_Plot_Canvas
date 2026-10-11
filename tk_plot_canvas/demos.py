"""Interactive demonstrations of the package widgets.

Each function opens a Tk window and blocks until it is closed.
"""

import tkinter as tk
from typing import Optional

import numpy as np
import xarray as xr

from .canvas.plot_canvas import TkPlotCanvas
from .config import CLASS_MODE_AUTO, DEMO_WINDOW_TITLE, DEMO_XARRAY_VIEW
from .widgets import ClassSelectionFrame, VerticalScrolledFrame

MONTH_COUNT = 12
POINT_COUNT = 11


def _weather_attributes(reference: str, comment: str, **extra: str) -> dict[str, str]:
    """Build the metadata of a demo dataset.

    Args:
        reference: Value of the "references" attribute.
        comment: Value of the "comment" attribute.
        **extra: Additional attributes, inserted after "description".

    Returns:
        The dataset attributes.
    """
    attributes = {"description": "Weather data", **extra}
    attributes.update(base="", source="Simulated", history="Created for demo")
    attributes.update(references=reference, comment=comment)
    return attributes


def _power_dataset(exponent: float, reference: str, comment: str) -> xr.Dataset:
    """Build a dataset where temperature = time ** exponent.

    Args:
        exponent: Power applied to the time values.
        reference: Value of the "references" attribute.
        comment: Value of the "comment" attribute.

    Returns:
        The dataset.
    """
    times = list(range(POINT_COUNT))
    return xr.Dataset(
        data_vars=dict(temperature=("time", [time**exponent for time in times])),
        coords=dict(time=times),
        attrs=_weather_attributes(reference, comment, units="°C"),
    )


def _create_demo_canvas(load_view: Optional[str] = None) -> tuple[tk.Tk, TkPlotCanvas]:
    """Create the demo main window and its plot canvas.

    Args:
        load_view: View file applied to the canvas, if any.

    Returns:
        ``(root, canvas)``.
    """
    root = tk.Tk()
    root.title(DEMO_WINDOW_TITLE)
    plot_widget = TkPlotCanvas(root, load_view=load_view)
    plot_widget.pack(fill="both", expand=True)
    return root, plot_widget


def demo_standard() -> None:
    """Plot two curves with :meth:`TkPlotCanvas.plot`."""
    root, plot_widget = _create_demo_canvas()
    first = _power_dataset(2, "1", "First curve")
    texts = dict(title=first.attrs["description"], xlabel="time", ylabel="Temperature")
    plot_widget.plot(first["time"], first["temperature"], label=first.attrs, legend=True, **texts)
    second = _power_dataset(1.5, "2", "Second curve")
    style = dict(clear=False, color="black")
    plot_widget.plot(
        second["time"], second["temperature"], label=second.attrs, legend=True, **style
    )
    root.mainloop()


def _monthly_dataset(
    temperature: list[float], humidity: list[float], reference: str, comment: str
) -> xr.Dataset:
    """Build a monthly demo dataset with two variables.

    Args:
        temperature: Temperature values.
        humidity: Humidity values.
        reference: Value of the "references" attribute.
        comment: Value of the "comment" attribute.

    Returns:
        The dataset.
    """
    months = [
        np.datetime64("2024-01") + np.timedelta64(month, "M") for month in range(MONTH_COUNT)
    ]
    return xr.Dataset(
        data_vars={
            "temperature": (("time"), temperature, {"units": "°C"}),
            "humidity": (("time"), humidity, {"units": "%"}),
        },
        coords=dict(time=months),
        attrs=_weather_attributes(reference, comment),
    )


def demo_xarray() -> None:
    """Plot three monthly xarray datasets with :meth:`TkPlotCanvas.plot_xarray`."""
    root, plot_widget = _create_demo_canvas(load_view=DEMO_XARRAY_VIEW)
    months = range(MONTH_COUNT)
    first = _monthly_dataset([i**2 for i in months], list(months), "1", "First curve")
    second = _monthly_dataset(
        [i**1.5 for i in months], [i * 10 for i in months], "2", "Second curve"
    )
    third = _monthly_dataset(list(months), [1] * MONTH_COUNT, "3", "Second curve")
    plot_widget.plot_xarray(
        first, clear=False, title=first.attrs["description"], label=first.attrs, legend=True
    )
    plot_widget.plot_xarray(second, clear=False, label=second.attrs, legend=True)
    plot_widget.plot_xarray(third, clear=False, label=second.attrs, legend=True)
    root.mainloop()


def demo_class_selection() -> None:
    """Show the contour class selection frame."""
    root = tk.Tk()
    root.title("Test choix_class")
    frame = ClassSelectionFrame(
        root,
        with_buttons=True,
        classes=[0, 10, 20, 30],
        type_class=CLASS_MODE_AUTO,
        nb_classes=5,
        v_min=0.0,
        v_max=30.0,
    )
    frame.pack(fill="both", expand=True)
    root.mainloop()


def demo_scrolled_frame() -> None:
    """Show a scrollable frame filled with labels and entries."""
    root = tk.Tk()
    root.title("Scrollbar Test")
    root.geometry("400x500")
    frame = VerticalScrolledFrame(root, width=300, borderwidth=2, relief=tk.SUNKEN, x_bar=True)
    frame.pack(fill=tk.BOTH, expand=True)
    for row in range(30):
        tk.Label(frame, text=f"This is a label {row}").grid(column=1, row=row, sticky=tk.W)
        tk.Entry(frame, textvariable="text").grid(column=2, row=row, sticky=tk.W)
    root.mainloop()


DEMOS = {
    "standard": demo_standard,
    "xarray": demo_xarray,
    "class-selection": demo_class_selection,
    "scrolled-frame": demo_scrolled_frame,
}

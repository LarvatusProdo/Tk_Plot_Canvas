import os
import sys
import tkinter as tk
import xarray as xr

from class_TkPlotCanvas import TkPlotCanvas

"""
This script is used to test the plotting of xarray datasets using the TkPlotCanvas class.

command : python -m "Scripts de test.test_carte"
"""

root = tk.Tk()
plot_canvas = TkPlotCanvas(root, load_view="Exemples de vues json/vue_xarray_3D.json")
plot_canvas.pack(fill=tk.BOTH, expand=True)

current_path =  os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/"

ds_temperature = xr.open_dataset(current_path + "2024_temperature_2m_carte.nc")
ds_temperature["temperature_test"] = ds_temperature["temperature"] * 10 + 10
plot_canvas.plot_xarray(ds_temperature, clear=False, label= ds_temperature.attrs, legend=True)

root.mainloop()
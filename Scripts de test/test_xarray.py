import tkinter as tk
import os
import xarray as xr

from class_TkPlotCanvas import TkPlotCanvas

"""
This script is used to test the plotting of xarray datasets using the TkPlotCanvas class.

command : python -m "Scripts de test.test_xarray"
"""

root = tk.Tk()
plot_canvas = TkPlotCanvas(root,  load_view="Exemples de vues json/vue_xarray.json")
plot_canvas.pack(fill=tk.BOTH, expand=True)

current_path =  os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/"

ds_temperature = xr.open_dataset(current_path + "2024_temperature_2m_temporel.nc")

plot_canvas.plot_xarray(ds_temperature, clear=False, title="Temperature 2m", label= dict(description="Weather data", base="", source="", history="", references="1", comment="") , legend=True)


root.mainloop()
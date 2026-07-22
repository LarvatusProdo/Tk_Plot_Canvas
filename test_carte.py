from class_TkPlotCanvas import TkPlotCanvas
import tkinter as tk
import os
import xarray as xr

root = tk.Tk()
plot_canvas = TkPlotCanvas(root)
plot_canvas.pack(fill=tk.BOTH, expand=True)

current_path =  os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"

ds_temperature = xr.open_dataset(current_path + "2024_temperature_2m_carte.nc")

plot_canvas.plot_xarray(ds_temperature, clear=False, label= ds_temperature.attrs, legend=True)

root.mainloop()
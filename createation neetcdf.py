import xarray as xr
import os
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
current_path =  os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
ds_temperature = xr.open_dataset(current_path + "2024_temperature_2m.nc")
ds_temperature = ds_temperature.rename({"valid_time": "time", "t2m": "temperature"})  # Renommer les dimensions et variables pour plus de clarté
ds_temperature = ds_temperature.mean(dim=["longitude", "latitude"])  # Moyenne spatiale pour obtenir une série temporelle globale
ds_temperature["temperature"] = ds_temperature["temperature"] - 273.15  # Convertir de Kelvin à Celsius
ds_temperature["temperature"].attrs["units"] = "°C"  # Ajouter les unités aux attributs de la variable


ds_temperature.to_netcdf(current_path + "2024_temperature_2m_temporel.nc", engine="h5netcdf")




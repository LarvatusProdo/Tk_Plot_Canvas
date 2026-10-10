"""Build the time-series NetCDF file used by the xarray time-series example.

Reads ``2024_temperature_2m.nc`` (ERA5-like 2 m temperature on a grid),
averages it over longitude/latitude, converts Kelvin to Celsius and writes
``2024_temperature_2m_temporel.nc``. Both files live in the parent folder of
the project. Run from the project root::

    python tools/create_temporal_netcdf.py
"""

from pathlib import Path

import xarray as xr

DATA_DIR = Path(__file__).resolve().parents[2]
SOURCE_FILE = DATA_DIR / "2024_temperature_2m.nc"
OUTPUT_FILE = DATA_DIR / "2024_temperature_2m_temporel.nc"
RENAMED_NAMES = {"valid_time": "time", "t2m": "temperature"}
SPATIAL_DIMENSIONS = ["longitude", "latitude"]
KELVIN_TO_CELSIUS_OFFSET = 273.15
CELSIUS_UNITS = "°C"
NETCDF_ENGINE = "h5netcdf"


def build_time_series(dataset: xr.Dataset) -> xr.Dataset:
    """Turn a gridded temperature dataset into a global mean time series.

    Args:
        dataset: Dataset with "valid_time", "t2m", "longitude" and "latitude".

    Returns:
        Dataset with a "time" dimension and a "temperature" variable in °C.
    """
    time_series = dataset.rename(RENAMED_NAMES)
    time_series = time_series.mean(dim=SPATIAL_DIMENSIONS)
    time_series["temperature"] = time_series["temperature"] - KELVIN_TO_CELSIUS_OFFSET
    time_series["temperature"].attrs["units"] = CELSIUS_UNITS
    return time_series


def main() -> None:
    """Read the source file and write the time-series file."""
    time_series = build_time_series(xr.open_dataset(SOURCE_FILE))
    time_series.to_netcdf(OUTPUT_FILE, engine=NETCDF_ENGINE)


if __name__ == "__main__":
    main()

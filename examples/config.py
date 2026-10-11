"""Paths shared by the examples.

The NetCDF data files live in the parent folder of the project.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT.parent
VIEWS_DIR = PROJECT_ROOT / "Exemples de vues json"
TIME_SERIES_FILE = DATA_DIR / "2024_temperature_2m_temporel.nc"
MAP_FILE = DATA_DIR / "2024_temperature_2m_carte.nc"
TIME_SERIES_VIEW = VIEWS_DIR / "vue_xarray.json"
MAP_VIEW = VIEWS_DIR / "vue_xarray_3D.json"

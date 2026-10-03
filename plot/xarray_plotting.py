"""Xarray plotting methods for the Tk plot canvas."""

import copy
import tkinter as tk
from typing import Optional

import xarray as xr
from numpy import datetime64

try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    CARTOPY_INSTALLED = True
except Exception:
    CARTOPY_INSTALLED = False


class XarrayPlotMixin:
    """Plot one-dimensional and two-dimensional xarray datasets on a canvas."""

    def plot_xarray_2D(
        self,
        ds: xr.Dataset,
        *,
        title: Optional[str] = None,
        grid: bool = True,
        clear: bool = True,
        legend: bool = False,
        label: Optional[dict] = None,
        replot: bool = False,
        **plot_kwargs,
        ) -> None:
        """Plot a curve in the embedded canvas if the xarray Dataset has 1 dimension.

        Args:
            ds: xarray Dataset containing the data to plot.
            title: Optional plot title.
            grid: Whether to show a grid.
            clear: Whether to clear previous plot before plotting.
            legend: Whether to show a legend (if labels are provided).
            label: Optional dict of metadata to display in the legend (e.g., {'name': 'curve', 'value': 42}).
            **plot_kwargs: Passed to `Axes.plot`.
        """
        # Construct label string from dict
        label_str = None
        if label:           
            label_str = self.get_string_legende(label, shown_keys=self.Is_title_display)

        modif_plot_kwargs = copy.copy(plot_kwargs)   
        if self.parametre_vue != {}: # Si un fichier json a été chargé : 
            # Changement de self.parametre_vue, si l'utilisateuur spécifie des attriibues
            n_lines = len(self._lines) 
            if str(n_lines) in self.parametre_vue["curves"] :
                for key in self.parametre_vue["curves"][str(n_lines)]:
                    if not key in plot_kwargs:
                        modif_plot_kwargs[key] = self.parametre_vue["curves"][str(n_lines)][key]

        # remove type option from modif_plot_kwargs if it exists, since it's not needed for 2D plotting
        if "type" in modif_plot_kwargs:
            del modif_plot_kwargs["type"]

        list_dim_var = list(ds.dims) + list(ds.data_vars)
        dimension = self.xarray_data["x"] if self.xarray_data["x"] in list_dim_var else list(ds.dims)[0]
        variable = self.xarray_data["y"] if self.xarray_data["y"] in list_dim_var else list(ds.data_vars)[0]

        x = ds[dimension].values
        y = ds[variable].values

        if type(x[0]) == datetime64:
            self.Is_Date_on_x_axis = True
            self.axes.xaxis_date()  # Set x-axis to date format if x data is datetime

        # On sauvegarde pour le prochain xarray : 
        self.xarray_data["x"] = dimension
        self.xarray_data["y"] = variable
    
        line, = self.axes.plot(x, y, label=label_str, **modif_plot_kwargs)
        self._lines.append(line)
        self._line_labels.append(label)

        # Cartouche: Update the cartouche with the metadata of the newly added line.
        if not replot :
            label_cartouche = dict()
            for key in self.cartouch_to_show :
                if label is not None and key in label:
                    label_cartouche[key] = label[key]
            self.fill_cartouche_frame(label_to_display=label_cartouche, line_index=len(self._lines)-1, line_display=True)
        else :
            self.update_cartouche_frame()

        self.axes.grid(grid)

        # Apply loaded view parameters to the new plot if a view has been loaded, to ensure consistency with the loaded view settings for axes, title, and labels.
        if self.parametre_vue != {}: # if a json file has been loaded :
            # Update X et Y axis from self.parameter_vue
            self._update_axis(self.axes.xaxis, self.parametre_vue.get("X_axis"), axe= "X" )
            self._update_axis(self.axes.yaxis, self.parametre_vue.get("Y_axis"), axe= "Y" )

            if title is not None and "title" in self.parametre_vue :
                self.axes.set_title(title, self.parametre_vue["title"])
                self._title_var.set(title)

            if dimension is not None and "xlabel" in self.parametre_vue :
                # Get unit label from xarray variable attributes if it exists
                if "units" in ds[dimension].attrs:
                    dimension_label = f"{dimension.capitalize()} ({ds[dimension].attrs['units']})"
                else:
                    dimension_label = dimension.capitalize()

                self.axes.set_xlabel(dimension_label, self.parametre_vue["xlabel"])
                self._xlabel_var.set(dimension_label)

            if variable is not None and "ylabel" in self.parametre_vue : 
                # Get unit label from xarray variable attributes if it exists
                if "units" in ds[variable].attrs:
                    variable_label = f"{variable.capitalize()} ({ds[variable].attrs['units']})"
                else:
                    variable_label = variable.capitalize()

                self.axes.set_ylabel(variable_label, self.parametre_vue["ylabel"])
                self._ylabel_var.set(variable_label)

        if legend and label_str is not None:
            if self.Is_legend_display:
                self.axes.legend(draggable=True)  # Make the legend draggable

        self._canvas.draw()
    
    def plot_xarray_3D(
        self,
        ds: xr.Dataset,
        *,
        title: Optional[str] = None,
        grid: bool = True,
        clear: bool = True,
        legend: bool = False,
        label: Optional[dict] = None,
        replot: bool = False,
        is_map: bool = None,
        **plot_kwargs,
        ) -> None:
        """Plot a curve in the embedded canvas if the xarray Dataset has 1 dimension."""
        if clear:
            self.axes.cla()
            self._lines.clear()
            self._line_labels.clear()
            if self._colorbar is not None:
                try:
                    self._colorbar.remove()
                except Exception:
                    pass
                self._colorbar = None

        # List dimension and variable of the xarray data
        list_dim_var = list(ds.dims) + list(ds.data_vars)
        dimension_abscisse = self.xarray_data["x"] if self.xarray_data["x"] in list_dim_var else list(ds.dims)[0]
        dimension_ordonnee = self.xarray_data["y"] if self.xarray_data["y"] in list_dim_var else list(ds.dims)[1]
        variable = self.xarray_data["z"] if self.xarray_data["z"] in list_dim_var else list(ds.data_vars)[0]

        # On sauvegarde pour le prochain xarray : 
        self.xarray_data["x"] = dimension_abscisse
        self.xarray_data["y"] = dimension_ordonnee
        self.xarray_data["z"] = variable

     
        # Use the existing plot_3D_map attribute if is_map is not provided
        if is_map is None:
            is_map = self.plot_3D_map 
        
        list_dimension_lower = [dimension_abscisse.lower(), dimension_ordonnee.lower()]

        # Check if the dimensions are longitude and latitude to determine if it's a map. If both "longitude" and "latitude" are present in the dimension names, we can assume it's a map and set is_map to True. Otherwise, set is_map to False.
        if "longitude" in list_dimension_lower and "latitude" in list_dimension_lower:
            is_map = self.plot_3D_map  # If the dimensions are longitude and latitude, we can assume it's a map and set is_map to True
        else :
            is_map = False  # If the dimensions are not longitude and latitude, we can assume it's not a map and set is_map to False

        # If is_map is True and Cartopy is installed, we will create a new axes with a PlateCarree projection and add coastlines and borders for geographical context. Otherwise, we will keep the existing axes for non-map plots.
        if is_map and CARTOPY_INSTALLED : 
            spec = self.axes.get_subplotspec()   # mémorise l'emplacement
            self.axes.remove()                   # supprime l'ancien axe
            self.axes = self.figure.add_subplot(spec, projection=ccrs.PlateCarree())
            self.axes.add_feature(cfeature.COASTLINE, linewidth=0.5)
            self.axes.add_feature(cfeature.BORDERS, linewidth=0.3)
            self.axes.xaxis.set_visible(True)
            self.axes.yaxis.set_visible(True)
            #self.axes.tick_params(axis="x", which="both", bottom=False, top=False, labelbottom=False)
            #self.axes.tick_params(axis="y", which="both", left=False, right=False, labelleft=False)
            self.plot_3D_map = True
        else :
            self.plot_3D_map = False

        x = ds[dimension_abscisse].values
        y = ds[dimension_ordonnee].values
        z = ds[variable].values

        # Check if the dimensions of x, y, and z are consistent for contourf plotting
        if (len(y) , len(x)) == z.shape:
            pass  # Dimensions are consistent, no action needed
        elif (len(x) , len(y)) == z.shape:
            z = z.T  # Transpose z to match the dimensions of x and y
        else:
            tk.messagebox.showerror("Error", f"Dimensions of x, y, and z are inconsistent for contourf plotting. x: {len(x)}, y: {len(y)}, z: {z.shape}", parent=self)
            return # Exit the function if dimensions are inconsistent
        
        # Set x-axis to date format if x data is datetime
        if type(x[0]) == datetime64:
            self.Is_Date_on_x_axis = True
            self.axes.xaxis_date()  
        # Set y-axis to date format if y data is datetime
        if type(y[0]) == datetime64:
            self.Is_Date_on_y_axis = True
            self.axes.yaxis_date()
            
        # Create a filled contour plot using the xarray data
        mapping = self.axes.contourf(x, y, z, antialiased=False)

        # Add a colorbar to the plot, removing any existing colorbar first to avoid overlap
        if self._colorbar is not None:
            try:
                self._colorbar.remove()
            except Exception:
                pass
            self._colorbar = None
        self._colorbar = self.figure.colorbar(mapping, ax=self.axes)
        self._colorbar.set_label(variable.capitalize() + (f" ({ds[variable].attrs['units']})" if "units" in ds[variable].attrs else ""))

        self._lines.append(mapping)
        self._line_labels.append(label)      

        # Cartouche: Update the cartouche with the metadata of the newly added line.
        if not replot :
            label_cartouche = dict()
            for key in self.cartouch_to_show :
                if label is not None and key in label:
                    label_cartouche[key] = label[key]
            self.fill_cartouche_frame(label_to_display=label_cartouche, line_index=len(self._lines)-1, line_display=True)
        else :
            self.update_cartouche_frame()

        # Apply labels on the chart
        if title is not None:
            self.axes.set_title(title)
            self._title_var.set(title)

        if dimension_abscisse is not None:
            # Get unit label from xarray variable attributes if it exists
            if "units" in ds[dimension_abscisse].attrs:
                dimension_label = f"{dimension_abscisse.capitalize()}"
            else:
                dimension_label = dimension_abscisse.capitalize()

            self.axes.set_xlabel(dimension_label)
            self._xlabel_var.set(dimension_label)

        if dimension_ordonnee is not None:
            # Get unit label from xarray variable attributes if it exists
            if "units" in ds[dimension_ordonnee].attrs:
                variable_label = f"{dimension_ordonnee.capitalize()}"
            else:
                variable_label = dimension_ordonnee.capitalize()

            self.axes.set_ylabel(variable_label)
            self._ylabel_var.set(variable_label)

        # Apply loaded view parameters to the new plot if a view has been loaded, to ensure consistency with the loaded view settings for axes, title, and labels.
        if self.parametre_vue != {} and self.parametre_vue is not None : # if a json file has been loaded :
            self.load_parameters(parameters_to_load=self.parametre_vue)

        self.axes.xaxis.set_visible(True)
        self.axes.yaxis.set_visible(True)

        self._canvas.draw()

    def plot_xarray(
        self,
        ds: xr.Dataset,
        *,
        title: Optional[str] = None,
        grid: bool = True,
        clear: bool = True,
        legend: bool = False,
        label: Optional[dict] = None,
        replot: bool = False,
        **plot_kwargs,  
        )-> None:
        """
        Plot data from an xarray Dataset in the embedded canvas.

        """

        if clear:
            self.axes.cla()
            self._lines.clear()
            self._line_labels.clear()

        
        # construction des variables associées au xarray : 
        if not replot :
            self.list_data_xarray.append(ds)

        # La méthpde plot_xarray_2D ou plot_xarray__3D sont définies dans le fichier xarray_plotting.py
        if len(ds.dims) == 1 : 
            self.type_plot = "2D"
            self.plot_xarray_2D(ds, title=title, grid=grid, clear=clear, legend=legend, label=label, replot=replot, **plot_kwargs)
        
        elif len(ds.dims) == 2 :
            self.type_plot = "3D"
            self.plot_xarray_3D(ds, title=title, grid=grid, clear=clear, legend=legend, label=label, replot=replot, **plot_kwargs)
        else :
            raise ValueError("The xarray dataset must have either 1 or 2 dimensions for plotting.")

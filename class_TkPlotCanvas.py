
from cProfile import label
from operator import index
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from typing import Iterable, Optional
from functools import partial

import matplotlib
import logging

# Ensure TkAgg is selected before importing backend-specific classes.
matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.font_manager as fm
from matplotlib.artist import Artist 

import copy
import json
import xarray as xr
import os
from numpy import datetime64
from numpy import timedelta64
import platform

from vertical_frame import VerticalScrolledFrame
from class_menu_graphique import Menu_graphique


"""Tkinter plotting widgets with Matplotlib integration.

This module provides a Tkinter-based plotting canvas with embedded
Matplotlib figures, a context menu for customizing axes, curves,
cartouche metadata, and legend settings, and support for saving/loading views.
"""

class TkPlotCanvas(ttk.Frame):
    """A Tkinter Frame that embeds a Matplotlib Figure.

    Attributes:
        figure: The Matplotlib Figure instance.
        axes: The Matplotlib Axes instance used for plotting.
        _canvas: The Tkinter widget wrapping the Figure.
    """
    _initialized_style: bool = False
    def __init__(
        self,
        master: Optional[tk.Misc] = None,
        dpi: int = 100,
        figsize: tuple[float, float] = (5.0, 4.0),
        bg_color: str = 'white',
        load_view: str = None,
        **kwargs,
    ):
        """Initialize the plot canvas.

        Args:
            master: Parent widget.
            dpi: Dots-per-inch for the Matplotlib figure.
            figsize: Figure size in inches (width, height).
            bg_color: Background color for the plot.
            load_view : json file associated to a previous view saved 
            **kwargs: Additional kwargs passed to tk.Frame.
        """
        super().__init__(master, **kwargs)

        if not self._initialized_style :
            self._initialized_style = True
            self._setup_styles(bg=bg_color)

        # StringVars to hold the current title and axis labels for synchronization with the menu.
        self._title_var = tk.StringVar(value="")
        self._xlabel_var = tk.StringVar(value="")
        self._ylabel_var = tk.StringVar(value="")
        self.legend_to_show = []
        self.cartouch_to_show = []
        self.Is_legend_display = False
        self.Is_title_display = False
        self.Is_Date_on_x_axis = False
        self.Is_cartouche_display = True
        self._colorbar = None

        # Panedwindow for resizable layout
        self.panedwindow = ttk.Panedwindow(self, orient=tk.VERTICAL)
        self.panedwindow.pack(fill=tk.BOTH, expand=True)

        # Frame Plot
        self._plot_frame = ttk.Frame(self.panedwindow, style='TkPlotCanvas.TFrame')
        self.panedwindow.add(self._plot_frame, weight=1)    

        # Frame Cartouche
        self._cartouche_frame = VerticalScrolledFrame(self.panedwindow, x_bar = True, bg_canvas ="", height_canvas = 100 , style_frame = 'Cartouche.TFrame')
        self.panedwindow.add(self._cartouche_frame, weight=0)
        self.cartouche_initialized = False
        self._cartouche_grid = []
        self._cartouche_title_grid = []

        # Ensure we use a TkAgg backend.
        matplotlib.use("TkAgg")

        self.figure = Figure(figsize=figsize, dpi=dpi)
        self.figure.set_facecolor(bg_color)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_facecolor(bg_color)
        
        # Track plotted lines so they can be modified after creation.
        self._lines: list = []
        self._line_labels: list = []  # Store original label dicts

        # Create the canvas
        self._canvas = FigureCanvasTkAgg(self.figure, master= self._plot_frame)
        self._canvas.draw()
       
        toolbar = NavigationToolbar2Tk( self._canvas, self._plot_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.X)
        self._canvas.get_tk_widget().pack(fill="both", expand=True)

        # Variable pour les paramètres Xarray : 
        self.xarray_data = dict( x = "", y = "", z = "")
        self.list_data_xarray = []
        

        # Create context menu.
        self.menu_click = tk.Menu(self, tearoff=0)
        self.menu_click.add_command(label="Sauvegarder la vue", command=self.save_parameters, accelerator="Ctrl+S")
        self.menu_click.add_command(label="Chargement de la vue", command=self.load_parameters, accelerator="Ctrl+G")
        self.menu_click.add_separator()
        self.menu_click.add_command(label="Modification du graphique", command=partial(self.open_menu_graphique, "Axes et titre"))

        self._canvas.get_tk_widget().bind("<Button-3>", self.do_popup)
        self._canvas.get_tk_widget().bind("<Control-g>", self.load_parameters)
        self._canvas.get_tk_widget().bind("<Control-s>", self.save_parameters)

        # load the view if specified
        if load_view is not None  and os.path.isfile(load_view) :
            self.parametre_vue = self.load_parameters(path_to_load = load_view)
        else : 
            self.parametre_vue = {}

    def _setup_styles(self, bg="white"):
        """Configure default ttk styles for the plot canvas and surrounding widgets."""
        self.style = ttk.Style()

        # Set background colors for the graph and frame styles
        self.bg_color_graph = bg
        self.bg_color_frame = self.style.lookup("TFrame", "background")

        # Set a default font based on the operating system for better cross-platform appearance
        if platform.system() == "Linux" : 
            self.font_default = "DejaVu Sans"
        else :
            self.font_default = "Arial"

        # Get the list of available font names from both Matplotlib and Tkinter for use in font selection dialogs
        self.list_font_matplotlib = list(set(fm.FontManager().get_font_names()))
        self.list_font_tkinter = list(tk.font.families())

        # Configure ttk styles for background color
        self.style.configure('TkPlotCanvas.TFrame')

        self.style.configure('TkPlotCanvas.TNotebook')
        self.style.configure('TkPlotCanvas.TNotebook.Tab', font=(self.font_default, 10, 'bold'), padding=(10, 5))
        self.style.map('TkPlotCanvas.TNotebook.Tab', foreground=[('selected', 'black'), ('!selected', 'gray')], background=[('selected', self.bg_color_frame), ('!selected', self.bg_color_frame)])

        self.style.configure('TkPlotCanvas.TLabel')
        self.style.configure('TkPlotCanvas.TCheckbutton')
        self.style.configure('TkPlotCanvas.TLabelframe')
        self.style.configure('TkPlotCanvas.TLabelframe.Label', font=(self.font_default, 10, 'bold'))       


        self.style.configure('Cartouche_titre.TLabel', font=(self.font_default, 10, 'bold'), foreground="black", background=self.bg_color_graph)
        self.style.configure('Cartouche.TLabel', font=(self.font_default, 10, 'normal'), foreground="black", background=self.bg_color_graph)
        self.style.configure('Cartouche.TFrame', background= self.bg_color_graph)

        self.style.configure('Titre_parammetre.TLabel', font=(self.font_default, 10, 'bold'), foreground="black")

        self.style.configure('TkPlotCanvas.TEntry')
        self.style.configure('TkPlotCanvas.TButton')

        
        self.style.configure('TkPlotCanvas_Courbe.TLabel', font=(self.font_default, 10, 'bold'), foreground="black")

    def do_popup(self, event):
        """Show the context menu at the mouse cursor position."""

        self.menu_click.tk_popup(event.x_root, event.y_root)
        

    def open_menu_graphique(self, menu_type):
        """Open the graphical settings dialog and close any previous instance."""
        try : 
            self.open_menu_graphique.destroy()  # Ferme le menu précédent s'il existe
        except Exception:
            pass
        self.open_menu_graphique = Menu_graphique(self, notebook_shown=menu_type)

    def fill_cartouche_frame(self, label_to_display: Optional[dict] = None, line_index: int = 0, line_display: bool = True) -> None:
        """
        Fill the cartouche frame with metadata information for a given line index.
        Args:            
            label_to_display: A dictionary of metadata to display in the cartouche, where keys are the metadata names and values are the corresponding values to display.
            line_index: The index of the line for which to display the metadata in the cartouche.
            line_display: Whether to display the line style and marker in the cartouche.
        """
        
        # Clear previous cartouche content for this line index
        if len(self._cartouche_grid) > line_index+1 : 
            for widget in self._cartouche_grid[line_index]:
                try :
                    widget.destroy()
                except Exception:
                    pass
            self._cartouche_grid[line_index] = []
        else :
            self._cartouche_grid.append([])
            while len(self._cartouche_grid) <= line_index+1 :
                self._cartouche_grid.append([])

        
        # Add a label to display metadata from the active line.
        if not(label_to_display is None):
                     
            column_index = 1
            if not self.cartouche_initialized:
                for key in label_to_display:
                    self._cartouche_title_grid.append(ttk.Label(self._cartouche_frame, text=key, style='Cartouche_titre.TLabel'))
                    self._cartouche_title_grid[-1].grid(row=0, column=column_index, sticky="w", padx=5, pady=5)
                    column_index += 1
                self.cartouche_initialized = True
            
        if line_display and self.type_plot == "2D":
            # Add line show :
            line = self._lines[line_index] 
            color = line.get_color()
            linestyle = line.get_linestyle() if line.get_linestyle() != "None" else ""
            if linestyle == '-':
                linestyle = "―"
            marker = line.get_marker() if line.get_marker() != "None" else ""

            self._cartouche_grid[line_index].append(tk.Label(self._cartouche_frame, text=f"{linestyle}{marker}", background=self.bg_color_graph, foreground=color, width=3, font=("Helvetica", 15, 'bold')))
            self._cartouche_grid[line_index][-1].grid(row= line_index + 1, column=0, sticky="w", padx=(5,0), pady=0)
            
        else : 
            self._cartouche_grid[line_index].append(None)

        if not(label_to_display is None):
            # Add the values of the metadata in the cartouche
            column_index = 1       
            for key, value in label_to_display.items():
                self._cartouche_grid[line_index].append(ttk.Label(self._cartouche_frame, text=str(value), style="Cartouche.TLabel"))
                self._cartouche_grid[line_index][-1].grid(row=line_index + 1, column=column_index, sticky="w", padx=5, pady=5)
                column_index += 1   

    def get_string_legende(self, label_dict, shown_keys = False):
        """Build the legend string from a metadata dictionary based on selected display keys."""
        
        string_legende = []

        for key in self.legend_to_show :
            if key in label_dict :
                value = label_dict[key]

                if shown_keys:
                    string_legende.append(f"{key}: {value}")
                else:
                    string_legende.append(f"{value}")

        return ", ".join(string_legende)


    def _update_legende(self):
        """Refresh legend labels and redraw the legend when settings change."""

        for index, line in enumerate(self._lines):
            label_dict = self._line_labels[index]
            line.set_label(self.get_string_legende(label_dict, shown_keys=self.Is_title_display))  # Update line label based on legend entry values and whether to show key titles

        # Update legend to reflect changes if lines are in the canvas
        if self.Is_legend_display and len(self._lines) > 0:
            if len(self.legend_to_show) > 0:
                self.axes.legend(draggable=True)  
            else :
                # If no keys are selected to show in the legend, remove the legend from the axes
                try : 
                    legend = self.axes.get_legend()
                    if legend:
                        legend.remove()  # Hide legend if no keys are selected to show
                except Exception:
                    pass
                
        # If legend display is turned off, remove the legend from the axes if it exists
        elif not self.Is_legend_display and len(self._lines) > 0: 
            legend = self.axes.get_legend()
            if legend:
                legend.remove()  # Hide legend

        self._canvas.draw()

    def _update_axis(self, axis_to_update, parameters = {}, axe = "X"):
        """Apply saved axis settings such as tick font, limits, and scale type."""
        
        if "ticks" in parameters:
            tick_params = parameters["ticks"]

            font_name = tick_params.get("name") if tick_params.get("name") in self.list_font_matplotlib else self.font_default

            for tick in axis_to_update.get_ticklabels():
                tick.set_fontname(font_name)
                tick.set_fontsize(tick_params.get("size"))
                tick.set_fontstyle(tick_params.get("style"))
                tick.set_fontweight(tick_params.get("weight"))
                tick.set_color(tick_params.get("color"))  
        
        if axe == "X":
            if "autoscale" in parameters :
                if parameters["autoscale"] : 
                    self.axes.autoscale(axis="x", tight=True)
                else:
                    self.axes.set_xlim(parameters["lim"])
            elif "lim" in parameters :
                self.axes.set_xlim(parameters["lim"])
            
            if "scale" in parameters and not self.Is_Date_on_x_axis:
                self.axes.set_xscale(parameters["scale"])   
                   
            if "inversion_axis" in parameters :
                if parameters["inversion_axis"] :
                    self.axes.invert_xaxis()


        if axe == "Y":
            if "autoscale" in parameters :
                if parameters["autoscale"] : 
                    self.axes.autoscale(axis="y", tight=True)
                    
                else:
                    self.axes.set_ylim(parameters["lim"])
            elif "lim" in parameters :
                 self.axes.set_ylim(parameters["lim"])
            
            if "scale" in parameters :
                self.axes.set_yscale(parameters["scale"])
            
            if "inversion_axis" in parameters :
                if parameters["inversion_axis"] :
                    self.axes.invert_yaxis()
      

        return True

    def save_parameters(self, *args):

        if hasattr(self.open_menu_graphique, "master"): # Check if the Menu_graphique Window is open 
            if self.open_menu_graphique.winfo_exists():
                window_parent = self.open_menu_graphique
            else : 
                window_parent = self
        else:
            window_parent = self

        try :
            path_to_save = filedialog.asksaveasfilename(parent = window_parent, initialdir=".", title="Enregistrer les paramètres",
                                                defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if not path_to_save:
                return  # User cancelled the save dialog
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred while opening the save dialog:\n{e}")
            return 
        
        # Implement saving parameters to a JSON file here
        # Store :
        #  - axes limits and scale types
        #  - font properties of axes and title
        #  - curve properties (color, linewidth, linestyle, marker, markersize, label)
        #  - cartouche parameters (metadata keys)
        #  - legend parameters (location, font properties, key to display in the legend)
        #  - xarray 3D settings (x, y, z variables, colorbar state, colormap, and color limits)

        parameters = self.get_current_parameters()
        try : 
            with open(path_to_save, 'w') as f:
                json.dump(parameters, f, indent=4)
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred while saving the parameters:\n{e}")

    def get_current_parameters(self):
        """
        Get the current parameters of the plot to be able to save them in a json file and reload them later to restore the view.
        """
        
        parameters = {

            "background_color": self.bg_color_graph,
            "window_size": (self.master.winfo_width(), self.master.winfo_height()),
            "window_position": (self.master.winfo_x(), self.master.winfo_y()),


            "X_axis": {
                "lim": self.axes.get_xlim(),
                "scale": self.axes.get_xscale(),
                "autoscale": self.axes.get_autoscalex_on(),  # Assuming you want to save the autoscale state for x-axis
                "inversion_axis" : bool(self.axes.xaxis_inverted()),
                "ticks": {
                    "name" : self.axes.xaxis.get_ticklabels()[0].get_fontname() if len(self.axes.xaxis.get_ticklabels()) > 0 else None,
                    "size": self.axes.xaxis.get_ticklabels()[0].get_fontsize() if len(self.axes.xaxis.get_ticklabels()) > 0 else None,
                    "style": self.axes.xaxis.get_ticklabels()[0].get_fontstyle() if len(self.axes.xaxis.get_ticklabels()) > 0 else None,
                    "weight": self.axes.xaxis.get_ticklabels()[0].get_fontweight() if len(self.axes.xaxis.get_ticklabels()) > 0 else None,
                    "color": self.axes.xaxis.get_ticklabels()[0].get_color() if len(self.axes.xaxis.get_ticklabels()) > 0 else None
                }
            },
            "Y_axis": {
                "lim": self.axes.get_ylim(),
                "scale": self.axes.get_yscale(),
                "autoscale": self.axes.get_autoscaley_on(),  # Assuming you want to save the autoscale state for x-axis
                "inversion_axis" : bool(self.axes.yaxis_inverted()),
                "ticks": {
                    "name" : self.axes.yaxis.get_ticklabels()[0].get_fontname() if len(self.axes.yaxis.get_ticklabels()) > 0 else None,
                    "size": self.axes.yaxis.get_ticklabels()[0].get_fontsize() if len(self.axes.yaxis.get_ticklabels()) > 0 else None,
                    "style": self.axes.yaxis.get_ticklabels()[0].get_fontstyle() if len(self.axes.yaxis.get_ticklabels()) > 0 else None,
                    "weight": self.axes.yaxis.get_ticklabels()[0].get_fontweight() if len(self.axes.yaxis.get_ticklabels()) > 0 else None,
                    "color": self.axes.yaxis.get_ticklabels()[0].get_color() if len(self.axes.yaxis.get_ticklabels()) > 0 else None
                    },
            },
            "title": {
                "fontname" : self.axes.title.get_fontproperties().get_name(), 
                "fontsize": self.axes.title.get_fontsize(),
                "fontstyle": self.axes.title.get_fontproperties().get_style(),
                "fontweight": self.axes.title.get_fontproperties().get_weight(),
                "color": self.axes.title.get_color()
            },
            "xlabel": {
                "fontname" : self.axes.xaxis.label.get_fontproperties().get_name(), 
                "fontsize": self.axes.xaxis.label.get_fontsize(),
                "fontstyle": self.axes.xaxis.label.get_fontproperties().get_style(),
                "fontweight": self.axes.xaxis.label.get_fontproperties().get_weight(),
                "color": self.axes.xaxis.label.get_color()
            },
            "ylabel": {
                "fontname" : self.axes.yaxis.label.get_fontproperties().get_name(), 
                "fontsize": self.axes.yaxis.label.get_fontsize(),
                "fontstyle": self.axes.yaxis.label.get_fontproperties().get_style(),
                "fontweight": self.axes.yaxis.label.get_fontproperties().get_weight(),
                "color": self.axes.yaxis.label.get_color()
            },
            "plot_type": getattr(self, "type_plot", "2D"),
            "curves": {
                str(index): (
                    {
                        "type": "contour",
                        "cmap": line.get_cmap().name if hasattr(line, "get_cmap") else None,
                        "clim": tuple(line.get_clim()) if hasattr(line, "get_clim") else None,
                    }
                    if hasattr(line, "get_cmap")
                    else {
                        "type": "line",
                        "color": line.get_color(),
                        "linewidth": line.get_linewidth(),
                        "linestyle": line.get_linestyle(),
                        "marker": line.get_marker(),
                        "markersize": line.get_markersize(),
                    }
                )
                for index, line in enumerate(self._lines)
            },
            "cartouche": {
                "cartouche_title_grid": [label.cget("text") for label in self._cartouche_title_grid],
                "cartouche_font_title": self.style.configure('Cartouche_titre.TLabel'),
                "cartouche_font_line": self.style.configure('Cartouche.TLabel'),
                "Is_cartouche_display": self.Is_cartouche_display,
            },
            "legend": {
                "displayed_keys": [ key for key in self.legend_to_show if key != '' ] if len(self.legend_to_show) > 0 else [],
                "Is_legend_display" : self.Is_legend_display,
                "Is_title_display": self.Is_title_display ,

            },
            "xarray_data" : {
                "x" : self.xarray_data["x"],
                "y" : self.xarray_data["y"],
                "z" : self.xarray_data["z"] if "z" in self.xarray_data else None,
            },
        }

        # Add 3D plot parameters if applicable
        parameters = self.get_3D_parameters(parameters)

        return parameters

    def get_3D_parameters(self, parameters):
        """
        Get the parameters specific to 3D plots, such as colorbar properties, colormap, and color limits, and add them to the provided parameters dictionary.
        Args:
            parameters: A dictionary to which the 3D plot parameters will be added.
        Returns:
            The updated parameters dictionary with 3D plot parameters included.
        """
        # Add 3D plot parameters if applicable
        if getattr(self, "type_plot", "") == "3D" and len(self._lines) > 0:
            parameters["xarray_3D"] = {
                "has_colorbar": self._colorbar is not None,
                "colorbar_orientation": self._colorbar.orientation if self._colorbar is not None and hasattr(self._colorbar, "orientation") else None,
                "cmap": self._lines[0].get_cmap().name if hasattr(self._lines[0], "get_cmap") else None,
                "clim": tuple(self._lines[0].get_clim()) if hasattr(self._lines[0], "get_clim") else None,
                "alpha": self._lines[0].get_alpha() if hasattr(self._lines[0], "get_alpha") else None,
            }

            if self._colorbar is not None and hasattr(self._colorbar, "ax"):
                if self._colorbar.orientation == "vertical" :
                    parameters["xarray_3D"]["colorbar_font"] = {
                        "fontname": self._colorbar.ax.yaxis.label.get_fontproperties().get_name() ,
                        "fontsize": self._colorbar.ax.yaxis.label.get_fontsize(),
                        "fontstyle": self._colorbar.ax.yaxis.label.get_fontproperties().get_style(),
                        "fontweight": self._colorbar.ax.yaxis.label.get_fontproperties().get_weight(),
                    }
                    parameters["xarray_3D"]["colorlabel_colorbar"] = self._colorbar.ax.yaxis.label.get_color() if self._colorbar.ax.yaxis.label.get_color() is not None else "black"

                elif self._colorbar.orientation == "horizontal" :
                    parameters["xarray_3D"]["colorbar_font"] = {
                        "fontname": self._colorbar.ax.xaxis.label.get_fontproperties().get_name() ,
                        "fontsize": self._colorbar.ax.xaxis.label.get_fontsize(),
                        "fontstyle": self._colorbar.ax.xaxis.label.get_fontproperties().get_style(),
                        "fontweight": self._colorbar.ax.xaxis.label.get_fontproperties().get_weight(),
                    }
                    parameters["xarray_3D"]["colorlabel_colorbar"] = self._colorbar.ax.xaxis.label.get_color() if self._colorbar.ax.xaxis.label.get_color() is not None else "black"

        # Ensure that the "xarray_3D" key exists in the parameters dictionary, even if it's empty, to maintain consistency when saving/loading views.
        if not "xarray_3D" in parameters:
            parameters["xarray_3D"] = {}

        return parameters


    def load_parameters(self, *args, path_to_load=None, parameters_to_load = None):
        """Load parameters from a JSON file and apply them to the plot to restore a previous view. If parameters_to_load is provided, it will be used directly instead of loading from a file."""

        if  parameters_to_load is not None:
             parameters = parameters_to_load
        else:
            # Implement loading parameters from a JSON file here
            if path_to_load is None:
                if hasattr(self.open_menu_graphique, "master"): # Check if the Menu_graphique Window exist
                    if self.open_menu_graphique.winfo_exists(): # Check if the Menu_graphique Window is shown
                        window_parent = self.open_menu_graphique
                    else : 
                        window_parent = self
                else :
                    window_parent = self
                
                path_to_load = filedialog.askopenfilename(parent = window_parent, initialdir=".", title="Charger les paramètres",
                                                            defaultextension=".json", filetypes=[("JSON files", "*.json")])
                if not path_to_load:
                    return  # User cancelled the save dialog
            try:
                with open(path_to_load, 'r') as f:
                    parameters = json.load(f)

            except Exception as e:
                parameters = {}
            
        # Apply loaded parameters to the plot (axes limits, scale types, font properties, curve properties, cartouche parameters, legend parameters)
        if "background_color" in parameters and parameters.get("plot_type", "2D") == "2D" :
            # Only for 2D plot (by defatult). For 3D plot, it will create a unwanted graph. 
            self.bg_color_graph = parameters["background_color"]
            self.figure.set_facecolor(self.bg_color_graph)
            self.axes.set_facecolor(self.bg_color_graph)
            for line in self._lines:
                if hasattr(line, "set_color"):
                    line.set_color(self.bg_color_graph)
            self._canvas.get_tk_widget().configure(background=self.bg_color_graph)
            self._canvas.draw()

        if "plot_type" in parameters:
            self.type_plot = parameters["plot_type"]
        if "window_size" in parameters:
            self.master.geometry(f"{parameters['window_size'][0]}x{parameters['window_size'][1]}")
        if "window_position" in parameters:
            self.master.geometry(f"+{parameters['window_position'][0]}+{parameters['window_position'][1]}")

        if "X_axis" in parameters:
            self._update_axis(self.axes.xaxis, parameters["X_axis"], axe= "X" )

        if "Y_axis" in parameters:
            self._update_axis(self.axes.yaxis, parameters["Y_axis"], axe= "Y" )
        
        if "title" in parameters:
            title_params = parameters["title"].copy()
            if title_params.get("fontname") not in self.list_font_matplotlib :
                title_params["fontname"] = self.font_default
                parameters["title"]["fontname"] = self.font_default
            self.axes.set_title(self._title_var.get(), **title_params)

        if "xlabel" in parameters:
            xlabel_params = parameters["xlabel"].copy()
            if xlabel_params.get("fontname") not in self.list_font_matplotlib :
                xlabel_params["fontname"] = self.font_default
                parameters["xlabel"]["fontname"] = self.font_default
            self.axes.set_xlabel(self._xlabel_var.get(), **xlabel_params)

        if "ylabel" in parameters:
            ylabel_params = parameters["ylabel"].copy()
            if ylabel_params.get("fontname") not in self.list_font_matplotlib :
                ylabel_params["fontname"] = self.font_default
                parameters["ylabel"]["fontname"] = self.font_default
            self.axes.set_ylabel(self._ylabel_var.get(), **ylabel_params)

        if parameters.get("plot_type","2D") == "2D" :
            for index, line in enumerate(self._lines):
                if "curves" in parameters and str(index) in parameters["curves"]:
                    curve_params = parameters["curves"][str(index)]
                    if curve_params.get("type") == "line" and hasattr(line, "set_color"):
                        line.set_color(curve_params.get("color"))
                        line.set_linewidth(curve_params.get("linewidth"))
                        line.set_linestyle(curve_params.get("linestyle"))
                        line.set_marker(curve_params.get("marker"))
                        line.set_markersize(curve_params.get("markersize"))
                    elif curve_params.get("type") == "contour":
                        if hasattr(line, "set_cmap") and curve_params.get("cmap"):
                            try:
                                line.set_cmap(matplotlib.cm.get_cmap(curve_params["cmap"]))
                            except Exception:
                                pass
                        if hasattr(line, "set_clim") and curve_params.get("clim"):
                            try:
                                line.set_clim(curve_params["clim"])
                            except Exception:
                                pass

        if "cartouche" in parameters:
            cartouche_params = parameters["cartouche"]

            # Set a safe font name that exists in the system : 
            cartouche_params["cartouche_font_title"]["font"] = self._safe_font_name(cartouche_params["cartouche_font_title"]["font"])
            cartouche_params["cartouche_font_line"]["font"] = self._safe_font_name(cartouche_params["cartouche_font_line"]["font"])


            self.Is_cartouche_display = cartouche_params.get("Is_cartouche_display", True)
            if not self.Is_cartouche_display:
                try :
                    self.panedwindow.forget(self._cartouche_frame)
                except:
                    pass
            
            # Load the cartouche title grid and font parameters, and update the cartouche display accordingly
            self.cartouch_to_show = cartouche_params.get("cartouche_title_grid", [])

            for index, label in enumerate(self._cartouche_title_grid):
                if index < len(cartouche_params["cartouche_title_grid"]):
                    label.config(text=cartouche_params["cartouche_title_grid"][index])

            self.style.configure('Cartouche_titre.TLabel',  font= cartouche_params["cartouche_font_title"]["font"], foreground=cartouche_params["cartouche_font_title"]["foreground"] )
            self.style.configure('Cartouche.TLabel', font= cartouche_params["cartouche_font_line"]["font"], foreground=cartouche_params["cartouche_font_line"]["foreground"] )

        if "legend" in parameters:
            legend_params = parameters["legend"]
            self.legend_to_show = legend_params.get("displayed_keys", [])
            for index, line in enumerate(self._lines):
                label_dict = self._line_labels[index]
                line.set_label(self.get_string_legende(label_dict, shown_keys=True))
                 
            self.Is_legend_display = legend_params.get("Is_legend_display", False)
            self.Is_title_display = legend_params.get("Is_title_display", False)
     
            self._update_legende()

        if "xarray_3D" in parameters and parameters.get("plot_type","2D") == "3D":
            xarray_3D_params = parameters["xarray_3D"]
            if len(self._lines) > 0:
                # Colorbar parameters to load, if has_colorbar is in xarray_3D_params
                if xarray_3D_params.get("has_colorbar", False):
                    if self._colorbar is None:
                        try:
                            self._colorbar = self.figure.colorbar(self._lines[0], ax=self.axes)
                        except Exception:
                            self._colorbar = None

                    if self._colorbar is not None:
                        
                        orientation = xarray_3D_params.get("colorbar_orientation")
                        if self._colorbar.orientation == "vertical":
                            colorbar_label = self._colorbar.ax.get_ylabel() if self._colorbar.ax.get_ylabel() is not None else ""
                            colorbar_axis = self._colorbar.ax.yaxis  
                            if orientation == "horizontal" :
                                # Change the orientation of the colorbar
                                self._colorbar = self.change_orientation_colorbar(colorbar_axis, orientation)
                        
                        else:
                            colorbar_label = self._colorbar.ax.get_xlabel() if self._colorbar.ax.get_xlabel() is not None else ""
                            colorbar_axis = self._colorbar.ax.xaxis 
                            if orientation == "horizontal" :
                                # Change the orientation of the colorbar
                                self._colorbar = self.change_orientation_colorbar(colorbar_axis, orientation)
                        
                        
                        if colorbar_label :
                            self._colorbar.set_label(colorbar_label)

                        font_colorbar =  xarray_3D_params.get("colorbar_font", False)
                       
                        if colorbar_label and font_colorbar:
                            colorlabel_colorbar =  xarray_3D_params.get("colorlabel_colorbar", False)
                            self.apply_font_to_the_colorbar(colorbar_axis, font_colorbar, colorlabel_colorbar )
            
                else:
                    if self._colorbar is not None:
                        try:
                            self._colorbar.remove()
                        except Exception:
                            pass
                        self._colorbar = None
                
                cmap_name = xarray_3D_params.get("cmap")
                if cmap_name and hasattr(self._lines[0], "set_cmap"):
                    try:
                        self._lines[0].set_cmap(matplotlib.cm.get_cmap(cmap_name))
                    except Exception:
                        pass

                clim = xarray_3D_params.get("clim")
                if clim and hasattr(self._lines[0], "set_clim"):
                    
                    self._lines[0].set_clim(clim)
                    

                alpha = xarray_3D_params.get("alpha")
                if alpha and hasattr(self._lines[0], "set_alpha"):
                    
                    self._lines[0].set_alpha(alpha)
                    
        try :
            self.xarray_data["x"] = parameters["xarray_data"].get("x", "")
            self.xarray_data["y"] = parameters["xarray_data"].get("y", "")
            self.xarray_data["z"] = parameters["xarray_data"].get("z", "")
        except Exception:
            pass

        self._canvas.draw()

        # Reload the legend menu to update the comboboxes and entries based on the loaded parameters
            # Get the current notebook shown
        current_notebook = self.open_menu_graphique._notebook if hasattr(self.open_menu_graphique, "_notebook") else None
            # If a notebook is currently shown, get its name and reopen the menu with the same notebook shown to update the legend menu display based on the loaded parameters
        if current_notebook is not None:
            notebook_shown = current_notebook.tab(current_notebook.select(), "text")
            self.open_menu_graphique.destroy()  # Close the current menu
            self.open_menu_graphique = Menu_graphique(self, notebook_shown=notebook_shown)  # Reopen the menu with the same notebook shown
    
        return parameters  # Return loaded parameters for potential further use
    
    
    def _safe_font_name(self, font_name:str):
        """Parse a font name string and return a safe font name that exists in the system, falling back to default if necessary."""
        list_font_name = font_name.split(" ")

        try :
            int(list_font_name[1])
        except ValueError :
            # If the second element is not an integer, it means the font string is in a different format (e.g., ['{Arial', 'Greek}', '14', 'bold']), so we need to parse it differently.
            style_font_buff = font_name["font"].split(" ")
            list_font_name = ["","",""]
            list_font_name[0] = style_font_buff[0][1:] + " " + style_font_buff[1][:-1]
            list_font_name[1] = style_font_buff[2]
            list_font_name[2] = style_font_buff[3]
            
        try:
            int(list_font_name[1])
        except ValueError:
            list_font_name = [self.font_default, "12", "normal"]  # Default values if parsing fails

        if not list_font_name[0] in self.list_font_tkinter :
            list_font_name[0] = self.font_default

        # On Linux, if the font name does not start with '{', we need to add it to ensure proper rendering in Tkinter.
        if list_font_name[0][0] != "{" and platform.system() == "Linux" :
            list_font_name[0] = "{" + list_font_name[0] + "}"

        safe_font = " ".join(list_font_name)

        return safe_font

    def plot(
        self,
        x: Iterable[float],
        y: Iterable[float],
        *,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        grid: bool = True,
        clear: bool = True,
        legend: bool = False,
        label: Optional[dict] = None,
        **plot_kwargs,
    ) -> None:
        """Plot a curve in the embedded canvas.

        Args:
            x: X data values.
            y: Y data values.
            title: Optional plot title.
            xlabel: Optional x-axis label.
            ylabel: Optional y-axis label.
            grid: Whether to show a grid.
            clear: Whether to clear previous plot before plotting.
            legend: Whether to show a legend (if labels are provided).
            label: Optional dict of metadata to display in the legend (e.g., {'name': 'curve', 'value': 42}).
            **plot_kwargs: Passed to `Axes.plot`.
        """
        if clear:
            self.axes.cla()
            self._lines.clear()
            self._line_labels.clear()

        self.type_plot = "2D"

        # Construct label string from dict
        label_str = None
        if label:           
            label_str = self.get_string_legende(label, shown_keys=self.Is_title_display)
        
        modif_plot_kwargs = copy.copy(plot_kwargs)   
        if self.parametre_vue != {}: # Si un fichier json a été chargé : 
            # Changement de self.parametre_vue, si l'utilisateuur spécifie des attriibues
            n_lines = len(self._lines) 
            for key in self.parametre_vue["curves"][str(n_lines)]:
                if not key in plot_kwargs:
                    modif_plot_kwargs[key] = self.parametre_vue["curves"][str(n_lines)][key]

        if type(x[0]) == datetime64:
            self.Is_Date_on_x_axis = True
            self.axes.xaxis_date()  # Set x-axis to date format if x data is datetime

        
        line, = self.axes.plot(x, y, label=label_str, **modif_plot_kwargs)
        self._lines.append(line)
        self._line_labels.append(label)

        # Cartouche: Update the cartouche with the metadata of the newly added line.
        label_cartouche = dict()
        for key in self.cartouch_to_show :
            if label is not None and key in label:
                label_cartouche[key] = label[key]

        self.fill_cartouche_frame(label_to_display= label_cartouche, line_index=len(self._lines)-1, line_display=True)

        if title is not None and "title" in self.parametre_vue :
            self.axes.set_title(title, self.parametre_vue["title"])
            self._title_var.set(title)
        if xlabel is not None and "xlabel" in self.parametre_vue :
            self.axes.set_xlabel(xlabel, self.parametre_vue["xlabel"])
            self._xlabel_var.set(xlabel)
        if ylabel is not None and "ylabel" in self.parametre_vue : 
            self.axes.set_ylabel(ylabel, self.parametre_vue["ylabel"])
            self._ylabel_var.set(ylabel)

        self.axes.grid(grid)

        if self.parametre_vue != {}: # Si un fichier json a été chargé : 
            # Update X et Y axis from self.parameter_vue
            self._update_axis(self.axes.xaxis, self.parametre_vue.get("X_axis"), axe= "X" )
            self._update_axis(self.axes.yaxis, self.parametre_vue.get("Y_axis"), axe= "Y" )

        if legend and label_str is not None:
            if self.Is_legend_display:
                self.axes.legend(draggable=True)  # Make the legend draggable

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

        if len(ds.dims) == 1 : 
            self.type_plot = "2D"
            self.plot_xarray_2D(ds, title=title, grid=grid, clear=clear, legend=legend, label=label, replot=replot, **plot_kwargs)
        
        elif len(ds.dims) == 2 :
            self.type_plot = "3D"
            self.plot_xarray_3D(ds, title=title, grid=grid, clear=clear, legend=legend, label=label, replot=replot, **plot_kwargs)
        else :
            raise ValueError("The xarray dataset must have either 1 or 2 dimensions for plotting.")

       




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
  
        self._canvas.draw()





    def update_plot(self):
        """Redraw the canvas to reflect any updates to the plot."""
        
        self.clear_plot()  # Clear the plot before re-plotting with updated data or parameters.

        title = self.open_menu_graphique._title_var.get()

        for index, ds in enumerate(self.list_data_xarray):
            self.plot_xarray(ds, clear=False, replot=True, label= self._line_labels[index], title= title if index == 0 else None, legend=True)


        # Reload the legend menu to update the comboboxes and entries based on the loaded parameters
            # Get the current notebook shown
        current_notebook = self.open_menu_graphique._notebook if hasattr(self.open_menu_graphique, "_notebook") else None
            # If a notebook is currently shown, get its name and reopen the menu with the same notebook shown to update the legend menu display based on the loaded parameters
        if current_notebook is not None:
            notebook_shown = current_notebook.tab(current_notebook.select(), "text")
            self.open_menu_graphique.destroy()  # Close the current menu
            self.open_menu_graphique = Menu_graphique(self, notebook_shown=notebook_shown)  # Reopen the menu with the same notebook shown

    def clear_plot(self):
        """Clear the plot and reset the canvas."""
        if self._colorbar is not None:
            try :
                self._colorbar.remove()
            except:
                pass
            self._colorbar = None

        self.axes.cla()
        self._lines.clear()
        self._canvas.draw()

    def update_cartouche_frame(self):
        """Update the cartouche frame to reflect any changes in the metadata of the plotted lines."""
        for index, line in enumerate(self._lines):
            label_dict = self._line_labels[index]
            self.fill_cartouche_frame(label_to_display=label_dict, line_index=index, line_display=True)

        pass

    def change_orientation_colorbar(self, colorbar, orientation, index = 0) :
        """ Remove the previous colorbar and apply the new one."""
          
        current_font = colorbar.label.get_fontproperties()
        current_label = colorbar.ax.get_ylabel() if orientation == "vertical" else colorbar.ax.get_xlabel()

        # Remove the existing colorbar and create a new one with the new orientation
        try : 
            colorbar.remove()
        except :
            return

        colorbar = self.master.master.figure.colorbar(self._lines[index], ax=self.axes, orientation=orientation)
        if current_label is not None :
            colorbar.set_label(current_label, fontproperties=current_font)

        return colorbar
    
    def apply_font_to_the_colorbar(self, colorbar_axis, current_font, color):
        """ Apply the new font to the colorbar."""
        if colorbar_axis is not None:
            try : 
                colorbar_axis.label.set_fontname(current_font["fontname"])
            except:
                pass
            try : 
                colorbar_axis.label.set_fontsize(current_font["fontsize"])
            except:
                pass
            try : 
                colorbar_axis.label.set_fontstyle(current_font["fontstyle"])
            except:
                pass
            try : 
                colorbar_axis.label.set_fontweight(current_font["fontweight"])
            except:
                pass

            try : 
                if color :
                    colorbar_axis.label.set_color(color)
            except:
                pass

        return colorbar_axis

if __name__ == "__main__":

    def demo() -> None:
        """Demo application for the TkPlotCanvas."""
        root = tk.Tk()
        root.title("Tkinter + Matplotlib Plot Demo")

        #plot_widget = TkPlotCanvas(root, load_view="vue.json")  # Load parameters from a JSON file if it exists
        plot_widget = TkPlotCanvas(root)
        plot_widget.pack(fill="both", expand=True)

        x = list(range(11))
        y = [xi**2 for xi in x]
        
        ds = xr.Dataset(
        data_vars=dict( temperature=("time", y),),
                        coords=dict( time= x),
                        attrs=dict(description="Weather data", units="°C", base="", source="Simulated", history="Created for demo", references="1", comment="First curve"
                    ),
    )

        plot_widget.plot(ds["time"], ds["temperature"], title=ds.attrs["description"], xlabel="time", ylabel="Temperature", label=ds.attrs, legend=True)
        
        y2 = [xi**1.5 for xi in x]
        ds_2 = xr.Dataset(
        data_vars=dict( temperature=("time", y2),),
                        coords=dict( time= x),
                        attrs=dict(description="Weather data", units="°C", base="", source="Simulated", history="Created for demo", references="2", comment="Second curve"
                    ),
    )


        # Add a second curve without clearing the first.
        plot_widget.plot(ds_2["time"], ds_2["temperature"], clear=False, label=ds_2.attrs, legend=True, color="black")
        
        root.mainloop()

    def demo_xarray() -> None:
        """Demo application for the TkPlotCanvas."""
        root = tk.Tk()
        root.title("Tkinter + Matplotlib Plot Demo")

        #plot_widget = TkPlotCanvas(root, load_view="vue.json")  # Load parameters from a JSON file if it exists
        plot_widget = TkPlotCanvas(root, load_view="vue_xarray.json" ) 

        plot_widget.pack(fill="both", expand=True)
        
        x_test = [datetime64("2024-01") + timedelta64(i, "M") for i in range(12)]

        y = [i**2 for i in range(len(x_test))]
        y4 = [i for i in range(len(x_test))]
        ds = xr.Dataset(    data_vars = { "temperature" : (("time"), y, {"units": "°C"}),
                                        "humidity" : (("time"),  y4 ,  {"units": "%"}),
                                        },      
                            coords=dict( time= x_test),
                            attrs=dict(description="Weather data", base="", source="Simulated", history="Created for demo", references="1", comment="First curve") )

        
        y2 = [i**1.5 for i in range(len(x_test))]
        y3 = [i*10 for i in range(len(x_test))]
        ds_2 = xr.Dataset( data_vars = { "temperature" : (("time"), y2, {"units": "°C"}),
                                        "humidity" : (("time"),  y3 ,  {"units": "%"}),
                                        },
                            coords=dict( time= x_test),
                            attrs=dict(description="Weather data", base="", source="Simulated", history="Created for demo", references="2", comment="Second curve") )
        
        y2 = [i for i in range(len(x_test))]
        y3 = [1 for i in range(len(x_test))]
        ds_3 = xr.Dataset( data_vars = { "temperature" : (("time"), y2, {"units": "°C"}),
                                        "humidity" : (("time"),  y3 ,  {"units": "%"}),
                                        },
                            coords=dict( time= x_test),
                            attrs=dict(description="Weather data", base="", source="Simulated", history="Created for demo", references="3", comment="Second curve") )

        plot_widget.plot_xarray(ds, clear=False, title=ds.attrs["description"], label=ds.attrs, legend=True)
        plot_widget.plot_xarray(ds_2, clear=False, label=ds_2.attrs, legend=True)
        plot_widget.plot_xarray(ds_3, clear=False, label=ds_2.attrs, legend=True)
        

        root.mainloop()




    #demo()
    demo_xarray()

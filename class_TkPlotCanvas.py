
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from typing import Optional
from functools import partial

import matplotlib

# Ensure TkAgg is selected before importing backend-specific classes.
matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.font_manager as fm

import xarray as xr
import os
from numpy import datetime64
from numpy import timedelta64
import platform


from vertical_frame import VerticalScrolledFrame
from menu.class_menu_graphique import Menu_graphique


from plot.xarray_plotting import XarrayPlotMixin
from plot.standard_plotting import StandardPlotMixin
from plot.plot_metadata import PlotMetadataMixin
from plot.plot_colorbar_contour import ColorbarContourMixin
from plot.plot_view_parameters import (
    get_3D_parameters as capture_3D_parameters,
    get_current_parameters as capture_current_parameters,
    read_parameters,
    update_variables_from_parameters as restore_plot_variables,
    write_parameters,
)

"""Tkinter plotting widgets with Matplotlib integration.

This module provides a Tkinter-based plotting canvas with embedded
Matplotlib figures, a context menu for customizing axes, curves,
cartouche metadata, and legend settings, and support for saving/loading views.
"""

class TkPlotCanvas(
    ttk.Frame,
    StandardPlotMixin,
    XarrayPlotMixin,
    PlotMetadataMixin,
    ColorbarContourMixin,
):
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
        self.plot_3D_classe = "Auto" 
        self.plot_3D_map = True

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
            self.update_variables_from_parameters(self.parametre_vue)
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
            write_parameters(path_to_save, parameters)
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred while saving the parameters:\n{e}")

    def get_current_parameters(self):
        """Return the current view settings in the persisted JSON format."""
        return capture_current_parameters(self)

    def get_3D_parameters(self, parameters):
        """Add 3D view settings to a parameter dictionary."""
        return capture_3D_parameters(self, parameters)


    def load_parameters(self, *args, path_to_load=None, parameters_to_load = None, reload_plot = False):
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
                parameters = read_parameters(path_to_load)

            except Exception:
                parameters = {}

        # If the parameters are loaded from a file, update the xarray_data attributes accordingly. This ensures that the xarray data settings are restored when loading a saved view.
        if parameters_to_load is None  :
            self.update_variables_from_parameters(parameters)

        if reload_plot :
            self.update_plot()  # Update the plot to reflect any changes in the xarray data settings         

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

        if "xarray_3D" in parameters and parameters.get("plot_type", "2D") == "3D":
            self.apply_3d_parameters(parameters["xarray_3D"])

        self._canvas.draw()

        # If the open_menu_graphique exists, retrieve the title and current notebook to maintain consistency in the plot display.
        if hasattr(self, "open_menu_graphique") and self.open_menu_graphique is not None:
            # Get the current notebook shown
            current_notebook = self.open_menu_graphique._notebook if hasattr(self.open_menu_graphique, "_notebook") else None
            notebook_selected = current_notebook.tab(current_notebook.select(), "text") if current_notebook is not None else ''
        else:
            notebook_selected = ""

        # Reload the legend menu to update the comboboxes and entries based on the loaded parameters
            # If a notebook is currently shown, get its name and reopen the menu with the same notebook shown to update the legend menu display based on the loaded parameters
        if notebook_selected != "":
            self.open_menu_graphique.destroy()  # Close the current menu
            self.open_menu_graphique = Menu_graphique(self, notebook_shown = notebook_selected)  # Reopen the menu with the same notebook shown

    
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

    def update_variables_from_parameters(self, parameters):
        """Restore plot variables that affect subsequent xarray plots."""
        restore_plot_variables(self, parameters)

    def update_plot(self, **kwargs):
        """Redraw the canvas to reflect any updates to the plot."""
        
        self.clear_plot()  # Clear the plot before re-plotting with updated data or parameters.

        # If the open_menu_graphique exists, retrieve the title and current notebook to maintain consistency in the plot display.
        if hasattr(self, "open_menu_graphique") and self.open_menu_graphique is not None:
            # Get the title from the open_menu_graphique if it exists
            title = self.open_menu_graphique._title_var.get() if hasattr(self.open_menu_graphique, "_title_var") else None
            # Get the current notebook shown
            current_notebook = self.open_menu_graphique._notebook if hasattr(self.open_menu_graphique, "_notebook") else None
            notebook_selected = current_notebook.tab(current_notebook.select(), "text") if current_notebook is not None else ''
        else:
            title = None
            notebook_selected = ""

        for index, ds in enumerate(self.list_data_xarray):
            self.plot_xarray(ds, clear=False, replot=True, label= self._line_labels[index], title= title if index == 0 else None, legend=True,  **kwargs)

        # Reload the legend menu to update the comboboxes and entries based on the loaded parameters
            # If a notebook is currently shown, get its name and reopen the menu with the same notebook shown to update the legend menu display based on the loaded parameters
        if notebook_selected != "":
            self.open_menu_graphique.destroy()  # Close the current menu
            self.open_menu_graphique = Menu_graphique(self, notebook_shown = notebook_selected)  # Reopen the menu with the same notebook shown

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

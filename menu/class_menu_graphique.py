import tkinter as tk
from tkinter import ttk
from functools import partial

if __package__ == "menu":
    from vertical_frame import VerticalScrolledFrame
elif __package__:
    from ..vertical_frame import VerticalScrolledFrame

from .menu_axes_settings import AxesSettingsMixin
from .menu_cartouche_settings import CartoucheSettingsMixin
from .menu_curve_settings import CurveSettingsMixin
from .menu_legend_settings import LegendSettingsMixin
from .menu_3d_settings import (
    Graphique3DSettingsMixin,
    Window_colorbar_parameter,
    Window_value_range_parameter,
)

__all__ = [
    "Menu_graphique",
    "Window_colorbar_parameter",
    "Window_value_range_parameter",
]

class Menu_graphique(
    tk.Toplevel,
    AxesSettingsMixin,
    CartoucheSettingsMixin,
    CurveSettingsMixin,
    LegendSettingsMixin,
    Graphique3DSettingsMixin,
):
    """Dialog window to edit plot, curve, cartouche, legend, and 3D settings."""

    def __init__(self, master, notebook_shown=""):
        super().__init__(master)
        self.title("Menu de modification de la courbe")
        self.geometry(f"1000x550+{self.master.master.winfo_x() + 600}+{self.master.master.winfo_y() + 50}")

        self.notebook_shown = notebook_shown

        # Initialize a dictionary to store font controls for axes and title
        self.dict_widget_font =  {"title": None, "xlabel": None, "ylabel": None}

        self.padding_notebook =  (5, 5, 5, 5) # (left, right, top, bottom)
        self.style = ttk.Style(self)

        frame_button = ttk.Frame(self, style='TkPlotCanvas.TFrame')
        frame_button.pack(side="top", fill="x")

        # Button : Save parameters of the plot in a json file
        self._save_button = ttk.Button(frame_button, text="Enregistrer les paramètres", command=self.master.save_parameters, style='TkPlotCanvas.TButton')
        self._save_button.pack(side="right", pady=5, padx=10)

        # Button : Load parameters of the plot from a json file
        self._load_button = ttk.Button(frame_button, text="Charger les paramètres", command= partial(self.master.load_parameters, reload_plot = True), style='TkPlotCanvas.TButton')
        self._load_button.pack(side="right", pady=5, padx=10)

        # Create notebook for organizing controls
        self._notebook = ttk.Notebook(self, style='TkPlotCanvas.TNotebook')
        self._notebook.pack(side="bottom", fill="both", expand=True)

        # Tab Axes et titre:
        self.tab_axes = VerticalScrolledFrame(self._notebook, x_bar = True, style_frame = 'TkPlotCanvas.TFrame')
        self._notebook.add(self.tab_axes, text="Axes et titre", padding=self.padding_notebook)
        self.fill__frame_axes()

        # Tab 3: Cartouche
        self.tab_cartouche = VerticalScrolledFrame(self._notebook, x_bar = True, style_frame = 'TkPlotCanvas.TFrame')
        self._notebook.add(self.tab_cartouche, text="Cartouche", padding=self.padding_notebook)
        self.fill__frame_cartouche_menu()


        if self.master.type_plot == "2D" :
            # Tab 4: Courbe
            self.tab_courbe = VerticalScrolledFrame(self._notebook, x_bar = True, style_frame = 'TkPlotCanvas.TFrame')
            self._notebook.add(self.tab_courbe, text="Courbes", padding=self.padding_notebook)
            self.fill__frame_courbe()

            # Tab 5: Legende
            self.tab_legende = VerticalScrolledFrame(self._notebook, x_bar = True, style_frame = 'TkPlotCanvas.TFrame')

            self._notebook.add(self.tab_legende, text="Légende", padding=self.padding_notebook)
            self.fill__frame_legende()


        elif self.master.type_plot == "3D"  :
            # Tab 4: Courbe
            self.tab_courbe = VerticalScrolledFrame(self._notebook, x_bar = True, style_frame = 'TkPlotCanvas.TFrame')
            self._notebook.add(self.tab_courbe, text="Graphique 3D", padding=self.padding_notebook)
            self.fill__frame_courbe_3D()



        # Show the specified tab on open
        if notebook_shown == "Axes et titre":
            self._notebook.select(self.tab_axes)
        elif notebook_shown == "Cartouche":
            self._notebook.select(self.tab_cartouche)
        elif notebook_shown == "Courbes":
            self._notebook.select(self.tab_courbe)
        elif notebook_shown == "Légende":
            self._notebook.select(self.tab_legende)
        elif notebook_shown == "Graphique 3D":
            self._notebook.select(self.tab_courbe)

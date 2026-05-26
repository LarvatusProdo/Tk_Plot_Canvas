
from cProfile import label
from operator import index
import tkinter as tk
from tkinter import ttk
from typing import Callable, Iterable, Optional
from functools import partial

import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.font_manager as fm
from tkinter import colorchooser
import copy
import json
import xarray as xr
import os
from numpy import datetime64
from numpy import timedelta64

from vertical_frame import VerticalScrolledFrame
"""Tkinter plotting widgets with Matplotlib integration.

This module provides a Tkinter-based plotting canvas with embedded
Matplotlib figures, a context menu for customizing axes, curves,
cartouche metadata, and legend settings, and support for saving/loading views.
"""

class Window_font_parameter(tk.Toplevel):
    """Dialog window to edit font properties for titles, axes, and cartouche labels."""

    def __init__(self, master, frame_to_modifiy=""):
        super().__init__(master)
        self.title(f"Modification du {frame_to_modifiy}")
        self.geometry("400x400+500+100")
        self["bg"] = "#f0f0f0"

        self.frame_window = ttk.Frame(self, style='TkPlotCanvas.TFrame')
        self.frame_window.pack(fill="both", expand=True, anchor="nw")

        self.button_apply = ttk.Button(self.frame_window, text="Appliquer les changement", style='TkPlotCanvas.TButton')

        self.padx_echelle = (5, 5)
        self.pady_echelle = (5, 5)

        self.dict_font_parameters = {}
        if frame_to_modifiy == "cartouche" : 
            label_frame_title = ttk.LabelFrame(self.frame_window, text="Paramètres pour le nom des colonnes :" , style='TkPlotCanvas.TLabelframe')
            label_frame_title.pack(fill="both", side="top", padx=10, pady=10)

            label_frame_line = ttk.LabelFrame(self.frame_window, text="Paramètres pour les lignes :", style='TkPlotCanvas.TLabelframe')
            label_frame_line.pack(fill="both", side="top", padx=10, pady=10)

            self._fill_label_frame(label_frame_title, nom_frame="Cartouche, title")
            self._fill_label_frame(label_frame_line, nom_frame="Cartouche, line")


        elif frame_to_modifiy in ["xlabel", "ylabel"]  : 
            label_frame_title = ttk.LabelFrame(self.frame_window, text="Paramètres du nom de l'axe :", style='TkPlotCanvas.TLabelframe')
            label_frame_title.pack(fill="both", side="top", padx=10, pady=10)
            
            label_frame_line = ttk.LabelFrame(self.frame_window, text="Paramètres de l'échelle :" , style='TkPlotCanvas.TLabelframe')
            label_frame_line.pack(fill="both", side="top", padx=10, pady=10)
            
            self._fill_label_frame(label_frame_title, nom_frame= frame_to_modifiy +", nom")
            self._fill_label_frame(label_frame_line, nom_frame=frame_to_modifiy + ", tick")

            self._set_widget_with_axis_font(frame_to_modifiy, self.master.master.axes )

        elif frame_to_modifiy == "Graphique title" : 
            label_frame_title = ttk.LabelFrame(self.frame_window, text="Paramètres du titre :" , style='TkPlotCanvas.TLabelframe')
            label_frame_title.pack(fill="both", side="top", padx=10, pady=10)
            self._fill_label_frame(label_frame_title, nom_frame= frame_to_modifiy +", nom")

            self._set_widget_with_axis_font(frame_to_modifiy, self.master.master.axes )
        
        self.button_apply.pack(fill="x", side="top", padx=10, pady=10)

    def _fill_label_frame(self, label_frame, nom_frame = ""):
        """Create font control widgets in the provided label frame.

        The widgets include font family, size, style, bold toggle, and a
        color chooser button for the selected frame component.
        """
        
        row_start = 0
        column_start = 0

        ttk.Label(label_frame, text="Police :", style='TkPlotCanvas.TLabel').grid(row=row_start, column=column_start, sticky="e", padx=self.padx_echelle, pady=self.pady_echelle)
        # Filter to only fonts available in both Tkinter and Matplotlib
        matplotlib_fonts = set(fm.FontManager().get_font_names())
        self.list_police = []

        for family in tk.font.families():
            if family in matplotlib_fonts:
                try:
                    tk.font.Font(family=family)
                    self.list_police.append(family)
                except tk.TclError:
                    pass

        combo_police = ttk.Combobox(label_frame, values= self.list_police, state="readonly", width=20)
        combo_police.grid(row=row_start, column=column_start + 1, sticky="w", columnspan=2, padx=5, pady=5)
        index_police = self.list_police.index("Arial") if "Arial" in self.list_police else 0
        combo_police.current(index_police)  # Set to current style of ticks or "normal" by default
        row_start +=1

        ttk.Label(label_frame, text="Taille de la police :", style='TkPlotCanvas.TLabel').grid(row=row_start, column=column_start, sticky="e", padx=self.padx_echelle, pady=self.pady_echelle)
            # Spinbox to choose the size of the ticks on the axis
        spinbox_size_police = ttk.Spinbox(label_frame, from_=0, to=20, increment=1, width=10)
        spinbox_size_police.grid(row=row_start, column=column_start + 1,columnspan=2, sticky="w", padx=5, pady=5)
        spinbox_size_police.delete(0, "end")
        #self.spinbox_size_police_title.insert(0, int(axes_axis.get_ticklabels()[0].get_fontsize()) if axes_axis.get_ticklabels() else 10)  # Set to current size of x ticks or 10 by default
        row_start +=1

        # Combobox to choose the style of the frame
        ttk.Label(label_frame, text="Styles de la police:", style='TkPlotCanvas.TLabel').grid(row=row_start, column=column_start, sticky="e", padx=self.padx_echelle, pady=self.pady_echelle) 
        self.list_style_police = ["normal", "italic", "oblique"]
        combo_style_police = ttk.Combobox(label_frame, values=self.list_style_police, state="readonly", width=10)
        combo_style_police.grid(row=row_start, column=column_start + 1, sticky="w", padx=5, pady=5)
        #index_style = list_style_police.index(label_frame.get_ticklabels()[0].get_fontstyle()) if axes_axis.get_ticklabels() else 0 
        combo_style_police.current(0)  # Set to current style of ticks or "normal" by default
        
         # Checkbutton to choose if frame is bold or not
        var_checkbutton_gras = tk.BooleanVar(value=False)
        checkbutton_bold = ttk.Checkbutton(label_frame, text="Gras", variable= var_checkbutton_gras, style='TkPlotCanvas.TCheckbutton')
        checkbutton_bold.grid(row=row_start, column=column_start + 2, sticky="w", padx=5, pady=5)
        checkbutton_bold.configure(state=["selected"])  # Ensure the checkbutton is not in an indeterminate state
        row_start +=1
        
        # Button to choose the color :
        ttk.Label(label_frame, text="Couleur de la police:", style='TkPlotCanvas.TLabel').grid(row=row_start, column=column_start, sticky="e", padx=self.padx_echelle, pady=self.pady_echelle)
        button_couleur = tk.Button(label_frame, width=3)
        button_couleur.grid(row=row_start, column=column_start + 1, sticky="w", padx=5, pady=5)
        button_couleur.configure(command=partial(self.choisir_couleur_police, button_couleur))
        
        self.dict_font_parameters[nom_frame] = {
            "combo_police" : combo_police,
            "spinbox size police" : spinbox_size_police,
            "combobox style police" : combo_style_police,
            "checkbutton bold" : [checkbutton_bold , var_checkbutton_gras],
            "button_couleur" : button_couleur
        }


    # Fonction pour le cartouche : 
    def _set_widget_frame_cartouche(self, style= "", nom_frame ="" ):
        """Initialize the cartouche font editor controls from an existing ttk style."""
 
        style = self.master.master.style.configure(style)
        style_font = style["font"].split(" ")

        index_police = self.list_police.index(style_font[0]) if style_font[0] in self.list_police else 0    
        self.dict_font_parameters[nom_frame]["combo_police"].current(index_police)
        self.dict_font_parameters[nom_frame]["spinbox size police"].insert(0, int(style_font[1]))
        self.dict_font_parameters[nom_frame]["checkbutton bold"][0].state(["selected"] if style_font[2] == "bold" else ["!selected"])
        self.dict_font_parameters[nom_frame]["checkbutton bold"][1].set( style_font[2] == "bold" )

        if len(style_font) > 3:
            index_police = self.list_style_police.index(int(style_font[0])) if style_font[0] in self.list_style_police else 0
            self.dict_font_parameters[nom_frame][ "combobox style police"].current(index_police)

        self.dict_font_parameters[nom_frame]["button_couleur"].configure(bg=style["foreground"])

    def set_widget_with_cartouch_font(self):
        """Prepare the cartouche font editor and bind the apply button."""
        self.button_apply.configure(command=self._update_cartouch)

        self._set_widget_frame_cartouche(style='Cartouche_titre.TLabel', nom_frame="Cartouche, title")
        self._set_widget_frame_cartouche(style='Cartouche.TLabel', nom_frame="Cartouche, line")
        

    def _update_cartouch(self):
        """Apply the selected cartouche font settings to the ttk styles."""
        police =  self.dict_font_parameters["Cartouche, title"]["combo_police"].get()
        size = self.dict_font_parameters["Cartouche, title"]["spinbox size police"].get()
        bold = "bold" if  self.dict_font_parameters["Cartouche, title"]["checkbutton bold"][1].get() == True else "normal"
        style = self.dict_font_parameters["Cartouche, title"][ "combobox style police"].get()

        if style != "normal":
            self.master.master.style.configure('Cartouche_titre.TLabel', font=(police, int(size), style, bold))
        else :
            self.master.master.style.configure('Cartouche_titre.TLabel', font=(police, int(size), bold))

        bg_button = self.dict_font_parameters["Cartouche, title"]["button_couleur"].cget("bg")
        self.master.master.style.configure('Cartouche_titre.TLabel', foreground = bg_button)

        # Pour le titre : 
        police =  self.dict_font_parameters["Cartouche, line"]["combo_police"].get()
        size = self.dict_font_parameters["Cartouche, line"]["spinbox size police"].get()
        bold = "bold" if  self.dict_font_parameters["Cartouche, line"]["checkbutton bold"][1].get() == True else "normal"
        style = self.dict_font_parameters["Cartouche, line"][ "combobox style police"].get()
        
        if style != "normal":
            self.master.master.style.configure('Cartouche.TLabel', font=(police, int(size), style, bold))
        else :
            self.master.master.style.configure('Cartouche.TLabel', font=(police, int(size), bold))

        bg_button = self.dict_font_parameters["Cartouche, line"]["button_couleur"].cget("bg")
        self.master.master.style.configure('Cartouche.TLabel', foreground = bg_button)

        self.destroy()  # Close the font parameter window after applying changes

    # Fonction pour les axes : 
    def _set_widget_with_axis_font(self, nom_axe, objet_axis):
        """Load the current axis or title font settings into the editor controls."""

        self.button_apply.configure(command=partial(self._update_axis, nom_axe, objet_axis))

        # get current font properties of the axis or title
        if nom_axe == "Graphique title":
            current_font = objet_axis.title.get_fontproperties()
            current_color = objet_axis.title.get_color()
        elif nom_axe == "xlabel":
            current_font = objet_axis.xaxis.label.get_fontproperties()
            current_color = objet_axis.xaxis.label.get_color()    
        elif nom_axe == "ylabel":
            current_font = objet_axis.yaxis.label.get_fontproperties()
            current_color = objet_axis.yaxis.label.get_color()  

        # pour le nom de l'axe : 
        nom_frame = nom_axe+', nom'
            # Get the family name of the current font and set the combobox to that value
        matplotlib_fonts = set(fm.FontManager().get_font_names())
        list_police = []
        for family in tk.font.families():
            if family in matplotlib_fonts:
                try:
                    tk.font.Font(family=family)
                    list_police.append(family)
                except tk.TclError:
                    pass
        index_police = list_police.index(current_font.get_name()) if current_font.get_name() in list_police else 0
        self.dict_font_parameters[nom_frame]["combo_police"].current(index_police)
        self.dict_font_parameters[nom_frame]["combobox style police"].set(current_font.get_style())
        self.dict_font_parameters[nom_frame]["spinbox size police"].insert(0, int(current_font.get_size()))
        self.dict_font_parameters[nom_frame]["checkbutton bold"][0].state(["selected"] if current_font.get_weight() == "bold" else ["!selected"])
        self.dict_font_parameters[nom_frame]["checkbutton bold"][1].set( current_font.get_weight() == "bold" )

        self.dict_font_parameters[nom_frame]["button_couleur"].configure(bg=current_color)

        if nom_axe in ["xlabel", "ylabel"]  : 
            if nom_axe == "xlabel":
                axe = objet_axis.xaxis
            else : 
                axe = objet_axis.yaxis

            # pour l'axe tick : 
            nom_frame = nom_axe+', tick'
            index_police = list_police.index(axe.get_ticklabels()[0].get_fontname()) if axe.get_ticklabels()[0].get_fontname() in list_police else 0
            self.dict_font_parameters[nom_frame]["combo_police"].current(index_police)
            index_style = self.list_style_police.index(axe.get_ticklabels()[0].get_fontstyle()) if axe.get_ticklabels() else 0 
            self.dict_font_parameters[nom_frame]["combobox style police"].current(index_style)  # Set to current style of ticks or "normal" by default
            self.dict_font_parameters[nom_frame]["spinbox size police"].insert(0, int(axe.get_ticklabels()[0].get_fontsize()) if axe.get_ticklabels() else 10)  # Set to current size of x ticks or 10 by default
            self.dict_font_parameters[nom_frame]["checkbutton bold"][0].state(["selected"] if axe.get_ticklabels()[0].get_fontweight() else ["!selected"])
            self.dict_font_parameters[nom_frame]["checkbutton bold"][1].set( axe.get_ticklabels()[0].get_fontweight() == "bold" )

            self.dict_font_parameters[nom_frame]["button_couleur"].configure(bg=axe.get_ticklabels()[0].get_color() if axe.get_ticklabels() else "#000000")

    def _update_axis(self, nom_axe, objet_axis):
        """Apply axis or title font settings selected in the dialog to the Matplotlib axis."""

        nom_frame = nom_axe+', nom'
        # Pour le titre : 
        police =  self.dict_font_parameters[nom_frame]["combo_police"].get()
        size = self.dict_font_parameters[nom_frame]["spinbox size police"].get()
        weight = "bold" if  self.dict_font_parameters[nom_frame]["checkbutton bold"][1].get() == True else "normal"
        style = self.dict_font_parameters[nom_frame][ "combobox style police"].get()
        color = self.dict_font_parameters[nom_frame]["button_couleur"].cget("bg")

        # Apply the changes to the axes and title based on the user input in the entries and font controls.
        if nom_axe == "Graphique title":
            objet_axis.set_title(self.master._title_var.get(), fontfamily= police, fontsize=size, fontstyle=style, fontweight=weight, color=color)
        else : 
            # pour l'axe tick : 
            nom_frame = nom_axe+', tick'
            police_tick =  self.dict_font_parameters[nom_frame]["combo_police"].get()
            size_tick = self.dict_font_parameters[nom_frame]["spinbox size police"].get()
            weight_tick = "bold" if  self.dict_font_parameters[nom_frame]["checkbutton bold"][1].get() == True else "normal"
            style_tick = self.dict_font_parameters[nom_frame][ "combobox style police"].get()
            color_tick = self.dict_font_parameters[nom_frame]["button_couleur"].cget("bg")

            if nom_axe == "xlabel":
                objet_axis.set_xlabel(self.master._xlabel_var.get(), fontfamily= police, fontsize=size, fontstyle=style, fontweight=weight, color=color)
                axe = objet_axis.xaxis
                for tick in axe.get_ticklabels():
                    tick.set_fontname(police_tick)
                    tick.set_fontsize(size_tick)
                    tick.set_fontstyle(style_tick)
                    tick.set_fontweight(weight_tick)
                    tick.set_color(color_tick)

            elif nom_axe == "ylabel":
                objet_axis.set_ylabel(self.master._ylabel_var.get(), fontfamily= police, fontsize=size, fontstyle=style, fontweight=weight, color=color)
                axe = objet_axis.yaxis
                for tick in axe.get_ticklabels():
                    tick.set_fontname(police_tick)
                    tick.set_fontsize(size_tick)
                    tick.set_fontstyle(style_tick)
                    tick.set_fontweight(weight_tick)
                    tick.set_color(color_tick)
    
        self.master.master._canvas.draw()

        self.destroy()  # Close the font parameter window after applying changes


    def choisir_couleur_police(self, widget):
        """Open a color chooser and update the font color button background."""
        color_code = colorchooser.askcolor(master = self ,title="Choisir une couleur de police")
        if color_code:
            # Update the color button background
           widget.configure(bg=color_code[1])  # Update button color

class Menu_graphique(tk.Toplevel):
    """Dialog window to edit plot, curve, cartouche, and legend settings."""

    def __init__(self, master, notebook_shown=""):
        super().__init__(master)
        self.title("Menu de modification de la courbe")
        self.geometry("1000x500+600+100")
        self["bg"] = "#f0f0f0"

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
        self._load_button = ttk.Button(frame_button, text="Charger les paramètres", command=self.master.load_parameters, style='TkPlotCanvas.TButton')
        self._load_button.pack(side="right", pady=5, padx=10)

        # Create notebook for organizing controls
        self._notebook = ttk.Notebook(self, style='TkPlotCanvas.TNotebook')
        self._notebook.pack(side="bottom", fill="both", expand=True)

        # Tab Axes et titre:
        self.tab_axes = VerticalScrolledFrame(self._notebook, x_bar = True, bg_canvas ="", style_frame = 'TkPlotCanvas.TFrame')
        self._notebook.add(self.tab_axes, text="Axes et titre", padding=self.padding_notebook)
        self.fill__frame_axes()
        
        # Tab 3: Cartouche
        self.tab_cartouche = VerticalScrolledFrame(self._notebook, x_bar = True, bg_canvas ="", style_frame = 'TkPlotCanvas.TFrame')
        self._notebook.add(self.tab_cartouche, text="Cartouche", padding=self.padding_notebook)
        self.fill__frame_cartouche_menu()

        # Tab 4: Courbe
        self.tab_courbe = VerticalScrolledFrame(self._notebook, x_bar = True, bg_canvas ="", style_frame = 'TkPlotCanvas.TFrame')
        self._notebook.add(self.tab_courbe, text="Courbes", padding=self.padding_notebook)
        self.fill__frame_courbe()

        # Tab 5: Legende
        self.tab_legende = VerticalScrolledFrame(self._notebook, x_bar = True, bg_canvas ="", style_frame = 'TkPlotCanvas.TFrame')
        
        self._notebook.add(self.tab_legende, text="Légende", padding=self.padding_notebook)
        self.fill__frame_legende()

        # Show the specified tab on open
        if notebook_shown == "Axes et titre":
            self._notebook.select(self.tab_axes)
        elif notebook_shown == "Cartouche":
            self._notebook.select(self.tab_cartouche)
        elif notebook_shown == "Courbes":
            self._notebook.select(self.tab_courbe)
        elif notebook_shown == "Légende":
            self._notebook.select(self.tab_legende)


    def fill__frame_cartouche_menu(self):
        """Create the cartouche configuration tab with metadata selection controls."""
        label = ttk.Label(self.tab_cartouche, text="Paramètres du cartouche:", style='TkPlotCanvas.Titre_parammetre.TLabel')
        label.grid(row=0, column=0, sticky="w", padx=5, pady=10, columnspan=3 )

        # Checkbutton pour l'affichage du cartouche : 
        self.Is_cartouche_display_var = tk.BooleanVar(value= self.master.Is_cartouche_display ) #TODO : value to apply
        checkbutton_cartouche_shown = ttk.Checkbutton(self.tab_cartouche, 
                                                            text = "Affichage du cartouche",
                                                            variable=self.Is_cartouche_display_var,
                                                            style='TkPlotCanvas.TCheckbutton',
                                                            command= self.show_hide_cartouche)
        checkbutton_cartouche_shown.grid(row=0, column=3, sticky="w", padx=5, pady=10, columnspan=1 )
        checkbutton_cartouche_shown.configure(state=["selected"])
        
        # Bonton pour moodifier font du cartouche : 
        button_modify_font = ttk.Button(self.tab_cartouche, text="Paramètres du cartouche:", 
                                        command=self._cartouch_show_font_parameters, style='TkPlotCanvas.TButton' )
        button_modify_font.grid(row=0, column=4, sticky="w", padx=5, pady=10, columnspan=2 )
        # 
        initialize_cartouche_frame = True

        # Choice of metadata to display in the cartouche
        self.list_combobox_cartouche = []
        self.list_entry_cartouche = [[] for _ in self.master._lines]  # To store entry widgets for each line and key
        for index, line in enumerate(self.master._lines):
            label = line.get_label()
            label_dict = self.master._line_labels[index]
            column_index = 1
            if initialize_cartouche_frame :
                for key in label_dict:
                    ttk.Label(self.tab_cartouche, text="Indice", style='Titre_parammetre.TLabel').grid(row=1, column=0, sticky="w", padx=5, pady=5)
                    if not any(key == combo['values'] for combo in self.list_combobox_cartouche):
                        list_values_combo = [""] + list(label_dict.keys())
                        
                        combobox = ttk.Combobox(self.tab_cartouche, values=list_values_combo, state="readonly", width=15)
                        combobox.grid(row=1, column=column_index, padx=5, pady=5)

                        # Set the combobox to the current key if it exists in the cartouche title grid, otherwise set to ""
                        key_to_show = self.master._cartouche_title_grid[column_index-1].cget("text") if column_index-1 < len(self.master._cartouche_title_grid) else "None"
                        index_key = list_values_combo.index(key_to_show) if key_to_show in list_values_combo else 0
                        combobox.current(index_key)  # Set to "None" by default

                        # bind the combobox selection event to update the cartouche display
                        combobox.bind("<<ComboboxSelected>>", partial(self._on_cartouche_update, combo_selected=combobox, column_index=column_index-1))
                        self.list_combobox_cartouche.append(combobox)

                    else:
                        # If the key already has a combobox, just add an empty one for this line
                        combobox = ttk.Combobox(self.tab_cartouche, values=["None"], state="readonly", width=15)
                        combobox.grid(row=1, column=column_index, padx=5, pady=5)
                        combobox.current(0)  # Set to "None" by default
                    column_index += 1
                
                initialize_cartouche_frame = False
                column_index = 1

            ttk.Label(self.tab_cartouche, text=str(index+1), style='Titre_parammetre.TLabel').grid(row=index+2, column=0, sticky="e", padx=5, pady=5)
           
            for combobox in self.list_combobox_cartouche:
                key_to_show = combobox.get()
                entry_key = ttk.Entry(self.tab_cartouche, width=15, style='TkPlotCanvas.TEntry')
                entry_key.bind('<KeyRelease>', partial(self._on_entry_cartouche_update, line_index=index, column_index=column_index-1))
                entry_key.grid(row=index+2, column=column_index, sticky="w", padx=5, pady=5)
                self.list_entry_cartouche[index].append(entry_key)
                column_index += 1
                if key_to_show in label_dict:
                    entry_key.insert(0,label_dict[key_to_show])

    def _on_entry_cartouche_update(self, event, line_index=None, column_index=None):
        """Update the cartouche metadata value for the selected line and column."""
        entry_widget = event.widget
        new_value = entry_widget.get()
        key_selected = self.list_combobox_cartouche[column_index].get()
        if key_selected and line_index is not None and column_index is not None:
            # Update the label dict for the line with the new value
            self.master._line_labels[line_index][key_selected] = new_value
            
            # Update the cartouche display for this line and key
            try:
                self.master._cartouche_grid[line_index][column_index+1].destroy()  # Remove the old label if it exists
            except Exception:                
                pass
            
            self.master._cartouche_grid[line_index][column_index+1] = ttk.Label(self.master._cartouche_frame, text=str(new_value), style="Cartouche.TLabel")
            self.master._cartouche_grid[line_index][column_index+1].grid(row=line_index + 1, column=column_index+1, sticky="w", padx=5, pady=5)


    def _on_cartouche_update(self, event, combo_selected=None, column_index=None):
        """Refresh the cartouche headers and values when a metadata key is selected."""
        
        key_selected = combo_selected.get()
        # Update the cartouche display based on the selected metadata keys and values.
        try:
            self.master._cartouche_title_grid[column_index].destroy()  # Remove the old label if it exists
        except Exception:                
            pass
            # Update the title of the cartouche column
        
        while len(self.master._cartouche_title_grid) < column_index+1 :
            self.master._cartouche_title_grid.append(ttk.Label(self.master._cartouche_frame, text="", style='Cartouche_titre.TLabel'))
        
        self.master._cartouche_title_grid[column_index] = ttk.Label(self.master._cartouche_frame, text=key_selected, style='Cartouche_titre.TLabel')
        self.master._cartouche_title_grid[column_index].grid(row=0, column=column_index+1, sticky="w", padx=5, pady=5)

            # Update the values in the cartouche for each line based on the selected key in the combobox
        for index, line in enumerate(self.master._lines):
            label_dict = self.master._line_labels[index]
            
            try :   
                self.master._cartouche_grid[index][column_index+1].destroy()  # Remove the old label if it exists
            except Exception:                
                pass
            
            if key_selected in label_dict:
                value = label_dict[key_selected]
            else :
                value = "" 

            while len(self.master._cartouche_grid[index]) < column_index+2 :
                self.master._cartouche_grid[index].append(ttk.Label(self.master._cartouche_frame, text="", style='Cartouche_titre.TLabel'))

            self.master._cartouche_grid[index][column_index+1] = ttk.Label(self.master._cartouche_frame, text=str(value), style="Cartouche.TLabel")
            self.master._cartouche_grid[index][column_index+1].grid(row=index + 1, column=column_index+1, sticky="w", padx=5, pady=5)

        # Update the entry on the cartouche frame for each line based on the selected key in the combobox
        for index, line in enumerate(self.master._lines):
            label_dict = self.master._line_labels[index]
            if key_selected in label_dict:
                value = label_dict[key_selected]
                if len(self.list_entry_cartouche[index]) > 0:
                    entry_widget = self.list_entry_cartouche[index][column_index]  
                    entry_widget.delete(0, tk.END)
                    entry_widget.insert(0, str(value))
            else:
                if len(self.list_entry_cartouche[index]) > 0:
                    entry_widget = self.list_entry_cartouche[index][column_index] 
                    entry_widget.delete(0, tk.END)
                    entry_widget.insert(0, "")


    def _cartouch_show_font_parameters(self):
        font_cartouch = Window_font_parameter(self, frame_to_modifiy="cartouche")
        font_cartouch.set_widget_with_cartouch_font()
    
    def show_hide_cartouche(self):
        
        if not self.Is_cartouche_display_var.get() == True : 
            self.master.panedwindow.forget(self.master._cartouche_frame)
            self.Is_cartouche_display_var.set( False ) 
            self.master.Is_cartouche_display = False    
        else :
            self.master.panedwindow.add(self.master._cartouche_frame, weight=0)
            self.Is_cartouche_display_var.set(True)
            self.master.Is_cartouche_display = True
        

    def fill__frame_courbe(self):
        """Create the curve properties tab and populate it with widgets for each plotted line."""
        
        self.style.configure('Courbe.TLabel', font=('Arial', 10, 'bold'), background = self.master.bg_color)

        label = ttk.Label(self.tab_courbe, text="Paramètres des courbes:", style='Courbe.TLabel')
        label.grid(row=0, column=0, sticky="w", padx=5, pady=10, columnspan=6 )

        label = ttk.Label(self.tab_courbe, text="Couleur:", style='Courbe.TLabel').grid(row=1, column=0, sticky="w", padx=5, pady=5)
        label = ttk.Label(self.tab_courbe, text="Épaisseur de ligne:", style='Courbe.TLabel').grid(row=1, column=1, sticky="w", padx=5, pady=5)
        label = ttk.Label(self.tab_courbe, text="Style de ligne:", style='Courbe.TLabel').grid(row=1, column=2, sticky="w", padx=5, pady=5)
        label = ttk.Label(self.tab_courbe, text="Marqueur:", style='Courbe.TLabel').grid(row=1, column=3, sticky="w", padx=5, pady=5)
        label = ttk.Label(self.tab_courbe, text="Taille du marqueur:", style='Courbe.TLabel').grid(row=1, column=4, sticky="w", padx=5, pady=5)

        self.list_widget = []
        for index, line in enumerate(self.master._lines):
           self.affiche_parametres_courbe(line, index,self.list_widget)
        # Add controls for curve properties here
        pass
    
    def affiche_parametres_courbe(self, line, index, list_widget):
        """Display editable properties for a specific curve and store the widgets."""
        
        
        label = line.get_label()
        color = line.get_color()
        linestyle = line.get_linestyle()
        linewidth = line.get_linewidth()
        marker = line.get_marker()
        markersize = line.get_markersize()

        button_color = tk.Button(self.tab_courbe, bg=color, command=partial(self.choisir_couleur, index), width=5)
        button_color.grid(row=index+2, column=0, padx=5, pady=5)

        spinbox_linewidth = ttk.Spinbox(self.tab_courbe, from_=0.5, to=10.0, increment=0.5, width=5, command=partial(self.update_line_property, 'linewidth', index=index))
        spinbox_linewidth.grid(row=index+2, column=1, padx=5, pady=5)
        spinbox_linewidth.set(linewidth)
        
        combobox_linestyle = ttk.Combobox(self.tab_courbe, values=["-", "--", "-.", "None"], state="readonly", width=8)
        combobox_linestyle.grid(row=index+2, column=2, padx=5, pady=5)
        combobox_linestyle.current(combobox_linestyle['values'].index(linestyle))
        combobox_linestyle.bind("<<ComboboxSelected>>", partial(self.update_line_property, 'linestyle', index=index))

        combobox_marker = ttk.Combobox(self.tab_courbe, values=["o", "s", "^", "x", "None"], state="readonly", width=8)
        combobox_marker.grid(row=index+2, column=3, padx=5, pady=5)
        combobox_marker.current(combobox_marker['values'].index(marker))
        combobox_marker.bind("<<ComboboxSelected>>", partial(self.update_line_property, 'marker', index=index))

        
        spinbox_markersize = ttk.Spinbox(self.tab_courbe, from_=1, to=20, increment=1, width=5, command=partial(self.update_line_property, 'markersize', index=index))
        spinbox_markersize.grid(row=index+2, column=4, padx=5, pady=5)
        spinbox_markersize.set(markersize)
   
        list_widget.append([button_color, spinbox_linewidth, combobox_linestyle, combobox_marker, spinbox_markersize])


    def choisir_couleur(self, index):
        """Open a color chooser to select a new curve color and update the plot."""
        color_code = colorchooser.askcolor(parent= self, title="Choisir une couleur")
        
        if color_code and color_code[1]:  # Check if a color was selected (colorchooser returns (None, None) if cancelled)
            self.master._lines[index].set_color(color_code[1])
            
            # Update the legend to reflect the new color if the line has a label and legend is displayed
            if self.master.Is_legend_display and self.master._lines[index].get_label() != "_nolegend_":
                self.master.axes.legend(draggable=True)  # Update the legend to reflect the new color
            
            self.master._canvas.draw()  # Redraw the canvas after color and legend update

            # Update the button color to reflect the new line color
            self.list_widget[index][0].configure(bg=color_code[1])

            # Update the cartouche color for this line 
            self.master._cartouche_grid[index][0].configure(foreground =color_code[1])


    def update_line_property(self, property_name, event=None, index=None):
        """
        Update the line property based on the user input in the corresponding widget.
         property_name: The name of the line property to update (e.g., 'linewidth', 'linestyle', 'marker', 'markersize').
         event: The event object from the widget (if applicable).
         index: The index of the line to update.
        """
        value_linestyle = self.list_widget[index][2].get()
        value_marker = self.list_widget[index][3].get()

        if property_name == 'linewidth':
            value_linewidth = self.list_widget[index][1].get()
            self.master._lines[index].set_linewidth(float(value_linewidth))
        elif property_name == 'linestyle':
            # Update the line style based on the selected value in the combobox
            self.master._lines[index].set_linestyle(value_linestyle)
            
        elif property_name == 'marker':
            value_marker = self.list_widget[index][3].get()
            self.master._lines[index].set_marker(value_marker)
        elif property_name == 'markersize':
            value_markersize = self.list_widget[index][4].get()
            self.master._lines[index].set_markersize(float(value_markersize))

        self.master._canvas.draw()

        # Update the cartouch :
        if value_linestyle != "None" or  value_linestyle != "None":
            if value_linestyle == '-':
                value_linestyle = "―"
            color = self.master._lines[index].get_color()
            
            line_string = f"{value_linestyle}" if value_linestyle != "None" else ""
            line_string += f"{value_marker}" if value_marker != "None" else ""

            self.master._cartouche_grid[index][0].configure(text=line_string, background=self.master.bg_color, foreground=color, width=3, font=("Helvetica", 15, 'bold'))
           


    def fill__frame_axes(self):
        """Create the axes and title configuration tab with controls for labels, limits, and scale."""
        
        ttk.Label(self.tab_axes, text="Modification des axes et titres:", style='Titre_parammetre.TLabel').grid(row=0, column=0, sticky="w", padx=5, pady=10, columnspan=2)

        # Add controls for axes and title here
        padx_axes = (5, 5)
        pady_axes = (5, 5)


        # Frame for title : 
        frame_title = ttk.LabelFrame(self.tab_axes, text="Titre", padding=(10, 10), style='TkPlotCanvas.TLabelframe')
        frame_title.grid(row=1, column=0, columnspan=4, sticky="we", padx=padx_axes, pady=pady_axes)

        ttk.Label(frame_title, text="Titre:", style='TkPlotCanvas.TLabel').grid(row=1, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        self._title_var = tk.StringVar(value="")
        self._title_entry = ttk.Entry(frame_title, textvariable=self._title_var, width=50, style='TkPlotCanvas.TEntry')
        self._title_entry.grid(row=1, column=1, padx=(0, 4), sticky="w")
        self._title_var.set(self.master.axes.get_title())
        button_font_title = ttk.Button(frame_title, text="Modifier la police", 
                            command= partial(Window_font_parameter, self, frame_to_modifiy="Graphique title"), style='TkPlotCanvas.TButton' )
        button_font_title.grid(row=1, column=2, padx=(10, 5), sticky="ew")

        # frame for X axis : 
        fame_x_axis = ttk.LabelFrame(self.tab_axes, text="Axe X", padding=(10, 10), style='TkPlotCanvas.TLabelframe')
        fame_x_axis.grid(row=2, column=0, columnspan=2, sticky="we", padx=padx_axes, pady=pady_axes)
        ttk.Label(fame_x_axis, text="Abscisse:", style='TkPlotCanvas.TLabel').grid(row=1, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        self._xlabel_var = tk.StringVar(value="")
        self._xlabel_entry = ttk.Entry(fame_x_axis, textvariable=self._xlabel_var, width=25, style='TkPlotCanvas.TEntry')
        self._xlabel_entry.grid(row=1, column=1, columnspan=2, padx=(0, 4), sticky="w")
        self._xlabel_var.set(self.master.axes.get_xlabel())
        
        ttk.Separator(fame_x_axis, orient='horizontal').grid(row=5, column=0, columnspan=3, sticky="we", pady=(10, 10))

            # Modifier les axes : 
        ttk.Label(fame_x_axis, text="Valeur min:", style='TkPlotCanvas.TLabel').grid(row=6, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        ttk.Label(fame_x_axis, text="Valeur max:", style='TkPlotCanvas.TLabel').grid(row=7, column=0, sticky="e", padx=padx_axes, pady=pady_axes)

        self._xlim_min_var = tk.StringVar(value= self.master.axes.get_xlim()[0].round(4) )
        entry_x_min = ttk.Entry(fame_x_axis, textvariable=self._xlim_min_var, width=15, style='TkPlotCanvas.TEntry')
        entry_x_min.grid(row=6, column=1, sticky="we")
        entry_x_min.bind('<KeyRelease>', lambda event: self.set_autoscale_false(axis="x"))  # Set autoscale to False when user types in the entry
        entry_x_min.bind("<Return>", lambda event: self._apply_axes_changes())  # Apply changes when Enter is pressed

        self._xlim_max_var = tk.StringVar(value= self.master.axes.get_xlim()[1].round(4) )
        entry_x_max = ttk.Entry(fame_x_axis, textvariable=self._xlim_max_var, width=15, style='TkPlotCanvas.TEntry')
        entry_x_max.grid(row=7, column=1, sticky="we")  
        entry_x_max.bind('<KeyRelease>', lambda event: self.set_autoscale_false(axis="x"))  # Set autoscale to False when user types in the entry
        entry_x_max.bind("<Return>", lambda event: self._apply_axes_changes())  # Apply changes when Enter is pressed
        

        ttk.Label(fame_x_axis, text="Echelle:", style='TkPlotCanvas.TLabel').grid(row=8, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        self._xscale_var = tk.StringVar(value="linear")
        ttk.Combobox(fame_x_axis, textvariable=self._xscale_var, values=["linear", "log"], state="readonly", width=8).grid(row=8, column=1, columnspan=2, sticky="we")
        
        self.auto_scale_var_x = tk.BooleanVar(value= self.master.axes.get_autoscalex_on() )
        checkbutton_autoscale_x = ttk.Checkbutton(fame_x_axis, text="Auto", variable = self.auto_scale_var_x, command= partial(self._on_zoom_auto, axis ="x"), width=5, style='TkPlotCanvas.TCheckbutton')
        checkbutton_autoscale_x.grid(row=6,column=2, rowspan=2, padx=padx_axes, pady=pady_axes, sticky="we")
        
        
        ttk.Separator(fame_x_axis, orient='horizontal').grid(row=9, column=0, columnspan=3, sticky="we", pady=(10, 10))

            # Bouton police : 
        button_font_xlabel = ttk.Button(fame_x_axis, text="Modifier la police", 
                            command= partial(Window_font_parameter, self, frame_to_modifiy="xlabel"), style='TkPlotCanvas.TButton' )
        button_font_xlabel.grid(row=10, column=0, columnspan=3, padx=(5, 5), sticky="ew")

        # frame for Y axis : 
        fame_y_axis = ttk.LabelFrame(self.tab_axes, text="Axe Y", padding=(10, 10), style='TkPlotCanvas.TLabelframe')
        fame_y_axis.grid(row=2, column=2, columnspan=2, sticky="we", padx=padx_axes, pady=pady_axes)
        ttk.Label(fame_y_axis, text="Ordonnée:", style='TkPlotCanvas.TLabel').grid(row=1, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        self._ylabel_var = tk.StringVar(value="")
        self._ylabel_entry = ttk.Entry(fame_y_axis, textvariable=self._ylabel_var, width=25, style='TkPlotCanvas.TEntry')
        self._ylabel_entry.grid(row=1, column=1, columnspan=2, padx=(0, 4), sticky="w")
        self._ylabel_var.set(self.master.axes.get_ylabel())

        ttk.Separator(fame_y_axis, orient='horizontal').grid(row=5, column=0, columnspan=3, sticky="we", pady=(10, 10))
         # Modifier les axes : 
        ttk.Label(fame_y_axis, text="Valeur min:", style='TkPlotCanvas.TLabel').grid(row=6, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        ttk.Label(fame_y_axis, text="Valeur max:", style='TkPlotCanvas.TLabel').grid(row=7, column=0, sticky="e", padx=padx_axes, pady=pady_axes)

        self._ylim_min_var = tk.StringVar(value= self.master.axes.get_ylim()[0].round(4) )
        entry_y_min = ttk.Entry(fame_y_axis, textvariable=self._ylim_min_var, width=15, style='TkPlotCanvas.TEntry')
        entry_y_min.grid(row=6, column=1, sticky="we")
        entry_y_min.bind('<KeyRelease>', lambda event: self.set_autoscale_false(axis="y"))  # Set autoscale to False when user types in the entry
        entry_y_min.bind("<Return>", lambda event: self._apply_axes_changes())  # Apply changes when Enter is pressed

        self._ylim_max_var = tk.StringVar(value= self.master.axes.get_ylim()[1].round(4) )
        entry_y_max = ttk.Entry(fame_y_axis, textvariable=self._ylim_max_var, width=15, style='TkPlotCanvas.TEntry')
        entry_y_max.grid(row=7, column=1, sticky="we")
        entry_y_max.bind('<KeyRelease>', lambda event: self.set_autoscale_false(axis="y"))  # Set autoscale to False when user types in the entry
        entry_y_max.bind("<Return>", lambda event: self._apply_axes_changes())  # Apply changes when Enter is pressed   

        self.auto_scale_var_y = tk.BooleanVar(value = self.master.axes.get_autoscaley_on() )
        checkbutton_autoscale_y = ttk.Checkbutton(fame_y_axis, text="Auto", variable = self.auto_scale_var_y, command=partial(self._on_zoom_auto, axis="y"), width=5, style='TkPlotCanvas.TCheckbutton')
        checkbutton_autoscale_y.grid(row=6,column=2, rowspan=2, padx=padx_axes, pady=pady_axes, sticky="we")


        ttk.Label(fame_y_axis, text="Echelle:", style='TkPlotCanvas.TLabel').grid(row=8, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        self._yscale_var = tk.StringVar(value="linear")
        ttk.Combobox(fame_y_axis, textvariable=self._yscale_var, values=["linear", "log"], state="readonly", width=8).grid(row=8, column=1, columnspan=2, sticky="we")

        ttk.Separator(fame_y_axis, orient='horizontal').grid(row=9, column=0, columnspan=3, sticky="we", pady=(10, 10))

        # Bouton police :
        button_font_ylabel = ttk.Button(fame_y_axis, text="Modifier la police", 
                            command= partial(Window_font_parameter, self, frame_to_modifiy="ylabel"), style='TkPlotCanvas.TButton' )
        button_font_ylabel.grid(row=10, column=0, columnspan=3, padx=(5, 5), sticky="ew")

        # Apply button to update axes and title:
        ttk.Button(self.tab_axes, text="Appliquer les changements", command=self._apply_axes_changes, width=20, style='TkPlotCanvas.TButton').grid(row=0, column=2, columnspan=2, padx=padx_axes, pady=pady_axes, sticky="we")

        if len(self.master.list_data_xarray) > 0 :
            list_dimension = list(self.master.list_data_xarray[0].dims)
            list_variable = list(self.master.list_data_xarray[0].data_vars)
            list_to_show = list_dimension + ["---------"] + list_variable
            ttk.Label(fame_x_axis, text="Variable:", style='TkPlotCanvas.TLabel').grid(row=2, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
            ttk.Label(fame_y_axis, text="Variable:", style='TkPlotCanvas.TLabel').grid(row=2, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
            self.list_combobox_variable_x = ttk.Combobox(fame_x_axis, values= list_to_show, state="readonly", width=20, style='Combobox_variable.TCombobox')
            self.list_combobox_variable_x.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="we")
            index = list_to_show.index(self.master.xarray_data["dimension"]) if self.master.xarray_data["dimension"] in list_to_show else 0
            self.list_combobox_variable_x.current(index)  # Set to the first dimension by default

            self.list_combobox_variable_y = ttk.Combobox(fame_y_axis, values= list_to_show, state="readonly", width=20, style='Combobox_variable.TCombobox')
            self.list_combobox_variable_y.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="we")
            index = list_to_show.index(self.master.xarray_data["variable"]) if self.master.xarray_data["variable"] in list_to_show else 0
            self.list_combobox_variable_y.current(index)  # Set to the first dimension by default

    def set_autoscale_false(self, event=None, axis=""):
        """Set the autoscale checkboxes to False when the user manually changes axis limits."""
        if axis == "x":
            self.auto_scale_var_x.set(False)
        elif axis == "y":
            self.auto_scale_var_y.set(False)

    def _apply_axes_changes(self):
        """Apply the axes, title, and xarray selection changes from the axes tab."""
  
        current_font = self.master.axes.title.get_fontproperties()
        current_color = self.master.axes.title.get_color()
        self.master.axes.set_title(self._title_var.get(), fontfamily=current_font.get_name(), fontsize=current_font.get_size(), fontstyle=current_font.get_style(), fontweight=current_font.get_weight(), color=current_color)
        self.master.axes.set_xlabel(self._xlabel_var.get())
        self.master.axes.set_ylabel(self._ylabel_var.get())
        
        # if list_data_xarray is not empty, update the x and y variables based on the combobox selection
        if len(self.master.list_data_xarray) > 0 :
            # Show the variable selected from comboboxes if they are not already shown
                # Get the selected variable from the comboboxes
            selected_variable_x = self.list_combobox_variable_x.get()
            selected_variable_y = self.list_combobox_variable_y.get()   
            list_variable = list(self.master.list_data_xarray[0].data_vars) + list(self.master.list_data_xarray[0].dims)
            Is_variable_modified = False
                # Update the master variables with the selected variables
            if selected_variable_x != self.master.xarray_data["dimension"] and selected_variable_x in list_variable:
                Is_variable_modified = True
                self.master.xarray_data["dimension"] = selected_variable_x
            if selected_variable_y != self.master.xarray_data["variable"] and selected_variable_y in list_variable:
                Is_variable_modified = True
                self.master.xarray_data["variable"] = selected_variable_y   

            if Is_variable_modified:
                # Save the current parameter_vue : 
                self.master.parametre_vue = self.master.get_current_parameters()

                # Update the plot to reflect the variable change   
                self.master.update_plot()           


        # Mise à jour de l'échelle : 
        # Get the new axis limits and scale types from the entries and comboboxes, and apply them to the plot.
        try:
            x_min = float(self._xlim_min_var.get()) if self._xlim_min_var.get() else None
            x_max = float(self._xlim_max_var.get()) if self._xlim_max_var.get() else None
            y_min = float(self._ylim_min_var.get()) if self._ylim_min_var.get() else None
            y_max = float(self._ylim_max_var.get()) if self._ylim_max_var.get() else None

            if x_min is not None and x_max is not None:
                self.master.axes.set_xlim(x_min, x_max)
            elif x_min is not None:
                self.master.axes.set_xlim(left=x_min)
            elif x_max is not None:
                self.master.axes.set_xlim(right=x_max)

            if y_min is not None and y_max is not None:
                self.master.axes.set_ylim(y_min, y_max)
            elif y_min is not None:
                self.master.axes.set_ylim(bottom=y_min)
            elif y_max is not None:
                self.master.axes.set_ylim(top=y_max)

            # Update scale types
            if not self.master.Is_Date_on_x_axis : 
                self.master.axes.set_xscale(self._xscale_var.get())
            self.master.axes.set_yscale(self._yscale_var.get())
            
        except ValueError:
            tk.messagebox.showerror("Invalid input", "Please enter valid numeric values for axis limits.")

        # Update the autoscale settings based on the checkboxes
        if self.auto_scale_var_x.get() :
            self.master.axes.autoscale(axis="x", tight=True)
        if self.auto_scale_var_y.get() :
            self.master.axes.autoscale(axis="y", tight=True)

        self.master._canvas.draw()
    
    def _on_zoom_auto(self, axis="both", tight=True):
        self.master.axes.autoscale(axis=axis, tight=tight)
        self.master._canvas.draw()

        # Update the entries for axis limits with the new autoscaled limits
        self._xlim_min_var.set(self.master.axes.get_xlim()[0].round(4))
        self._xlim_max_var.set(self.master.axes.get_xlim()[1].round(4))

        self._ylim_min_var.set(self.master.axes.get_ylim()[0].round(4))
        self._ylim_max_var.set(self.master.axes.get_ylim()[1].round(4))


    def choisir_couleur_police(self, canvas, axis_type):
        color_code = colorchooser.askcolor(title="Choisir une couleur de police")
        if color_code:
            # Update the color button background
            self.dict_widget_font[axis_type]["color"].configure(bg=color_code[1])  # Update button color



    def fill__frame_legende(self):
        """Create the legend settings tab with controls to show/hide and customize legend entries."""
        ttk.Label(self.tab_legende, text="Paramètres de la légende:", style='Titre_parammetre.TLabel').grid(row=0, column=0, sticky="w", padx=5, pady=10, columnspan=2)
        
        # Checkbutton to show/hide legend on the canvas
        self.checkbutton_var_legende = tk.BooleanVar(value=self.master.axes.get_legend() is not None)
        checkbutton_show_legend = ttk.Checkbutton(self.tab_legende, text="Afficher la légende", variable=self.checkbutton_var_legende, command=self._toggle_legend, style='TkPlotCanvas.TCheckbutton')
        checkbutton_show_legend.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        
        # Checkbutton to show/hide the column titles in the legend
        self.checkbutton_var_title_column_legende = tk.BooleanVar(value = self.master.Is_title_display)
        checkbutton_title_column_legende = ttk.Checkbutton(self.tab_legende, text="Afficher les titres des colonnes", variable=self.checkbutton_var_title_column_legende, command=self._toggle_title_column_legende, style='TkPlotCanvas.TCheckbutton')
        checkbutton_title_column_legende.grid(row=1, column=2, columnspan=2, sticky="w", padx=5, pady=5)

        # Button to optimize (Automatically) the legend position (only if legend is shown)
        ttk.Button(self.tab_legende, text="Position par défaut", command=self._optimize_legend_position, style='TkPlotCanvas.TButton').grid(row=0, column=4, columnspan=2, sticky="we", padx=5, pady=5)

        # Button to apply legend changes:
        ttk.Button(self.tab_legende, text="Appliquer les changements", command=self._apply_legend_changes, style='TkPlotCanvas.TButton').grid(row=0, column=6, columnspan=3, padx=5, pady=5, sticky="we")

        # Choice of metadata to display in the legende
        self.list_combobox_legende = []
        self.list_entry_legende = [[] for _ in self.master._lines]  # To store entry widgets for each line and key
        for index, line in enumerate(self.master._lines):
            label_dict = self.master._line_labels[index]
            column_index = 0
            if len(self.list_combobox_legende) == 0:
                ttk.Label(self.tab_legende, text="Indice", style='Titre_parammetre.TLabel').grid(row=2, column=column_index, sticky="w", padx=5, pady=5)
                
                for key in label_dict:
                    # Only add a combobox for this key if it doesn't already exist in the legend title grid (to avoid duplicate comboboxes for the same key across different lines)
                    if not any(key == combo['values'] for combo in self.list_combobox_legende):
                        list_values_combo = [""] + list(label_dict.keys())
                        
                        combobox = ttk.Combobox(self.tab_legende, values=list_values_combo, state="readonly", width=15)
                        combobox.grid(row=2, column=column_index+1, padx=5, pady=5)

                        # Set the combobox to the current key if it exists in the legend title grid, otherwise set to ""
                        key_to_show = self.master.legend_to_show[column_index] if column_index < len(self.master.legend_to_show) else ""
                        index_key = list_values_combo.index(key_to_show) if key_to_show in list_values_combo else 0
                        combobox.current(index_key)  # Set to "None" by default

                        # bind the combobox selection event to update the legend display
                        combobox.bind("<<ComboboxSelected>>", partial(self._on_legende_update, combo_selected=combobox, column_index=column_index))
                        self.list_combobox_legende.append(combobox)

                    else:
                        # If the key already has a combobox, just add an empty one for this line
                        combobox = ttk.Combobox(self.tab_legende, values=[""], state="readonly", width=15)
                        combobox.grid(row=2, column=column_index+1, padx=5, pady=5)
                        combobox.current(0)  # Set to "None" by default
                    column_index += 1
                
            ttk.Label(self.tab_legende, text=str(index+1), style='Titre_parammetre.TLabel').grid(row=index+3, column=0, sticky="e", padx=5, pady=5)
            column_index = 0
            # Update the entries in the legend frame for each line based on the selected keys in the comboboxes
            for combobox in self.list_combobox_legende:
                key_to_show = combobox.get()
                entry_key = ttk.Entry(self.tab_legende, width=15, style='TkPlotCanvas.TEntry')
                entry_key.grid(row=index+3, column=column_index+1, sticky="w", padx=5, pady=5)
                self.list_entry_legende[index].append(entry_key)
                if key_to_show in label_dict:
                    if key_to_show in self.master.legend_to_show:
                        entry_key.insert(0,label_dict[key_to_show])

                column_index += 1

    def _on_legende_update(self, event, combo_selected=None, column_index=None):
        key_selected = combo_selected.get()
        # Update the legend display based on the selected metadata keys and values.
        for index, line in enumerate(self.master._lines):
            label_dict = self.master._line_labels[index]
            if key_selected in label_dict:
                value = label_dict[key_selected]
                if len(self.list_entry_legende[index]) > 0:
                    entry_widget = self.list_entry_legende[index][column_index]  
                    entry_widget.delete(0, tk.END)
                    entry_widget.insert(0, str(value))
            else:
                if len(self.list_entry_legende[index]) > 0:
                    entry_widget = self.list_entry_legende[index][column_index] 
                    entry_widget.delete(0, tk.END)
                    entry_widget.insert(0, "")

    def _toggle_legend(self):
        if self.checkbutton_var_legende.get():
            self.master.axes.legend(draggable=True)  # Show legend
            self.master.Is_legend_display = True
        else:
            legend = self.master.axes.legend(draggable=True) 
            if legend:
                legend.remove()  # Hide legend
                self.master.Is_legend_display = False
        self.master._canvas.draw()

    def _apply_legend_changes(self):
        """Apply the legend configuration and update the lines and displayed legend."""
        
        show_key_titles = self.checkbutton_var_title_column_legende.get()

        # Apply the changes to the legend based on the user input in the entries.
        for index, line in enumerate(self.master._lines):
            label_dict = self.master._line_labels[index]
            legend_entry_values = {}
            
            for column_index, combobox in enumerate(self.list_combobox_legende):
                key_selected = combobox.get()
                if key_selected in label_dict:
                    entry_widget = self.list_entry_legende[index][column_index]  
                    new_value = entry_widget.get()
                    legend_entry_values[key_selected] = new_value

            # Update the line label based on the legend entry values and whether to show key titles
            self.master._lines[index].set_label(self.master.get_string_legende(legend_entry_values, shown_keys=show_key_titles))  # Update line label based on legend entry values
        
         # Update the legend_to_show list with the new values for this line
        self.master.legend_to_show = [self.list_combobox_legende[i].get() for i in range(len(self.list_combobox_legende))] 

        if self.checkbutton_var_legende.get():
            self.master.axes.legend(draggable=True)  # Update legend to reflect changes
        self.master._canvas.draw()

    def _optimize_legend_position(self):
        if self.checkbutton_var_legende.get():
            self.master.axes.legend(loc='best', draggable=True)  # Automatically choose the best location for the legend
           
        else : 
            self.master.axes.legend(loc=None, draggable=True )  # Remove legend from the axes but keep it draggable
       
        self.master._canvas.draw()

    def _toggle_title_column_legende(self):
        # Update the legend display to show/hide column titles based on the checkbutton state
        self.master.Is_title_display = self.checkbutton_var_title_column_legende.get()
        
        # Update the legend_to_show list with the new values for this line
        self.master.legend_to_show = [self.list_combobox_legende[i].get() for i in range(len(self.list_combobox_legende))] 

        # Update the legende : 
        self.master._update_legende()

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
            bg_color: Background color for the widgets and plot.
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
        self.Is_cartouche_display = False

        # Panedwindow for resizable layout
        self.panedwindow = ttk.Panedwindow(self, orient=tk.VERTICAL)
        self.panedwindow.pack(fill=tk.BOTH, expand=True)

        # Frame Plot
        self._plot_frame = ttk.Frame(self.panedwindow, style='TkPlotCanvas.TFrame')
        self.panedwindow.add(self._plot_frame, weight=1)    

        # Frame Cartouche
        self._cartouche_frame = VerticalScrolledFrame(self.panedwindow, x_bar = True, bg_canvas ="", height_canvas = 100 , style_frame = 'TkPlotCanvas.TFrame')
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
        self.xarray_data = dict( dimension = "", variable = "")
        self.list_data_xarray = []
        

        # Create context menu.
        self.menu_click = tk.Menu(self, tearoff=0, bg=bg_color)
        self.menu_click.add_command(label="Modiification des axes et titres", command=partial(self.open_menu_graphique, "Axes et titre"))
        self.menu_click.add_separator()
        self.menu_click.add_command(label="Modiification des courbes", command=partial(self.open_menu_graphique, "Courbes"))
        self.menu_click.add_separator()
        self.menu_click.add_command(label="Modification du cartouche", command=partial(self.open_menu_graphique, "Cartouche"))    
        self.menu_click.add_command(label="Modiification de la légende", command=partial(self.open_menu_graphique, "Légende"))
        self._canvas.get_tk_widget().bind("<Button-3>", self.do_popup)

        # load the view if specified
        if load_view is not None  and os.path.isfile(load_view) :
            self.parametre_vue = self.load_parameters(load_view)
        else : 
            self.parametre_vue = {}

    def _setup_styles(self, bg="white"):
        """Configure default ttk styles for the plot canvas and surrounding widgets."""
        self.style = ttk.Style()

        self.bg_color = bg

        # Configure ttk styles for background color
        self.style.configure('TkPlotCanvas.TFrame', background=self.bg_color)

        self.style.configure('TkPlotCanvas.TNotebook', background=self.bg_color)
        self.style.configure('TkPlotCanvas.TNotebook.Tab', background=self.bg_color, font=('Arial', 10, 'bold'), padding=(10, 5))
        self.style.map('TkPlotCanvas.TNotebook.Tab', foreground=[('selected', 'black'), ('!selected', 'gray')], background=[('selected', self.bg_color), ('!selected', self.bg_color)])

        self.style.configure('TkPlotCanvas.TLabel', background=self.bg_color)
        self.style.configure('Cartouche_titre.TLabel', font=('Arial', 10, 'bold'), foreground="black", background=self.bg_color)
        self.style.configure('Cartouche.TLabel', font=('Arial', 10, 'normal'), foreground="black", background=self.bg_color)

        self.style.configure('Titre_parammetre.TLabel', font=('Arial', 10, 'bold'), foreground="black", background=self.bg_color)

        self.style.configure('TkPlotCanvas.TEntry', background=self.bg_color)
        self.style.configure('TkPlotCanvas.TButton', background=self.bg_color)

        self.style.configure('TkPlotCanvas.TCheckbutton', background=self.bg_color)
        self.style.configure('TkPlotCanvas.TLabelframe', background=self.bg_color)
        self.style.configure('TkPlotCanvas.TLabelframe.Label', background=self.bg_color, font=('Arial', 10, 'bold'))       


    def do_popup(self, event):
        """Show the context menu at the mouse cursor position."""
        try:
            self.menu_click.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_click.grab_release()

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
                widget.destroy()
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
            
        if line_display:
            # Add line show :
            line = self._lines[line_index] 
            color = line.get_color()
            linestyle = line.get_linestyle() if line.get_linestyle() != "None" else ""
            if linestyle == '-':
                linestyle = "―"
            marker = line.get_marker() if line.get_marker() != "None" else ""

            self._cartouche_grid[line_index].append(tk.Label(self._cartouche_frame, text=f"{linestyle}{marker}", background=self.bg_color, foreground=color, width=3, font=("Helvetica", 15, 'bold')))
            self._cartouche_grid[line_index][-1].grid(row= line_index + 1, column=0, sticky="w", padx=(5,0), pady=0)
            
        else : 
            self._cartouche_grid[line_index].append([])

        if not(label_to_display is None):
            # Add the values of the metadata in the cartouche
            column_index = 1       
            for key, value in label_to_display.items():
                self._cartouche_grid[line_index].append(ttk.Label(self._cartouche_frame, text=str(value), style="Cartouche.TLabel"))
                self._cartouche_grid[line_index][-1].grid(row=line_index + 1, column=column_index, sticky="w", padx=5, pady=5)
                column_index += 1   

    def get_string_legende(self, label_dict, shown_keys = False):
        """Build the legend string from a metadata dictionary based on selected display keys."""
        if shown_keys:
            return ", ".join(f"{key}: {value}" for key, value in label_dict.items() if key in self.legend_to_show)
        else:
            return ", ".join(f"{value}" for key, value in label_dict.items() if key in self.legend_to_show)

    def _update_legende(self):
        """Refresh legend labels and redraw the legend when settings change."""

        for index, line in enumerate(self._lines):
            label_dict = self._line_labels[index]
            line.set_label(self.get_string_legende(label_dict, shown_keys=self.Is_title_display))  # Update line label based on legend entry values and whether to show key titles

        # Update legend to reflect changes if lines are in the canvas
        if self.Is_legend_display and len(self._lines) > 0:
            self.axes.legend(draggable=True)  
        self._canvas.draw()

    def _update_axis(self, axis_to_update, parameters = {}, axe = "X"):
        """Apply saved axis settings such as tick font, limits, and scale type."""
        
        if "ticks" in parameters:
            tick_params = parameters["ticks"]
            for tick in axis_to_update.get_ticklabels():
                tick.set_fontname(tick_params.get("name"))
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
      

        return True

    def save_parameters(self):

        if hasattr(self, "open_menu_graphique"):
            window_parent = self.open_menu_graphique
        else :
            window_parent = self


        path_to_save = tk.filedialog.asksaveasfilename(parent = window_parent, initialdir=".", title="Enregistrer les paramètres",
                                                    defaultextension=".json", filetypes=[("JSON files", "*.json")])
        # Implement saving parameters to a JSON file here
        # Store :
        #  - axes limits and scale types
        #  - font properties of axes and title
        #  - curve properties (color, linewidth, linestyle, marker, markersize, label)
        #  - cartouche parameters (metadata keys)
        #  - legend parameters (location, font properties, key to display in the legend)

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

            "background_color": self.bg_color,
            "window_size": (self.master.winfo_width(), self.master.winfo_height()),
            "window_position": (self.master.winfo_x(), self.master.winfo_y()),


            "X_axis": {
                "lim": self.axes.get_xlim(),
                "scale": self.axes.get_xscale(),
                "autoscale": self.axes.get_autoscalex_on(),  # Assuming you want to save the autoscale state for x-axis
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
            "curves": { str(index):
                {
                    "color": line.get_color(),
                    "linewidth": line.get_linewidth(),
                    "linestyle": line.get_linestyle(),
                    "marker": line.get_marker(),
                    "markersize": line.get_markersize(),
                }
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
                "dimension" : self.xarray_data["dimension"],
                "variable" : self.xarray_data["variable"]
            }
        }

        return parameters


    def load_parameters(self, path_to_load=None, parameters_to_load = None):
        """Load parameters from a JSON file and apply them to the plot to restore a previous view. If parameters_to_load is provided, it will be used directly instead of loading from a file."""

        if  parameters_to_load is not None:
             parameters = parameters_to_load
        else:
            # Implement loading parameters from a JSON file here
            if path_to_load is None:
                if hasattr(self, "open_menu_graphique"):
                    window_parent = self.open_menu_graphique
                else :
                    window_parent = self

                path_to_load = tk.filedialog.askopenfilename(parent = window_parent, initialdir=".", title="Charger les paramètres",
                                                            defaultextension=".json", filetypes=[("JSON files", "*.json")])
                
            try:
                with open(path_to_load, 'r') as f:
                    parameters = json.load(f)

            except Exception as e:
                parameters = {}
            
        # Apply loaded parameters to the plot (axes limits, scale types, font properties, curve properties, cartouche parameters, legend parameters)
        if "background_color" in parameters:
            self.bg_color = parameters["background_color"]
            self.figure.set_facecolor(self.bg_color)
            self.axes.set_facecolor(self.bg_color)
            for line in self._lines:
                line.set_color(self.bg_color)
            self._canvas.get_tk_widget().configure(background=self.bg_color)
            self._canvas.draw()
        if "window_size" in parameters:
            self.master.geometry(f"{parameters['window_size'][0]}x{parameters['window_size'][1]}")
        if "window_position" in parameters:
            self.master.geometry(f"+{parameters['window_position'][0]}+{parameters['window_position'][1]}")

        if "X_axis" in parameters:
            self._update_axis(self.axes.xaxis, parameters["X_axis"], axe= "X" )

        if "Y_axis" in parameters:
            self._update_axis(self.axes.xaxis, parameters["Y_axis"], axe= "Y" )
        
        if "title" in parameters:
            title_params = parameters["title"].copy()
            if title_params.get("fontname") not in fm.FontManager().get_font_names():
                title_params["fontname"] = 'DejaVu Sans'
            self.axes.set_title(self._title_var.get(), **title_params)
        if "xlabel" in parameters:
            xlabel_params = parameters["xlabel"].copy()
            if xlabel_params.get("fontname") not in fm.FontManager().get_font_names():
                xlabel_params["fontname"] = 'DejaVu Sans'
            self.axes.set_xlabel(self._xlabel_var.get(), **xlabel_params)
        if "ylabel" in parameters:
            ylabel_params = parameters["ylabel"].copy()
            if ylabel_params.get("fontname") not in fm.FontManager().get_font_names():
                ylabel_params["fontname"] = 'DejaVu Sans'
            self.axes.set_ylabel(self._ylabel_var.get(), **ylabel_params)

        for index, line in enumerate(self._lines):
            if "curves" in parameters and str(index) in parameters["curves"]:
                curve_params = parameters["curves"][str(index)]
                line.set_color(curve_params.get("color"))
                line.set_linewidth(curve_params.get("linewidth"))
                line.set_linestyle(curve_params.get("linestyle"))
                line.set_marker(curve_params.get("marker"))
                line.set_markersize(curve_params.get("markersize"))

        if "cartouche" in parameters:
            cartouche_params = parameters["cartouche"]

            self.Is_cartouche_display = cartouche_params.get("Is_cartouche_display", True)
            if not self.Is_cartouche_display:
                self.panedwindow.forget(self._cartouche_frame)
            
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

        try :
            self.xarray_data["dimension"] = parameters["xarray_data"].get("dimension", "")
            self.xarray_data["variable"] = parameters["xarray_data"].get("variable", "")
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
        ) -> None:
        """Plot a curve in the embedded canvas.

        Args:
            ds: xarray Dataset containing the data to plot.
            title: Optional plot title.
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

        # construction des variables associées au xarray : 
        if not replot :
            self.list_data_xarray.append(ds)

        list_dim_var = list(ds.dims) + list(ds.data_vars)
        dimension = self.xarray_data["dimension"] if self.xarray_data["dimension"] in list_dim_var else list(ds.dims)[0]
        variable = self.xarray_data["variable"] if self.xarray_data["variable"] in list_dim_var else list(ds.data_vars)[0]

        x = ds[dimension].values
        y = ds[variable].values

        if type(x[0]) == datetime64:
            self.Is_Date_on_x_axis = True
            self.axes.xaxis_date()  # Set x-axis to date format if x data is datetime

        # On sauvegarde pour le prochain xarray : 
        self.xarray_data["dimension"] = dimension
        self.xarray_data["variable"] = variable

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

        self.axes.grid(grid)

        if self.parametre_vue != {}: # Si un fichier json a été chargé : 
            # Update X et Y axis from self.parameter_vue
            self._update_axis(self.axes.xaxis, self.parametre_vue.get("X_axis"), axe= "X" )
            self._update_axis(self.axes.yaxis, self.parametre_vue.get("Y_axis"), axe= "Y" )

        if legend and label_str is not None:
            if self.Is_legend_display:
                self.axes.legend(draggable=True)  # Make the legend draggable

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
        self.axes.cla()
        self._lines.clear()
        self._canvas.draw()

    def update_cartouche_frame(self):
        """Update the cartouche frame to reflect any changes in the metadata of the plotted lines."""
        for index, line in enumerate(self._lines):
            label_dict = self._line_labels[index]
            self.fill_cartouche_frame(label_to_display=label_dict, line_index=index, line_display=True)

        pass

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
        #plot_widget = TkPlotCanvas(root)
        plot_widget.pack(fill="both", expand=True)
        
        current_path =  os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
        try :
            ds_temperature = xr.open_dataset(current_path + "2024_temperature_2m.nc")
            ds_temperature = ds_temperature.rename({"valid_time": "time", "t2m": "temperature"})  # Renommer les dimensions et variables pour plus de clarté
            ds_temperature = ds_temperature.mean(dim=["latitude", "longitude"])  # Moyenne spatiale pour obtenir une série temporelle globale
            ds_temperature["temperature"] = ds_temperature["temperature"] - 273.15  # Convertir de Kelvin à Celsius
            ds_temperature["temperature"].attrs["units"] = "°C"  # Ajouter les unités aux attributs de la variable
            #print(ds_temperature)
            plot_widget.plot_xarray(ds_temperature, clear=False, title="Temperature 2m", label= dict(description="Weather data", base="", source="", history="", references="1", comment="") , legend=True)

            x = ds_temperature["time"].values

        except FileNotFoundError : 
            pass
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


from cProfile import label
from operator import index
import tkinter as tk
from tkinter import ttk
from typing import Callable, Iterable, Optional
from functools import partial

import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import colorchooser
import numpy as np
import copy
import json

class Window_font_parameter(tk.Toplevel):
    def __init__(self, master, frame_to_modifiy=""):
        super().__init__(master)
        self.title(f"Modification du {frame_to_modifiy}")
        self.geometry("400x400+500+100")
        self["bg"] = "#f0f0f0"

        self.frame_window = ttk.Frame(self)
        self.frame_window.pack(fill="both", expand=True, anchor="nw")

        self.button_apply = ttk.Button(self.frame_window, text="Appliquer les changement")

        self.padx_echelle = (5, 5)
        self.pady_echelle = (5, 5)

        self.dict_font_parameters = {}
        if frame_to_modifiy == "cartouche" : 
            label_frame_title = ttk.LabelFrame(self.frame_window, text="Paramètres pour le nom des colonnes :" )
            label_frame_title.pack(fill="both", side="top", padx=10, pady=10)

            label_frame_line = ttk.LabelFrame(self.frame_window, text="Paramètres pour les lignes :" )
            label_frame_line.pack(fill="both", side="top", padx=10, pady=10)

            self._fill_label_frame(label_frame_title, nom_frame="Cartouche, title")
            self._fill_label_frame(label_frame_line, nom_frame="Cartouche, line")


        elif frame_to_modifiy in ["xlabel", "ylabel"]  : 
            label_frame_title = ttk.LabelFrame(self.frame_window, text="Paramètres du nom de l'axe :" )
            label_frame_title.pack(fill="both", side="top", padx=10, pady=10)
            
            label_frame_line = ttk.LabelFrame(self.frame_window, text="Paramètres de l'échelle :" )
            label_frame_line.pack(fill="both", side="top", padx=10, pady=10)
            
            self._fill_label_frame(label_frame_title, nom_frame= frame_to_modifiy +", nom")
            self._fill_label_frame(label_frame_line, nom_frame=frame_to_modifiy + ", tick")

            self._set_widget_with_axis_font(frame_to_modifiy, self.master.master.axes )

        elif frame_to_modifiy == "Graphique title" : 
            label_frame_title = ttk.LabelFrame(self.frame_window, text="Paramètres du titre :" )
            label_frame_title.pack(fill="both", side="top", padx=10, pady=10)
            self._fill_label_frame(label_frame_title, nom_frame= frame_to_modifiy +", nom")

            self._set_widget_with_axis_font(frame_to_modifiy, self.master.master.axes )
        
        self.button_apply.pack(fill="x", side="top", padx=10, pady=10)

    def _fill_label_frame(self, label_frame, nom_frame = ""):
        
        row_start = 0
        column_start = 0

        ttk.Label(label_frame, text="Police :").grid(row=row_start, column=column_start, sticky="e", padx=self.padx_echelle, pady=self.pady_echelle)
        list_police = list(tk.font.families())
        combo_police = ttk.Combobox(label_frame, values=list_police, state="readonly", width=20)
        combo_police.grid(row=row_start, column=column_start + 1, sticky="w", columnspan=2, padx=5, pady=5)
        combo_police.current(0)  # Set to current style of ticks or "normal" by default
        row_start +=1

        ttk.Label(label_frame, text="Taille de la police :").grid(row=row_start, column=column_start, sticky="e", padx=self.padx_echelle, pady=self.pady_echelle)
            # Spinbox to choose the size of the ticks on the axis
        spinbox_size_police = ttk.Spinbox(label_frame, from_=0, to=20, increment=1, width=10)
        spinbox_size_police.grid(row=row_start, column=column_start + 1,columnspan=2, sticky="w", padx=5, pady=5)
        spinbox_size_police.delete(0, "end")
        #self.spinbox_size_police_title.insert(0, int(axes_axis.get_ticklabels()[0].get_fontsize()) if axes_axis.get_ticklabels() else 10)  # Set to current size of x ticks or 10 by default
        row_start +=1

        # Combobox to choose the style of the frame
        ttk.Label(label_frame, text="Styles de la police:").grid(row=row_start, column=column_start, sticky="e", padx=self.padx_echelle, pady=self.pady_echelle) 
        self.list_style_police = ["normal", "italic", "oblique"]
        combo_style_police = ttk.Combobox(label_frame, values=self.list_style_police, state="readonly", width=10)
        combo_style_police.grid(row=row_start, column=column_start + 1, sticky="w", padx=5, pady=5)
        #index_style = list_style_police.index(label_frame.get_ticklabels()[0].get_fontstyle()) if axes_axis.get_ticklabels() else 0 
        combo_style_police.current(0)  # Set to current style of ticks or "normal" by default
        
         # Checkbutton to choose if frame is bold or not
        var_checkbutton_gras = tk.BooleanVar(value=False)
        checkbutton_bold = ttk.Checkbutton(label_frame, text="Gras", variable= var_checkbutton_gras)
        checkbutton_bold.grid(row=row_start, column=column_start + 2, sticky="w", padx=5, pady=5)
        checkbutton_bold.configure(state=["selected"])  # Ensure the checkbutton is not in an indeterminate state
        row_start +=1
        
        # Button to choose the color :
        ttk.Label(label_frame, text="Couleur de la police:").grid(row=row_start, column=column_start, sticky="e", padx=self.padx_echelle, pady=self.pady_echelle)
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
 
        style = self.master.master.style.configure(style)
        style_font = style["font"].split(" ")
        index_police = self.list_style_police.index(int(style_font[0])) if style_font[0] in self.list_style_police else 0
        self.dict_font_parameters[nom_frame]["combo_police"].current(index_police)
        self.dict_font_parameters[nom_frame]["spinbox size police"].insert(0, int(style_font[1]))
        self.dict_font_parameters[nom_frame]["checkbutton bold"][0].state(["selected"] if style_font[2] == "bold" else ["!selected"])
        self.dict_font_parameters[nom_frame]["checkbutton bold"][1].set( style_font[2] == "bold" )

        if len(style_font) > 3:
            index_police = self.list_style_police.index(int(style_font[0])) if style_font[0] in self.list_style_police else 0
            self.dict_font_parameters[nom_frame][ "combobox style police"].current(index_police)

        self.dict_font_parameters[nom_frame]["button_couleur"].configure(bg=style["foreground"])

    def set_widget_with_cartouch_font(self):
        # Bind fonction apply style : 
        self.button_apply.configure(command=self._update_cartouch)

        self._set_widget_frame_cartouche(style='Cartouche_titre.TLabel', nom_frame="Cartouche, title")
        self._set_widget_frame_cartouche(style='Cartouche.TLabel', nom_frame="Cartouche, line")
        

    def _update_cartouch(self):
        # Pour le titre : 
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

    # Fonction pour les axes : 
    def _set_widget_with_axis_font(self, nom_axe, objet_axis):

        # Bind fonction apply style : 
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
        list_police = list(tk.font.families())
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


    def choisir_couleur_police(self, widget):
        color_code = colorchooser.askcolor(master = self ,title="Choisir une couleur de police")
        if color_code:
            # Update the color button background
           widget.configure(bg=color_code[1])  # Update button color

class Menu_graphique(tk.Toplevel):
    def __init__(self, master, notebook_shown=""):
        super().__init__(master)
        self.title("Menu de modification de la courbe")
        self.geometry("1000x500+600+100")
        self["bg"] = "#f0f0f0"

        self.notebook_shown = notebook_shown
    
        # Initialize a dictionary to store font controls for axes and title
        self.dict_widget_font =  {"title": None, "xlabel": None, "ylabel": None}

        self.padding_notebook =  (20, 5, 20, 5) # (left, right, top, bottom)
        self.style = ttk.Style(self)
    
        frame_button = ttk.Frame(self)
        frame_button.pack(side="top", fill="x")

        # Button : Save parameters of the plot in a json file
        self._save_button = ttk.Button(frame_button, text="Enregistrer les paramètres", command=self.master.save_parameters)
        self._save_button.pack(side="right", pady=5, padx=10)

        # Button : Load parameters of the plot from a json file
        self._load_button = ttk.Button(frame_button, text="Charger les paramètres", command=self.master.load_parameters)
        self._load_button.pack(side="right", pady=5, padx=10)

        # Create notebook for organizing controls
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(side="bottom", fill="both", expand=True)

        # Tab Axes et titre:
        self.tab_axes = ttk.Frame(self._notebook)
        self._notebook.add(self.tab_axes, text="Axes et titre", padding=self.padding_notebook)
        self.fill__frame_axes()
        
        # Tab 3: Cartouche
        self.tab_cartouche = ttk.Frame(self._notebook)
        self._notebook.add(self.tab_cartouche, text="Cartouche", padding=self.padding_notebook)
        self.fill__frame_cartouche_menu()

        # Tab 4: Courbe
        self.tab_courbe = ttk.Frame(self._notebook)
        self._notebook.add(self.tab_courbe, text="Courbes", padding=self.padding_notebook)
        self.fill__frame_courbe()

        # Tab 5: Legende
        self.tab_legende = ttk.Frame(self._notebook)
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
        # Add controls for cartouche here
        label = ttk.Label(self.tab_cartouche, text="Paramètres du cartouche:", style='Titre_parammetre.TLabel')
        label.grid(row=0, column=0, sticky="w", padx=5, pady=10, columnspan=4 )

        # Bonton pour moodifier font du cartouche : 
        button_modify_font = ttk.Button(self.tab_cartouche, text="Paramètres du cartouche:", 
                                        command=self._cartouch_show_font_parameters )
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
                entry_key = ttk.Entry(self.tab_cartouche, width=15)
                entry_key.bind('<KeyRelease>', partial(self._on_entry_cartouche_update, line_index=index, column_index=column_index-1))
                entry_key.grid(row=index+2, column=column_index, sticky="w", padx=5, pady=5)
                self.list_entry_cartouche[index].append(entry_key)
                column_index += 1
                if key_to_show in label_dict:
                    entry_key.insert(0,label_dict[key_to_show])

    def _on_entry_cartouche_update(self, event, line_index=None, column_index=None):
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
            
            self.master._cartouche_grid[line_index][column_index+1] = ttk.Label(self.master._cartouche_frame, text=str(new_value))
            self.master._cartouche_grid[line_index][column_index+1].grid(row=line_index + 1, column=column_index+1, sticky="w", padx=5, pady=5)


    def _on_cartouche_update(self, event, combo_selected=None, column_index=None):
        
        key_selected = combo_selected.get()
        # Update the cartouche display based on the selected metadata keys and values.
        try:
            self.master._cartouche_title_grid[column_index].destroy()  # Remove the old label if it exists
        except Exception:                
            pass
            # Update the title of the cartouche column
        self.master._cartouche_title_grid[column_index] = ttk.Label(self.master._cartouche_frame, text=key_selected, style='Cartouche_titre.TLabel')
        self.master._cartouche_title_grid[column_index].grid(row=0, column=column_index+1, sticky="w", padx=5, pady=5)
            # Update the values in the cartouche for each line based on the selected key in the combobox
        for index, line in enumerate(self.master._lines):
            label_dict = self.master._line_labels[index]
            
            self.master._cartouche_grid[index][column_index+1].destroy()  # Remove the old label if it exists

            
            if key_selected in label_dict:
                value = label_dict[key_selected]
            else :
                value = "" 

            self.master._cartouche_grid[index][column_index+1] = ttk.Label(self.master._cartouche_frame, text=str(value))
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
    


    def fill__frame_courbe(self):
        
        self.style.configure('Courbe.TLabel', font=('Arial', 10, 'bold'))

        label = ttk.Label(self.tab_courbe, text="Paramètres des courbes:", style='Courbe.TLabel')
        label.grid(row=0, column=0, sticky="w", padx=5, pady=10, columnspan=6 )

        label = ttk.Label(self.tab_courbe, text="Couleur:", style='Courbe.TLabel').grid(row=1, column=0, sticky="w", padx=5, pady=5)
        label = ttk.Label(self.tab_courbe, text="Épaisseur de ligne:", style='Courbe.TLabel').grid(row=1, column=1, sticky="w", padx=5, pady=5)
        label = ttk.Label(self.tab_courbe, text="Style de ligne:", style='Courbe.TLabel').grid(row=1, column=2, sticky="w", padx=5, pady=5)
        label = ttk.Label(self.tab_courbe, text="Marqueur:", style='Courbe.TLabel').grid(row=1, column=3, sticky="w", padx=5, pady=5)
        label = ttk.Label(self.tab_courbe, text="Taille du marqueur:", style='Courbe.TLabel').grid(row=1, column=4, sticky="w", padx=5, pady=5)
        label = ttk.Label(self.tab_courbe, text="Label:", style='Courbe.TLabel').grid(row=1, column=5, sticky="w", padx=5, pady=5)

        self.list_widget = []
        for index, line in enumerate(self.master._lines):
           self.affiche_parametres_courbe(line, index,self.list_widget)
        # Add controls for curve properties here
        pass
    
    def affiche_parametres_courbe(self, line, index, list_widget):
        
        
        label = line.get_label()
        color = line.get_color()
        linestyle = line.get_linestyle()
        linewidth = line.get_linewidth()
        marker = line.get_marker()
        markersize = line.get_markersize()

        button_color = tk.Button(self.tab_courbe, bg=color, command=partial(self.choisir_couleur, line, index), width=5)
        button_color.grid(row=index+2, column=0, padx=5, pady=5)

        spinbox_linewidth = ttk.Spinbox(self.tab_courbe, from_=0.5, to=10.0, increment=0.5, width=5, command=partial(self.update_line_property, line, 'linewidth', index=index))
        spinbox_linewidth.grid(row=index+2, column=1, padx=5, pady=5)
        spinbox_linewidth.set(linewidth)
        
        combobox_linestyle = ttk.Combobox(self.tab_courbe, values=["-", "--", "-.", "None"], state="readonly", width=8)
        combobox_linestyle.grid(row=index+2, column=2, padx=5, pady=5)
        combobox_linestyle.current(combobox_linestyle['values'].index(linestyle))
        combobox_linestyle.bind("<<ComboboxSelected>>", partial(self.update_line_property, line, 'linestyle', index=index))

        combobox_marker = ttk.Combobox(self.tab_courbe, values=["o", "s", "^", "None"], state="readonly", width=8)
        combobox_marker.grid(row=index+2, column=3, padx=5, pady=5)
        combobox_marker.current(combobox_marker['values'].index(marker))
        combobox_marker.bind("<<ComboboxSelected>>", partial(self.update_line_property, line, 'marker', index=index))

        
        spinbox_markersize = ttk.Spinbox(self.tab_courbe, from_=1, to=20, increment=1, width=5, command=partial(self.update_line_property, line, 'markersize', index=index))
        spinbox_markersize.grid(row=index+2, column=4, padx=5, pady=5)
        spinbox_markersize.set(markersize)

        entry_label = ttk.Entry(self.tab_courbe, width=100)
        entry_label.grid(row=index+2, column=5, padx=5, pady=5)
        entry_label.insert(0, label)
        entry_label.bind("<FocusOut>", partial(self.update_line_property, line, 'label', index=index))
   
        list_widget.append([button_color, spinbox_linewidth, combobox_linestyle, combobox_marker, spinbox_markersize, entry_label])


    def choisir_couleur(self, line, index):
        color_code = colorchooser.askcolor(title="Choisir une couleur")
        if color_code:
            line.set_color(color_code[1])
            self.master._canvas.draw()  
            self.list_widget[index][0].configure(bg=color_code[1])  # Update button color

    def update_line_property(self, line, property_name, event=None, index=None):
        widget = event.widget if event else None
        if property_name == 'linewidth':
            value_linewidth = self.list_widget[index][1].get()
            line.set_linewidth(float(value_linewidth))
        elif property_name == 'linestyle':
            value_linestyle = self.list_widget[index][2].get()
            line.set_linestyle(value_linestyle)
        elif property_name == 'marker':
            value_marker = self.list_widget[index][3].get()
            line.set_marker(value_marker)
        elif property_name == 'markersize':
            value_markersize = self.list_widget[index][4].get()
            line.set_markersize(float(value_markersize))
        elif property_name == 'label':
            line.set_label(widget.get())
            self.master.axes.legend()  # Update legend to reflect label change
        self.master._canvas.draw()

    def fill__frame_axes(self):
        
        ttk.Label(self.tab_axes, text="Modification des axes et titres:", style='Titre_parammetre.TLabel').grid(row=0, column=0, sticky="w", padx=5, pady=10, columnspan=2)

        # Add controls for axes and title here
        padx_axes = (5, 5)
        pady_axes = (5, 5)


        # Frame for title : 
        frame_title = ttk.LabelFrame(self.tab_axes, text="Titre", padding=(10, 10))
        frame_title.grid(row=1, column=0, columnspan=4, sticky="we", padx=padx_axes, pady=pady_axes)

        ttk.Label(frame_title, text="Titre:").grid(row=1, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        self._title_var = tk.StringVar(value="")
        self._title_entry = ttk.Entry(frame_title, textvariable=self._title_var, width=50)
        self._title_entry.grid(row=1, column=1, padx=(0, 4), sticky="w")
        self._title_var.set(self.master.axes.get_title())
        button_font_title = ttk.Button(frame_title, text="Modifier la police", 
                            command= partial(Window_font_parameter, self, frame_to_modifiy="Graphique title") )
        button_font_title.grid(row=1, column=2, padx=(10, 5), sticky="ew")

        # frame for X axis : 
        fame_x_axis = ttk.LabelFrame(self.tab_axes, text="Axe X", padding=(10, 10))
        fame_x_axis.grid(row=2, column=0, columnspan=2, sticky="we", padx=padx_axes, pady=pady_axes)
        ttk.Label(fame_x_axis, text="Abscisse:").grid(row=1, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        self._xlabel_var = tk.StringVar(value="")
        self._xlabel_entry = ttk.Entry(fame_x_axis, textvariable=self._xlabel_var, width=25)
        self._xlabel_entry.grid(row=1, column=1, columnspan=2, padx=(0, 4), sticky="w")
        self._xlabel_var.set(self.master.axes.get_xlabel())
        
        ttk.Separator(fame_x_axis, orient='horizontal').grid(row=5, column=0, columnspan=3, sticky="we", pady=(10, 5))

            # Modifier les axes : 
        ttk.Label(fame_x_axis, text="Valeur min:").grid(row=6, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        ttk.Label(fame_x_axis, text="Valeur max:").grid(row=7, column=0, sticky="e", padx=padx_axes, pady=pady_axes)

        self._xlim_min_var = tk.StringVar(value="")
        ttk.Entry(fame_x_axis, textvariable=self._xlim_min_var, width=15).grid(row=6, column=1, sticky="we")
        self._xlim_max_var = tk.StringVar(value="")
        ttk.Entry(fame_x_axis, textvariable=self._xlim_max_var, width=15).grid(row=7, column=1, sticky="we")

        ttk.Label(fame_x_axis, text="Echelle:").grid(row=8, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        self._xscale_var = tk.StringVar(value="linear")
        ttk.Combobox(fame_x_axis, textvariable=self._xscale_var, values=["linear", "log"], state="readonly", width=8).grid(row=8, column=1, columnspan=2, sticky="we")
        ttk.Button(fame_x_axis, text="Auto", command=self._on_zoom_auto, width=5).grid(row=6,column=2, rowspan=2, padx=padx_axes, pady=pady_axes, sticky="we")

        ttk.Separator(fame_x_axis, orient='horizontal').grid(row=9, column=0, columnspan=3, sticky="we", pady=(10, 5))

            # Bouton police : 
        button_font_xlabel = ttk.Button(fame_x_axis, text="Modifier la police", 
                            command= partial(Window_font_parameter, self, frame_to_modifiy="xlabel") )
        button_font_xlabel.grid(row=10, column=0, columnspan=3, padx=(5, 5), sticky="ew")

        # frame for Y axis : 
        fame_y_axis = ttk.LabelFrame(self.tab_axes, text="Axe Y", padding=(10, 10))
        fame_y_axis.grid(row=2, column=2, columnspan=2, sticky="we", padx=padx_axes, pady=pady_axes)
        ttk.Label(fame_y_axis, text="Ordonnée:").grid(row=1, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        self._ylabel_var = tk.StringVar(value="")
        self._ylabel_entry = ttk.Entry(fame_y_axis, textvariable=self._ylabel_var, width=25)
        self._ylabel_entry.grid(row=1, column=1, columnspan=2, padx=(0, 4), sticky="w")
        self._ylabel_var.set(self.master.axes.get_ylabel())

        ttk.Separator(fame_y_axis, orient='horizontal').grid(row=5, column=0, columnspan=3, sticky="we", pady=(10, 5))
         # Modifier les axes : 
        ttk.Label(fame_y_axis, text="Valeur min:").grid(row=6, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        ttk.Label(fame_y_axis, text="Valeur max:").grid(row=7, column=0, sticky="e", padx=padx_axes, pady=pady_axes)

        self._ylim_min_var = tk.StringVar(value="")
        ttk.Entry(fame_y_axis, textvariable=self._ylim_min_var, width=15).grid(row=6, column=1, sticky="we")
        self._ylim_max_var = tk.StringVar(value="")
        ttk.Entry(fame_y_axis, textvariable=self._ylim_max_var, width=15).grid(row=7, column=1, sticky="we")
        ttk.Button(fame_y_axis, text="Auto", command=self._on_zoom_auto, width=5).grid(row=6,column=2, rowspan=2, padx=padx_axes, pady=pady_axes, sticky="we")

        ttk.Label(fame_y_axis, text="Echelle:").grid(row=8, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        self._yscale_var = tk.StringVar(value="linear")
        ttk.Combobox(fame_y_axis, textvariable=self._yscale_var, values=["linear", "log"], state="readonly", width=8).grid(row=8, column=1, columnspan=2, sticky="we")

        ttk.Separator(fame_y_axis, orient='horizontal').grid(row=9, column=0, columnspan=3, sticky="we", pady=(10, 5))

        # Bouton police :
        button_font_ylabel = ttk.Button(fame_y_axis, text="Modifier la police", 
                            command= partial(Window_font_parameter, self, frame_to_modifiy="ylabel") )
        button_font_ylabel.grid(row=10, column=0, columnspan=3, padx=(5, 5), sticky="ew")


        # Apply button to update axes and title:
        ttk.Button(self.tab_axes, text="Appliquer les changements", command=self._apply_axes_changes, width=20).grid(row=0, column=2, columnspan=2, padx=padx_axes, pady=pady_axes, sticky="we")

    def _apply_axes_changes(self):
        # Mise à jour des titre et x/y labels : 
        self.master.axes.set_title(self._title_var.get())
        self.master.axes.set_xlabel(self._xlabel_var.get())
        self.master.axes.set_ylabel(self._ylabel_var.get())
        
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
            self.master.axes.set_xscale(self._xscale_var.get())
            self.master.axes.set_yscale(self._yscale_var.get())

            
        except ValueError:
            tk.messagebox.showerror("Invalid input", "Please enter valid numeric values for axis limits.")

        self.master._canvas.draw()
    
    def _on_zoom_auto(self):
        self.master.axes.autoscale()
        self.master._canvas.draw()


    def choisir_couleur_police(self, canvas, axis_type):
        color_code = colorchooser.askcolor(title="Choisir une couleur de police")
        if color_code:
            # Update the color button background
            self.dict_widget_font[axis_type]["color"].configure(bg=color_code[1])  # Update button color



    def fill__frame_legende(self):
        # Add controls for legend properties here
        ttk.Label(self.tab_legende, text="Paramètres de la légende:", style='Titre_parammetre.TLabel').grid(row=0, column=0, sticky="w", padx=5, pady=10, columnspan=2)
        
        # Checkbutton to show/hide legend on the canvas
        self.checkbutton_var_legende = tk.BooleanVar(value=self.master.axes.get_legend() is not None)
        checkbutton_show_legend = ttk.Checkbutton(self.tab_legende, text="Afficher la légende", variable=self.checkbutton_var_legende, command=self._toggle_legend)
        checkbutton_show_legend.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        
        # Checkbutton to show/hide the column titles in the legend
        self.checkbutton_var_title_column_legende = tk.BooleanVar(value = self.master.Is_title_display)
        checkbutton_title_column_legende = ttk.Checkbutton(self.tab_legende, text="Afficher les titres des colonnes", variable=self.checkbutton_var_title_column_legende, command=self._toggle_title_column_legende)
        checkbutton_title_column_legende.grid(row=1, column=2, columnspan=2, sticky="w", padx=5, pady=5)

        # Button to optimize (Automatically) the legend position (only if legend is shown)
        ttk.Button(self.tab_legende, text="Position par défaut", command=self._optimize_legend_position).grid(row=0, column=4, columnspan=2, sticky="we", padx=5, pady=5)

        # Button to apply legend changes:
        ttk.Button(self.tab_legende, text="Appliquer les changements", command=self._apply_legend_changes, width=20).grid(row=0, column=6, columnspan=3, padx=5, pady=5, sticky="we")

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
                entry_key = ttk.Entry(self.tab_legende, width=15)
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
            self.master.axes.legend()  # Show legend
            self.master.Is_legend_display = True
        else:
            legend = self.master.axes.get_legend()
            if legend:
                legend.remove()  # Hide legend
                self.master.Is_legend_display = False
        self.master._canvas.draw()

    def _apply_legend_changes(self):
        
        # Determine whether to show column titles in the legend based on the checkbutton state
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
            self.master.axes.legend()  # Update legend to reflect changes
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

        if self._initialized_style :
            self._initialized_style(bg=bg_color)
            self._initialized_style = True

        # StringVars to hold the current title and axis labels for synchronization with the menu.
        self._title_var = tk.StringVar(value="")
        self._xlabel_var = tk.StringVar(value="")
        self._ylabel_var = tk.StringVar(value="")
        self.legend_to_show = []
        self.Is_legend_display = False
        self.Is_title_display = False

        # Panedwindow for resizable layout
        self.panedwindow = ttk.Panedwindow(self, orient=tk.VERTICAL)
        self.panedwindow.pack(fill=tk.BOTH, expand=True)

        # Frame Plot
        self._plot_frame = ttk.Frame(self.panedwindow)
        self.panedwindow.add(self._plot_frame, weight=1)    

        # Frame Cartouche
        self._cartouche_frame = ttk.Frame(self.panedwindow, height=100)
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
        self._active_line_index: int = 0

        # Create the canvas
        self._canvas = FigureCanvasTkAgg(self.figure, master= self._plot_frame)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(fill="both", expand=True)

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
        if load_view:
            self.parametre_vue = self.load_parameters(load_view)
        else : 
            self.parametre_vue = {}

    def _initialized_style(self, bg="white"):
        # Set a default style for the application (optional)
        self.style = ttk.Style()

        self.bg_color = bg

        # Configure ttk styles for background color
        self.style.configure('TFrame', background=self.bg_color)

        self.style.configure('TNotebook', background=self.bg_color)
        self.style.configure('TNotebook.Tab', background=self.bg_color, font=('Arial', 10, 'bold'), padding=(10, 5))
        self.style.map('TNotebook.Tab', foreground=[('selected', 'black'), ('!selected', 'gray')], background=[('selected', self.bg_color), ('!selected', self.bg_color)])

        self.style.configure('TLabel', background=self.bg_color)
        self.style.configure('Cartouche_titre.TLabel', font=('Arial', 10, 'bold'), foreground="black")
        self.style.configure('Cartouche.TLabel', font=('Arial', 10, 'normal'), foreground="black")

        self.style.configure('Titre_parammetre.TLabel', font=('Arial', 10, 'bold'), foreground="black")

        self.style.configure('TEntry', background=self.bg_color)
        self.style.configure('TButton', background=self.bg_color)
        self.style.configure('TCombobox', background=self.bg_color)
        self.style.configure('TCheckbutton', background=self.bg_color)
        self.style.configure('TLabelframe', background=self.bg_color)
        self.style.configure('TLabelframe.Label', background=self.bg_color, font=('Arial', 10, 'bold'))
        


    def do_popup(self, event):
        try:
            self.menu_click.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_click.grab_release()

    def open_menu_graphique(self, menu_type):
        try : 
            self.open_menu_graphique.destroy()  # Ferme le menu précédent s'il existe
        except Exception:
            pass
        self.open_menu_graphique = Menu_graphique(self, notebook_shown=menu_type)

    def fill_cartouche_frame(self, label_to_display: Optional[dict] = None, line_index: int = 0, line_display: bool = True) -> None:
        
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

            self._cartouche_grid[line_index].append(ttk.Label(self._cartouche_frame, text=f"{linestyle}{marker}", background=self.bg_color, foreground=color, width=3, font=("Helvetica", 15, 'bold')))
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
        if shown_keys:
            return ", ".join(f"{key}: {value}" for key, value in label_dict.items() if key in self.legend_to_show)
        else:
            return ", ".join(f"{value}" for key, value in label_dict.items() if key in self.legend_to_show)

    def _update_legende(self):

        for index, line in enumerate(self._lines):
            label_dict = self._line_labels[index]
            line.set_label(self.get_string_legende(label_dict, shown_keys=self.Is_title_display))  # Update line label based on legend entry values and whether to show key titles

        # Update legend to reflect changes if lines are in the canvas
        if self.Is_legend_display and len(self._lines) > 0:
            self.axes.legend(draggable=True)  
        self._canvas.draw()

    def _update_axis(self, axis_to_update, parameters = {}, axe = "X"):
        
        if "ticks" in parameters:
            tick_params = parameters["ticks"]
            for tick in axis_to_update.get_ticklabels():
                tick.set_fontsize(tick_params.get("size"))
                tick.set_fontstyle(tick_params.get("style"))
                tick.set_fontweight(tick_params.get("weight"))
                tick.set_color(tick_params.get("color"))  
        
        if "lim" in parameters and axe == "X":
                self.axes.set_xlim(parameters["lim"])
        if "scale" in parameters and axe == "X":
            self.axes.set_xscale(parameters["scale"])

        if "lim" in parameters and axe == "Y":
            self.axes.set_ylim(parameters["lim"])
        if "scale" in parameters and axe == "Y":
            self.axes.set_yscale(parameters["scale"])
        

        return True

    def save_parameters(self):
        
        path_to_save = tk.filedialog.asksaveasfilename(initialdir=".", title="Enregistrer les paramètres",
                                                    defaultextension=".json", filetypes=[("JSON files", "*.json")])
        # Implement saving parameters to a JSON file here
        # Store :
        #  - axes limits and scale types
        #  - font properties of axes and title
        #  - curve properties (color, linewidth, linestyle, marker, markersize, label)
        #  - cartouche parameters (metadata keys)
        #  - legend parameters (location, font properties, key to display in the legend)

        parameters = {

            "background_color": self.bg_color,
            "window_size": (self.master.winfo_width(), self.master.winfo_height()),
            "window_position": (self.master.winfo_x(), self.master.winfo_y()),


            "X_axis": {
                "lim": self.axes.get_xlim(),
                "scale": self.axes.get_xscale(),
                "ticks": {
                    "size": self.axes.xaxis.get_ticklabels()[0].get_fontsize() if len(self.axes.xaxis.get_ticklabels()) > 0 else None,
                    "style": self.axes.xaxis.get_ticklabels()[0].get_fontstyle() if len(self.axes.xaxis.get_ticklabels()) > 0 else None,
                    "weight": self.axes.xaxis.get_ticklabels()[0].get_fontweight() if len(self.axes.xaxis.get_ticklabels()) > 0 else None,
                    "color": self.axes.xaxis.get_ticklabels()[0].get_color() if len(self.axes.xaxis.get_ticklabels()) > 0 else None
                }
            },
            "Y_axis": {
            "lim": self.axes.get_ylim(),
            "scale": self.axes.get_yscale(),
            "ticks": {
                "size": self.axes.yaxis.get_ticklabels()[0].get_fontsize() if len(self.axes.yaxis.get_ticklabels()) > 0 else None,
                "style": self.axes.yaxis.get_ticklabels()[0].get_fontstyle() if len(self.axes.yaxis.get_ticklabels()) > 0 else None,
                "weight": self.axes.yaxis.get_ticklabels()[0].get_fontweight() if len(self.axes.yaxis.get_ticklabels()) > 0 else None,
                "color": self.axes.yaxis.get_ticklabels()[0].get_color() if len(self.axes.yaxis.get_ticklabels()) > 0 else None
                },
            },
            "title": {
                "fontsize": self.axes.title.get_fontsize(),
                "fontstyle": self.axes.title.get_fontproperties().get_style(),
                "fontweight": self.axes.title.get_fontproperties().get_weight(),
                "color": self.axes.title.get_color()
            },
            "xlabel": {
                "fontsize": self.axes.xaxis.label.get_fontsize(),
                "fontstyle": self.axes.xaxis.label.get_fontproperties().get_style(),
                "fontweight": self.axes.xaxis.label.get_fontproperties().get_weight(),
                "color": self.axes.xaxis.label.get_color()
            },
            "ylabel": {
                "fontsize": self.axes.yaxis.label.get_fontsize(),
                "fontstyle": self.axes.yaxis.label.get_fontproperties().get_style(),
                "fontweight": self.axes.yaxis.label.get_fontproperties().get_weight(),
                "color": self.axes.yaxis.label.get_color()
            },
            "curves": { index:
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
            },
            "legend": {
                "displayed_keys": [ key for key in self.legend_to_show if key != '' ] if len(self.legend_to_show) > 0 else [],
                "Is_legend_display" : self.Is_legend_display,
                "Is_title_display": self.Is_title_display ,

            }
        }
        
        with open(path_to_save, 'w') as f:
            json.dump(parameters, f, indent=4)


    def load_parameters(self, path_to_load=None):
        # Implement loading parameters from a JSON file here
        if path_to_load is None:
            path_to_load = tk.filedialog.askopenfilename(initialdir=".", title="Charger les paramètres",
                                                        defaultextension=".json", filetypes=[("JSON files", "*.json")])
            
        if path_to_load =="":
            return False # TODO 

        with open(path_to_load, 'r') as f:
            parameters = json.load(f)
        
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
            self.axes.set_title(self._title_var.get(), parameters["title"])
        if "xlabel" in parameters:
            self.axes.set_xlabel(self._xlabel_var.get(), parameters["xlabel"])
        if "ylabel" in parameters:
            self.axes.set_ylabel(self._ylabel_var.get(), parameters["ylabel"])

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
            self._active_line_index = 0


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

        
        line, = self.axes.plot(x, y, label=label_str, **modif_plot_kwargs)
        self._lines.append(line)
        self._line_labels.append(label)

        # Cartouche: Update the cartouche with the metadata of the newly added line.
        self.fill_cartouche_frame(label_to_display=label, line_index=len(self._lines)-1, line_display=True)

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

    


def demo() -> None:
    """Demo application for the TkPlotCanvas."""
    root = tk.Tk()
    root.title("Tkinter + Matplotlib Plot Demo")

    plot_widget = TkPlotCanvas(root, load_view="vue.json")  # Load parameters from a JSON file if it exists
    #plot_widget = TkPlotCanvas(root)
    plot_widget.pack(fill="both", expand=True)

    x = list(range(11))
    y = [xi**2 for xi in x]
    
    import xarray as xr
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

    #ds_2.attrs["references"] = "2"
    #ds_2.attrs["comment"] = "Second curve"
    # Add a second curve without clearing the first.

    plot_widget.plot(ds_2["time"], ds_2["temperature"], clear=False, label=ds_2.attrs, legend=True, color="black")
    
    root.mainloop()


if __name__ == "__main__":
    demo()

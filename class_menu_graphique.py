from tkinter import colorchooser
import tkinter as tk
from tkinter import ttk
from functools import partial

from vertical_frame import VerticalScrolledFrame
from class_window_font_parameter import Window_font_parameter


class Menu_graphique(tk.Toplevel):
    """Dialog window to edit plot, curve, cartouche, and legend settings."""

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
        self._load_button = ttk.Button(frame_button, text="Charger les paramètres", command=self.master.load_parameters, style='TkPlotCanvas.TButton')
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


    def fill__frame_cartouche_menu(self):
        """Create the cartouche configuration tab with metadata selection controls."""
        label = ttk.Label(self.tab_cartouche, text="Paramètres du cartouche:", style='TkPlotCanvas.Titre_parammetre.TLabel')
        label.grid(row=0, column=0, sticky="w", padx=5, pady=10, columnspan=3 )

        # Checkbutton pour l'affichage du cartouche : 
        self.Is_cartouche_display_var = tk.BooleanVar(value= self.master.Is_cartouche_display ) 
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
        
        

        label = ttk.Label(self.tab_courbe, text="Paramètres des courbes:", style='TkPlotCanvas_Courbe.TLabel')
        label.grid(row=0, column=0, sticky="w", padx=5, pady=10, columnspan=6 )

        label = ttk.Label(self.tab_courbe, text="Couleur:", style='TkPlotCanvas_Courbe.TLabel').grid(row=1, column=0, sticky="w", padx=5, pady=5)
        label = ttk.Label(self.tab_courbe, text="Épaisseur de ligne:", style='TkPlotCanvas_Courbe.TLabel').grid(row=1, column=1, sticky="w", padx=5, pady=5)
        label = ttk.Label(self.tab_courbe, text="Style de ligne:", style='TkPlotCanvas_Courbe.TLabel').grid(row=1, column=2, sticky="w", padx=5, pady=5)
        label = ttk.Label(self.tab_courbe, text="Marqueur:", style='TkPlotCanvas_Courbe.TLabel').grid(row=1, column=3, sticky="w", padx=5, pady=5)
        label = ttk.Label(self.tab_courbe, text="Taille du marqueur:", style='TkPlotCanvas_Courbe.TLabel').grid(row=1, column=4, sticky="w", padx=5, pady=5)

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
        color_code = colorchooser.askcolor(parent = self, title="Choisir une couleur")
        
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
           self.master._lines[index].set_marker(value_marker)
        elif property_name == 'markersize':
            value_markersize = self.list_widget[index][4].get()
            self.master._lines[index].set_markersize(float(value_markersize))

        self.master._canvas.draw()

        line_string  = ""
        color = self.master._lines[index].get_color()

        # Update the cartouch :
        if value_linestyle == '-':
            value_linestyle = "―"
            
            
        line_string = f"{value_linestyle}" if value_linestyle != "None" else ""
        line_string += f"{value_marker}" if value_marker != "None" else ""

        self.master._cartouche_grid[index][0].configure(text=line_string, background=self.master.bg_color_graph, foreground=color, width=3, font=("Helvetica", 15, 'bold'))
           


    def fill__frame_axes(self):
        """Create the axes and title configuration tab with controls for labels, limits, and scale."""
        
        ttk.Label(self.tab_axes, text="Modification des axes et titres:", style='Titre_parammetre.TLabel').grid(row=0, column=0, sticky="w", padx=5, pady=10, columnspan=2)

        # Add controls for axes and title here
        padx_axes = (5, 5)
        pady_axes = (5, 5)

        # To keep track of the current column index for placing frames in the axes tab
        self.column_frame_axes = 0 

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
        if len(self.master.list_data_xarray) > 0 :
            list_dimension = list(self.master.list_data_xarray[0].dims)
            list_variable = list(self.master.list_data_xarray[0].data_vars)
            list_variables_xarray = list_dimension + ["---------"] + list_variable

        self.dict_axis_widget = dict()

        self.dict_axis_widget["x"] = {
            "label_var": tk.StringVar(value= self.master.axes.get_xlabel()),
            "lim_min_var": tk.StringVar(value= self.master.axes.get_xlim()[0].round(4) ),
            "lim_max_var": tk.StringVar(value= self.master.axes.get_xlim()[1].round(4) ),
            "scale_var": tk.StringVar(value= self.master.axes.get_xscale() ),
            "auto_scale_var": tk.BooleanVar(value= self.master.axes.get_autoscalex_on() ),
            "combobox_variable" : None,
            "innversion_axe_var" : tk.BooleanVar(value= bool(self.master.axes.xaxis_inverted()) ),
        }

        self.dict_axis_widget["y"] = {
            "label_var": tk.StringVar(value= self.master.axes.get_ylabel()),
            "lim_min_var": tk.StringVar(value= self.master.axes.get_ylim()[0].round(4) ),
            "lim_max_var": tk.StringVar(value= self.master.axes.get_ylim()[1].round(4) ),
            "scale_var": tk.StringVar(value= self.master.axes.get_yscale() ),
            "auto_scale_var": tk.BooleanVar(value= self.master.axes.get_autoscaley_on() ),
            "combobox_variable" : None,
            "innversion_axe_var" : tk.BooleanVar(value= bool(self.master.axes.yaxis_inverted() )),
        }
                
        self._create_LabelFrame_axes("x", "Abscisse", self.dict_axis_widget["x"], list_variables = list_variables_xarray)
        self._create_LabelFrame_axes("y", "Ordonnée", self.dict_axis_widget["y"], list_variables = list_variables_xarray)


        # Apply button to update axes and title:
        ttk.Button(self.tab_axes, text="Appliquer les changements", command=self._apply_axes_changes, width=20, style='TkPlotCanvas.TButton').grid(row=0, column=2, columnspan=2, padx=padx_axes, pady=pady_axes, sticky="we")

        
    def _create_LabelFrame_axes(self, name_frame, name_axis, dict_variable, list_variables = []) :
        """ Create a labeled frame for axes settings with a consistent style.

            name_frame: The title of the frame to create (e.g., "x", "y").
            name_axis: The name of the axis associated (e.g., "abscisse", "ordonnée") to label the entry for axis label.
            dict_variable: 
                label_var : the StringVar to link to the axis label entry,
                lim_min_var : the StringVar to link to the axis minimum limit entry,
                lim_max_var : the StringVar to link to the axis maximum limit entry,
                scale_var : the StringVar to link to the axis scale combobox. (e.g., "linear", "log"),
                auto_scale_var : the BooleanVar to link to the axis autoscale checkbutton.
                combobox_variable : Optional (if xarray data is loaded)
                
        """

        # Add controls for axes and title here
        padx_axes = (5, 5)
        pady_axes = (5, 5)

        # frame for X axis : 
        fame_axis = ttk.LabelFrame(self.tab_axes, text= f"Axe {name_frame.upper()}", padding=(10, 10), style='TkPlotCanvas.TLabelframe')
        fame_axis.grid(row=2, column=self.column_frame_axes, columnspan=2, sticky="we", padx=padx_axes, pady=pady_axes)
        ttk.Label(fame_axis, text=f"{name_axis}:", style='TkPlotCanvas.TLabel').grid(row=1, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        label_entry = ttk.Entry(fame_axis, textvariable= dict_variable["label_var"], width=25, style='TkPlotCanvas.TEntry')
        label_entry.grid(row=1, column=1, columnspan=2, padx=(0, 4), sticky="w")
            
        ttk.Separator(fame_axis, orient='horizontal').grid(row=5, column=0, columnspan=3, sticky="we", pady=(10, 10))

            # Modifier les axes : 
        ttk.Label(fame_axis, text="Valeur min:", style='TkPlotCanvas.TLabel').grid(row=6, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        ttk.Label(fame_axis, text="Valeur max:", style='TkPlotCanvas.TLabel').grid(row=7, column=0, sticky="e", padx=padx_axes, pady=pady_axes)

        entry_min = ttk.Entry(fame_axis, textvariable = dict_variable["lim_min_var"], width=15, style='TkPlotCanvas.TEntry')
        entry_min.grid(row=6, column=1, sticky="we")
        entry_min.bind('<KeyRelease>', lambda event: self.set_autoscale_false(axis=name_frame))  # Set autoscale to False when user types in the entry
        entry_min.bind("<Return>", lambda event: self._apply_axes_changes())  # Apply changes when Enter is pressed

        entry_max = ttk.Entry(fame_axis, textvariable = dict_variable["lim_max_var"], width=15, style='TkPlotCanvas.TEntry')
        entry_max.grid(row=7, column=1, sticky="we")  
        entry_max.bind('<KeyRelease>', lambda event: self.set_autoscale_false(axis=name_frame))  # Set autoscale to False when user types in the entry
        entry_max.bind("<Return>", lambda event: self._apply_axes_changes())  # Apply changes when Enter is pressed
        

        ttk.Label(fame_axis, text="Echelle:", style='TkPlotCanvas.TLabel').grid(row=8, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        ttk.Combobox(fame_axis, textvariable= dict_variable["scale_var"], values=["linear", "log"], state="readonly", width=8).grid(row=8, column=1, columnspan=2, sticky="we")
        
        checkbutton_autoscale = ttk.Checkbutton(fame_axis, text="Auto", variable = dict_variable["auto_scale_var"], command= partial(self._on_zoom_auto, axis = name_frame), width=5, style='TkPlotCanvas.TCheckbutton')
        checkbutton_autoscale.grid(row=6,column=2, rowspan=2, padx=padx_axes, pady=pady_axes, sticky="we")
        
        ttk.Label(fame_axis, text="Inversion axe:", style='TkPlotCanvas.TLabel').grid(row=9, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        checkbutton_inversion_axe = ttk.Checkbutton(fame_axis, variable = dict_variable["innversion_axe_var"], command = partial(self._on_inversion_axe, axis = name_frame), width=5, style='TkPlotCanvas.TCheckbutton')
        checkbutton_inversion_axe.grid(row=9,column=1,  padx=padx_axes, pady=pady_axes, sticky="we")

        ttk.Separator(fame_axis, orient='horizontal').grid(row=20, column=0, columnspan=3, sticky="we", pady=(10, 10))

            # Bouton police : 
        button_font_label = ttk.Button(fame_axis, text="Modifier la police", 
                            command= partial(Window_font_parameter, self, frame_to_modifiy= f"{name_frame}label"), style='TkPlotCanvas.TButton' )
        button_font_label.grid(row=21, column=0, columnspan=3, padx=(5, 5), sticky="ew")

            # If the xarray data is loaded, add the combobox to select the variable to show on the axis :
        if len(list_variables) > 0 :
            ttk.Label(fame_axis, text="Variable:", style='TkPlotCanvas.TLabel').grid(row=2, column=0, sticky="e", padx=padx_axes, pady=pady_axes)
        
            dict_variable["combobox_variable"] = ttk.Combobox(fame_axis, values= list_variables, state="readonly", width=20, style='Combobox_variable.TCombobox')
            dict_variable["combobox_variable"].grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="we")
            index = list_variables.index(self.master.xarray_data[name_frame]) if self.master.xarray_data[name_frame] in list_variables else 0
            dict_variable["combobox_variable"].current(index)  # Set to the first dimension by default

            # Update the column index for the next frame
        self.column_frame_axes += 2

    def set_autoscale_false(self, event=None, axis=""):
        """Set the autoscale checkboxes to False when the user manually changes axis limits."""
        
        self.dict_axis_widget[axis]["auto_scale_var"].set(False)
    
    def _on_inversion_axe(self, event=None, axis=""):
        """Invert the specified axis when the inversion checkbox is toggled."""
        if axis == "x":
            self.master.axes.invert_xaxis()
        elif axis == "y":
            self.master.axes.invert_yaxis()
        self.master._canvas.draw()

    def _apply_axes_changes(self):
        """Apply the axes, title, and xarray selection changes from the axes tab."""
  
        current_font = self.master.axes.title.get_fontproperties()
        current_color = self.master.axes.title.get_color()
        self.master.axes.set_title(self._title_var.get(), fontfamily=current_font.get_name(), fontsize=current_font.get_size(), fontstyle=current_font.get_style(), fontweight=current_font.get_weight(), color=current_color)
        self.master.axes.set_xlabel(self.dict_axis_widget["x"]["label_var"].get())
        self.master.axes.set_ylabel(self.dict_axis_widget["y"]["label_var"].get())

        # TODO : utiliser une liste "additional y axes"
        
        # if list_data_xarray is not empty, update the x and y variables based on the combobox selection
        if len(self.master.list_data_xarray) > 0 :
            # Show the variable selected from comboboxes if they are not already shown
                # Get the selected variable from the comboboxes
            selected_variable_x = self.dict_axis_widget["x"]["combobox_variable"].get()
            selected_variable_y = self.dict_axis_widget["y"]["combobox_variable"].get()   
            list_variable = list(self.master.list_data_xarray[0].data_vars) + list(self.master.list_data_xarray[0].dims)
            Is_variable_modified = False
                # Update the master variables with the selected variables
            if selected_variable_x != self.master.xarray_data["x"] and selected_variable_x in list_variable:
                Is_variable_modified = True
                self.master.xarray_data["x"] = selected_variable_x
            if selected_variable_y != self.master.xarray_data["y"] and selected_variable_y in list_variable:
                Is_variable_modified = True
                self.master.xarray_data["y"] = selected_variable_y   

            if Is_variable_modified:
                # Save the current parameter_vue : 
                self.master.parametre_vue = self.master.get_current_parameters()

                # Update the plot to reflect the variable change   
                self.master.update_plot()           


        # Mise à jour de l'échelle : 
        # Get the new axis limits and scale types from the entries and comboboxes, and apply them to the plot.
        try:
            x_min = float(self.dict_axis_widget["x"]["lim_min_var"].get()) if self.dict_axis_widget["x"]["lim_min_var"].get() else None
            x_max = float(self.dict_axis_widget["x"]["lim_max_var"].get()) if self.dict_axis_widget["x"]["lim_max_var"].get() else None
            y_min = float(self.dict_axis_widget["y"]["lim_min_var"].get()) if self.dict_axis_widget["y"]["lim_min_var"].get() else None
            y_max = float(self.dict_axis_widget["y"]["lim_max_var"].get()) if self.dict_axis_widget["y"]["lim_max_var"].get() else None

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
                self.master.axes.set_xscale(self.dict_axis_widget["x"]["scale_var"].get())
            self.master.axes.set_yscale(self.dict_axis_widget["y"]["scale_var"].get())
            
        except ValueError:
            tk.messagebox.showerror("Invalid input", "Please enter valid numeric values for axis limits.")

        # Update the autoscale settings based on the checkboxes
        if self.dict_axis_widget["x"]["auto_scale_var"].get() :
            self.master.axes.autoscale(axis="x", tight=True)
        if self.dict_axis_widget["y"]["auto_scale_var"].get() :
            self.master.axes.autoscale(axis="y", tight=True)

        self.master._canvas.draw()
    
    def _on_zoom_auto(self, axis="both", tight=True):
        self.master.axes.autoscale(axis=axis, tight=tight)
        self.master._canvas.draw()

        # Update the entries for axis limits with the new autoscaled limits
        self.dict_axis_widget["x"]["lim_min_var"].set(self.master.axes.get_xlim()[0].round(4))
        self.dict_axis_widget["x"]["lim_max_var"].set(self.master.axes.get_xlim()[1].round(4))

        self.dict_axis_widget["y"]["lim_min_var"].set(self.master.axes.get_ylim()[0].round(4))
        self.dict_axis_widget["y"]["lim_max_var"].set(self.master.axes.get_ylim()[1].round(4))



    def fill__frame_legende(self):
        """Create the legend settings tab with controls to show/hide and customize legend entries."""
        ttk.Label(self.tab_legende, text="Paramètres de la légende:", style='Titre_parammetre.TLabel').grid(row=0, column=0, sticky="w", padx=5, pady=10, columnspan=2)
        
        # Checkbutton to show/hide legend on the canvas
        self.checkbutton_var_legende = tk.BooleanVar(value=self.master.axes.get_legend() is not None)
        checkbutton_show_legend = ttk.Checkbutton(self.tab_legende, text="Afficher la légende", variable=self.checkbutton_var_legende, command=self._toggle_legend, style='TkPlotCanvas.TCheckbutton')
        checkbutton_show_legend.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        
        # Checkbutton to show/hide the column titles in the legend
        self.checkbutton_var_title_column_legende = tk.BooleanVar(value = self.master.Is_title_display)
        checkbutton_title_column_legende = ttk.Checkbutton(self.tab_legende, text="Afficher les titres des colonnes", variable=self.checkbutton_var_title_column_legende, command=self._toggle_legend, style='TkPlotCanvas.TCheckbutton')
        checkbutton_title_column_legende.grid(row=1, column=2, columnspan=2, sticky="w", padx=5, pady=5)

        # Button to optimize (Automatically) the legend position (only if legend is shown)
        ttk.Button(self.tab_legende, text="Position par défaut", command=self._optimize_legend_position, style='TkPlotCanvas.TButton').grid(row=0, column=4, columnspan=2, sticky="we", padx=5, pady=5)

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

                entry_key.bind("<KeyRelease>", partial(self._toggle_entry, row =index, column= column_index))  # Update legend when entry is modified

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

        self._toggle_legend()  # Update the legend display based on the new selection

    def _toggle_legend(self, event=None):
        """Show or hide the legend on the canvas based on the checkbutton state."""

        # Update the legend_to_show list with the new values for this line
        self.master.legend_to_show = self.get_legende_to_show()

        # Update the master variable for title display in legend based on the checkbutton state
        self.master.Is_title_display = self.checkbutton_var_title_column_legende.get()

        # Update the master variable for legend display based on the checkbutton state
        self.master.Is_legend_display = self.checkbutton_var_legende.get()

        # Update the legende : 
        self.master._update_legende()

    def get_legende_to_show(self):
        """Return the list of metadata keys to show in the legend based on the combobox selections."""
        return [self.list_combobox_legende[i].get() for i in range(len(self.list_combobox_legende)) if self.list_combobox_legende[i].get() != ""]  # Only include non-empty selections
    
    def _toggle_entry(self, event=None, row=None, column=None):
        """Update the legend display when an entry widget is modified."""
        
        name_column = self.master.legend_to_show[column] if column < len(self.master.legend_to_show) else ""
        
        if name_column != "" and row is not None and column is not None:
            entry_widget = self.list_entry_legende[row][column]
            value = entry_widget.get()
            self.master._line_labels[row][name_column] = value  # Update the label dict for this line with the new value

        # Update the legende : 
        self._toggle_legend()

    def _optimize_legend_position(self):
        if self.checkbutton_var_legende.get():
            self.master.axes.legend(loc='best', draggable=True)  # Automatically choose the best location for the legend
           
        else : 
            self.master.axes.legend(loc=None, draggable=True )  # Remove legend from the axes but keep it draggable
       
        self.master._canvas.draw()

    def fill__frame_courbe_3D(self):
        """Create the 3D curve settings tab with controls for 3D plot properties."""
        ttk.Label(self.tab_courbe, text="Paramètres de la courbe 3D:", style='Titre_parammetre.TLabel').grid(row=0, column=0, sticky="w", padx=5, pady=10, columnspan=2)
        
        # Add controls for 3D curve properties here
        pass

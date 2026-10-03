"""Axes and title settings for the graphical plot menu."""

import tkinter as tk
from functools import partial
from tkinter import ttk

from .class_window_font_parameter import Window_font_parameter


class AxesSettingsMixin:
    """Build and apply the axes and title settings tab."""

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
        else :
            list_variables_xarray = []

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

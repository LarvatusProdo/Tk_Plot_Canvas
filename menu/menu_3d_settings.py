"""3D plot settings panel and related parameter dialogs."""

from functools import partial
import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt

from class_frame_choix_class import choix_classe
from .class_window_font_parameter import Window_font_parameter


class Graphique3DSettingsMixin:
    """Build and manage the 3D plot settings panel."""

    def fill__frame_courbe_3D(self):
        """Create the 3D curve settings tab with controls for 3D plot properties."""
        ttk.Label(self.tab_courbe, text="Paramètres du graphique 3D:", style='Titre_parammetre.TLabel').grid(row=0, column=0, sticky="w", padx=5, pady=10, columnspan=10)

        ttk.Label(self.tab_courbe, text="Indice", style='TkPlotCanvas_Courbe.TLabel').grid(row=1, column=1,  padx=5, pady=5)
        ttk.Label(self.tab_courbe, text="Variable affichée", style='TkPlotCanvas_Courbe.TLabel').grid(row=1, column=5, padx=5, pady=5)
        ttk.Label(self.tab_courbe, text="Plage de valeur", style='TkPlotCanvas_Courbe.TLabel').grid(row=1, column=10, padx=5, pady=5)
        ttk.Label(self.tab_courbe, text="Couleur", style='TkPlotCanvas_Courbe.TLabel').grid(row=1, column=20,  padx=5, pady=5)
        ttk.Label(self.tab_courbe, text="Transparence", style='TkPlotCanvas_Courbe.TLabel').grid(row=1, column=30, padx=5, pady=5)
        ttk.Label(self.tab_courbe, text="Afficahge colorbar", style='TkPlotCanvas_Courbe.TLabel').grid(row=1, column=40, padx=5, pady=5)
        ttk.Label(self.tab_courbe, text="Paramêtre colorbar", style='TkPlotCanvas_Courbe.TLabel').grid(row=1, column=50, padx=5, pady=5)

        self.checkbutton_map_show_var = tk.BooleanVar(value=self.master.plot_3D_map)
        self.checkbutton_map_show = ttk.Checkbutton(
            self.tab_courbe,
            text="Affichage d'une carte",
            variable=self.checkbutton_map_show_var,
            command=self._affichage_carte,
        )
        self.checkbutton_map_show.grid(row=0, column=20, padx=5, pady=5)

        self.list_widget = {}
        for index, line in enumerate(self.master._lines):
            self.affiche_parametres_courbe_3D(line, index)

    def affiche_parametres_courbe_3D(self, line, index):
        """Create controls for the selected 3D plot and its colorbar."""
        if len(self.master.list_data_xarray) == 0:
            return

        padx_axes = (10, 10)
        pady_axes = (10, 10)
        self.list_widget[str(index)] = {}
        map_object = self.master._lines[index]

        ttk.Label(self.tab_courbe, text=str(index + 1), style='TkPlotCanvas_Courbe.TLabel').grid(row=index + 2, column=1, sticky="w", padx=padx_axes, pady=pady_axes)

        list_variables = list(self.master.list_data_xarray[0].data_vars)
        self.list_widget[str(index)]["combobox_variable"] = ttk.Combobox(self.tab_courbe, values=list_variables, state="readonly", width=20, style='Combobox_variable.TCombobox')
        self.list_widget[str(index)]["combobox_variable"].grid(row=index + 2, column=5, columnspan=2, sticky="w", padx=padx_axes, pady=pady_axes)
        self.list_widget[str(index)]["combobox_variable"].current(list_variables.index(self.master.xarray_data["z"]) if self.master.xarray_data["z"] in list_variables else 0)
        self.list_widget[str(index)]["combobox_variable"].bind("<<ComboboxSelected>>", lambda event, idx=index: self._update_z_variable(idx))

        button_value_range = ttk.Button(self.tab_courbe, text="Valeurs", command=partial(self._window_parametre_value_range, index=index), style='TkPlotCanvas.TButton')
        button_value_range.grid(row=index + 2, column=10, sticky="w", padx=padx_axes, pady=pady_axes)

        list_colormap = sorted([m for m in plt.colormaps() if not m.endswith("_r")], key=str.lower)
        self.list_widget[str(index)]["combobox_colormap"] = ttk.Combobox(self.tab_courbe, values=list_colormap, state="readonly", width=20, style='Combobox_variable.TCombobox')
        self.list_widget[str(index)]["combobox_colormap"].grid(row=index + 2, column=20, columnspan=2, sticky="w", padx=padx_axes, pady=pady_axes)
        self.list_widget[str(index)]["combobox_colormap"].current(list_colormap.index(map_object.get_cmap().name) if map_object.get_cmap().name in list_colormap else 0)
        self.list_widget[str(index)]["combobox_colormap"].bind("<<ComboboxSelected>>", lambda event, idx=index: self._update_colormap(idx))

        self.list_widget[str(index)]["Spinbox_alpha_var"] = tk.StringVar(value=str(line.get_alpha()) if line.get_alpha() is not None else "1.0")
        self.list_widget[str(index)]["Spinbox_alpha"] = ttk.Spinbox(
            self.tab_courbe,
            from_=0.0,
            to=1.0,
            increment=0.05,
            width=5,
            style='TkPlotCanvas.TSpinbox',
            textvariable=self.list_widget[str(index)]["Spinbox_alpha_var"],
        )
        self.list_widget[str(index)]["Spinbox_alpha"].grid(row=index + 2, column=30, columnspan=2, sticky="w", padx=padx_axes, pady=pady_axes)
        self.list_widget[str(index)]["Spinbox_alpha"].bind("<Return>", lambda event, idx=index: self._update_alpha(idx))
        self.list_widget[str(index)]["Spinbox_alpha"].bind("<FocusOut>", lambda event, idx=index: self._update_alpha(idx))
        self.list_widget[str(index)]["Spinbox_alpha"].bind("<KeyRelease>", lambda event, idx=index: self._update_alpha(idx))
        self.list_widget[str(index)]["Spinbox_alpha"].bind("<MouseWheel>", lambda event, idx=index: self._update_alpha(idx))
        self.list_widget[str(index)]["Spinbox_alpha"].bind("<ButtonRelease-1>", lambda event, idx=index: self._update_alpha(idx))

        self.list_widget[str(index)]["checkbutton_colorbar_var"] = tk.BooleanVar(value=getattr(self.master, "_colorbar", None) is not None)
        self.list_widget[str(index)]["checkbutton_colorbar"] = ttk.Checkbutton(self.tab_courbe, text="Afficher", variable=self.list_widget[str(index)]["checkbutton_colorbar_var"], style='TkPlotCanvas.TCheckbutton')
        self.list_widget[str(index)]["checkbutton_colorbar"].grid(row=index + 2, column=40, sticky="w", padx=padx_axes, pady=pady_axes)
        self.list_widget[str(index)]["checkbutton_colorbar"].bind("<ButtonRelease-1>", lambda event, idx=index: self._toggle_colorbar(idx))

        button_colorbar_param = ttk.Button(self.tab_courbe, text="Modifier colorbar", command=partial(self._window_parametre_colorbar, index), style='TkPlotCanvas.TButton')
        button_colorbar_param.grid(row=index + 2, column=50, sticky="w", padx=padx_axes, pady=pady_axes)

    def _window_parametre_colorbar(self, index):
        """Open a new window to modify the colorbar parameters."""
        if getattr(self.master, "_colorbar", None) is not None:
            Window_colorbar_parameter(self, self.master._colorbar, index)

    def _window_parametre_value_range(self, index):
        """Open a new window to modify the value range or contour levels."""
        if index < len(self.master._lines):
            line = self.master._lines[index]
            Window_value_range_parameter(self, line, index)

    def _toggle_colorbar(self, index):
        """Show or hide the colorbar for the specified 3D plot."""
        line = self.master._lines[index]
        show_colorbar = self.list_widget[str(index)]["checkbutton_colorbar_var"].get()

        if not show_colorbar:
            self.master._colorbar = self.master.figure.colorbar(line, ax=self.master.axes, orientation='vertical')
            if getattr(self, "current_label_colorbar", None) is not None:
                label_colorbar = self.current_label_colorbar
            else:
                label_colorbar = ""

            self.master._colorbar.set_label(label_colorbar.capitalize() if self.list_widget[str(index)]["combobox_variable"] is not None else "")
        else:
            if getattr(self.master, "_colorbar", None) is not None:
                self.current_label_colorbar = self.master._colorbar.ax.get_ylabel()

            self.master._colorbar.remove()

        self.master._canvas.draw()

    def _update_colormap(self, index):
        """Update the colormap for the specified 3D plot."""
        line = self.master._lines[index]
        selected_colormap = self.list_widget[str(index)]["combobox_colormap"].get()
        line.set_cmap(selected_colormap)
        self.master._canvas.draw()

    def _update_alpha(self, index):
        """Update the alpha (transparency) for the specified 3D plot."""
        line = self.master._lines[index]
        try:
            new_alpha = float(self.list_widget[str(index)]["Spinbox_alpha_var"].get())
            if 0.0 <= new_alpha <= 1.0:
                line.set_alpha(new_alpha)
                self.master._canvas.draw()
            else:
                raise ValueError("Alpha must be between 0.0 and 1.0")
        except ValueError:
            tk.messagebox.showerror("Invalid input", "Please enter a valid numeric value for alpha between 0.0 and 1.0.")

    def _update_z_variable(self, index):
        """Update the Z variable for the specified 3D plot."""
        selected_variable = self.list_widget[str(index)]["combobox_variable"].get()
        if selected_variable in self.master.list_data_xarray[index].data_vars:
            self.master.xarray_data["z"] = selected_variable
            self.master.parametre_vue = self.master.get_current_parameters()
            self.master.update_plot()

    def _affichage_carte(self):
        self.master.plot_3D_map = self.checkbutton_map_show_var.get()
        self.master.update_plot(is_map=self.master.plot_3D_map)


class Window_colorbar_parameter(tk.Toplevel):
    def __init__(self, parent, colorbar, index=0):
        super().__init__(parent)
        self.title("Paramètres de la colorbar")
        self.geometry(f"400x450+{self.master.winfo_x() + 50}+{self.master.winfo_y() + 50}")
        self.colorbar = colorbar
        self.index = index
        if self.colorbar.orientation == "vertical":
            label_colorbar = self.colorbar.ax.get_ylabel() if self.colorbar.ax.get_ylabel() is not None else ""
        else:
            label_colorbar = self.colorbar.ax.get_xlabel() if self.colorbar.ax.get_xlabel() is not None else ""

        frame_colorbar_params = ttk.LabelFrame(self, text="Paramètres de la colorbar", padding=(10, 10), style='TkPlotCanvas.TLabelframe')
        frame_colorbar_params.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(frame_colorbar_params, text="Label:", style='TkPlotCanvas.TLabel').grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.label_var = tk.StringVar(value=label_colorbar)
        ttk.Entry(frame_colorbar_params, textvariable=self.label_var, width=30, style='TkPlotCanvas.TEntry').grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.label_var.trace_add("write", self.update_colorbar_label)

        button_font_label = ttk.Button(frame_colorbar_params, text="Modifier la police", command=partial(Window_font_parameter, self.master, frame_to_modifiy="colorbar label"), style='TkPlotCanvas.TButton')
        button_font_label.grid(row=10, column=0, columnspan=3, sticky="we", padx=5, pady=5)

        ttk.Separator(frame_colorbar_params, orient='horizontal').grid(row=20, column=0, columnspan=3, sticky="we", pady=(10, 10))

        ttk.Label(frame_colorbar_params, text="Orientation:", style='TkPlotCanvas.TLabel').grid(row=30, column=0, sticky="e", padx=5, pady=5)
        self.orientation_var = tk.StringVar(value=self.colorbar.orientation)
        ttk.Combobox(frame_colorbar_params, values=["vertical", "horizontal"], textvariable=self.orientation_var, state="readonly", width=15).grid(row=30, column=1, sticky="w", padx=5, pady=5)

        ttk.Separator(frame_colorbar_params, orient='horizontal').grid(row=99, column=0, columnspan=3, sticky="we", pady=(10, 10))
        ttk.Button(frame_colorbar_params, text="Appliquer", command=self.apply_changes).grid(row=100, column=0, columnspan=2, sticky="we", pady=(10, 10))

    def apply_changes(self):
        """Apply the changes to the colorbar based on user input."""
        new_label = self.label_var.get()
        new_orientation = self.orientation_var.get()
        if self.colorbar.orientation == "vertical":
            current_font = self.colorbar.ax.yaxis.label.get_fontproperties()
        else:
            current_font = self.colorbar.ax.xaxis.label.get_fontproperties()

        self.colorbar.ax.set_ylabel(new_label)

        if new_orientation != self.colorbar.orientation:
            try:
                self.colorbar.remove()
            except Exception:
                return

            self.master.master._colorbar = self.master.master.figure.colorbar(self.master.master._lines[self.index], ax=self.master.master.axes, orientation=new_orientation)
            self.master.master._colorbar.set_label(new_label, fontproperties=current_font)

        self.master.master._canvas.draw()
        self.destroy()

    def update_colorbar_label(self, *args):
        """Update the colorbar label in real-time as the user types in the entry."""
        new_label = self.label_var.get()
        self.colorbar.ax.set_ylabel(new_label)
        self.master.master._canvas.draw()


class Window_value_range_parameter(tk.Toplevel):
    def __init__(self, parent, line, index):
        super().__init__(parent)
        self.title("Paramètres de la plage de valeurs")
        self.geometry(f"400x500+{self.master.winfo_x() + 50}+{self.master.winfo_y() + 50}")

        self.line = line
        self.index = index

        frame_value_range_params = ttk.LabelFrame(self, text="Plage de valeurs", padding=(10, 10), style='TkPlotCanvas.TLabelframe')
        frame_value_range_params.pack(fill=tk.BOTH, padx=10, pady=10, side=tk.TOP)

        ttk.Label(frame_value_range_params, text="Valeur min:", style='TkPlotCanvas.TLabel').grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.vmin_var = tk.StringVar(value=str(self.line.get_clim()[0]))
        ttk.Entry(frame_value_range_params, textvariable=self.vmin_var, width=15, style='TkPlotCanvas.TEntry').grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame_value_range_params, text="Valeur max:", style='TkPlotCanvas.TLabel').grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.vmax_var = tk.StringVar(value=str(self.line.get_clim()[1]))
        ttk.Entry(frame_value_range_params, textvariable=self.vmax_var, width=15, style='TkPlotCanvas.TEntry').grid(row=1, column=1, sticky="w", padx=5, pady=5)

        frame_button_apply = ttk.Frame(self)
        frame_button_apply.pack(fill=tk.BOTH, padx=10, pady=10, side=tk.BOTTOM)
        ttk.Button(frame_button_apply, text="Appliquer", command=self.apply_changes).pack(expand=True, fill=tk.X)

        labelframe_choix_class = ttk.LabelFrame(self, text="Choix des classes :", padding=(10, 10), style='TkPlotCanvas.TLabelframe')
        labelframe_choix_class.pack(fill=tk.BOTH, expand=True, padx=10, pady=10, side=tk.TOP)

        levels_graph = list(map(float, self.line.levels))
        self.frame_choix_classe = choix_classe(
            labelframe_choix_class,
            v_max=self.vmax_var.get(),
            v_min=self.vmin_var.get(),
            nb_classes=len(levels_graph) - 1,
            classes=levels_graph,
            type_class=self.master.master.plot_3D_classe,
        )
        self.frame_choix_classe.pack(fill=tk.BOTH)

    def apply_changes(self):
        """Apply the changes to the value range based on user input."""
        self.master.master.plot_3D_classe, classes = self.frame_choix_classe.get_classes()

        if classes != []:
            self.master.master._replace_contour_levels(classes, index=self.index)
            self.master.master._canvas.draw()
            self.destroy()
        else:
            try:
                new_vmin = float(self.vmin_var.get())
                new_vmax = float(self.vmax_var.get())
                self.line.set_clim(vmin=new_vmin, vmax=new_vmax)
                self.master.master._canvas.draw()
                self.destroy()
            except ValueError:
                tk.messagebox.showerror("Invalid input", "Please enter valid numeric values for vmin and vmax.")

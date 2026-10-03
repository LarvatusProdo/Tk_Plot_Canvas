"""2D curve settings panel for the graphical plot menu."""

from functools import partial
from tkinter import colorchooser, ttk
import tkinter as tk


class CurveSettingsMixin:
    """Build and manage the 2D curve settings panel."""

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

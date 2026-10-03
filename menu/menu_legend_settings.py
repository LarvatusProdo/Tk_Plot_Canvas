"""Legend settings panel for the graphical plot menu."""

import tkinter as tk
from functools import partial
from tkinter import ttk


class LegendSettingsMixin:
    """Build and manage the legend settings panel."""

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

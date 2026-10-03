"""Cartouche settings panel for the graphical plot menu."""

import tkinter as tk
from functools import partial
from tkinter import ttk

from .class_window_font_parameter import Window_font_parameter


class CartoucheSettingsMixin:
    """Build and manage the cartouche settings panel."""

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

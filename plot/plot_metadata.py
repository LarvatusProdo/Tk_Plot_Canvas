"""Legend and cartouche management for the Tk plot canvas."""

import tkinter as tk
from tkinter import ttk
from typing import Optional


class PlotMetadataMixin:
    """Manage curve metadata labels, the cartouche, and the legend."""

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
                try :
                    widget.destroy()
                except Exception:
                    pass
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

        if line_display and self.type_plot == "2D":
            # Add line show :
            line = self._lines[line_index]
            color = line.get_color()
            linestyle = line.get_linestyle() if line.get_linestyle() != "None" else ""
            if linestyle == '-':
                linestyle = "―"
            marker = line.get_marker() if line.get_marker() != "None" else ""

            self._cartouche_grid[line_index].append(tk.Label(self._cartouche_frame, text=f"{linestyle}{marker}", background=self.bg_color_graph, foreground=color, width=3, font=("Helvetica", 15, 'bold')))
            self._cartouche_grid[line_index][-1].grid(row= line_index + 1, column=0, sticky="w", padx=(5,0), pady=0)

        else :
            self._cartouche_grid[line_index].append(None)

        if not(label_to_display is None):
            # Add the values of the metadata in the cartouche
            column_index = 1
            for key, value in label_to_display.items():
                self._cartouche_grid[line_index].append(ttk.Label(self._cartouche_frame, text=str(value), style="Cartouche.TLabel"))
                self._cartouche_grid[line_index][-1].grid(row=line_index + 1, column=column_index, sticky="w", padx=5, pady=5)
                column_index += 1

    def get_string_legende(self, label_dict, shown_keys = False):
        """Build the legend string from a metadata dictionary based on selected display keys."""

        string_legende = []

        for key in self.legend_to_show :
            if key in label_dict :
                value = label_dict[key]

                if shown_keys:
                    string_legende.append(f"{key}: {value}")
                else:
                    string_legende.append(f"{value}")

        return ", ".join(string_legende)


    def _update_legende(self):
        """Refresh legend labels and redraw the legend when settings change."""

        for index, line in enumerate(self._lines):
            label_dict = self._line_labels[index]
            line.set_label(self.get_string_legende(label_dict, shown_keys=self.Is_title_display))  # Update line label based on legend entry values and whether to show key titles

        # Update legend to reflect changes if lines are in the canvas
        if self.Is_legend_display and len(self._lines) > 0:
            if len(self.legend_to_show) > 0:
                self.axes.legend(draggable=True)
            else :
                # If no keys are selected to show in the legend, remove the legend from the axes
                try :
                    legend = self.axes.get_legend()
                    if legend:
                        legend.remove()  # Hide legend if no keys are selected to show
                except Exception:
                    pass

        # If legend display is turned off, remove the legend from the axes if it exists
        elif not self.Is_legend_display and len(self._lines) > 0:
            legend = self.axes.get_legend()
            if legend:
                legend.remove()  # Hide legend

        self._canvas.draw()

    def update_cartouche_frame(self):
        """Update the cartouche frame to reflect any changes in the metadata of the plotted lines."""
        for index, line in enumerate(self._lines):
            label_dict = self._line_labels[index]
            self.fill_cartouche_frame(label_to_display=label_dict, line_index=index, line_display=True)

        pass

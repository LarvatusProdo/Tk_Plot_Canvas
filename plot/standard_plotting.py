"""Standard Matplotlib plotting methods for the Tk plot canvas."""

import copy
from typing import Iterable, Optional

from numpy import datetime64


class StandardPlotMixin:
    """Plot ordinary x/y sequences on a Tk plot canvas."""

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

        self.type_plot = "2D"

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

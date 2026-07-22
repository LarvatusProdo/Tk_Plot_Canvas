from tkinter import colorchooser
import tkinter as tk
from tkinter import ttk
from functools import partial

class Window_font_parameter(tk.Toplevel):
    """Dialog window to edit font properties for titles, axes, and cartouche labels."""

    def __init__(self, master, frame_to_modifiy=""):
        super().__init__(master)
        self.title(f"Modification du {frame_to_modifiy}")
        self.geometry(f"400x450+{self.master.winfo_x() + 50}+{self.master.winfo_y() + 50}")

        self.frame_window = ttk.Frame(self, style='TkPlotCanvas.TFrame')
        self.frame_window.pack(fill="both", expand=True, anchor="nw")

        self.button_apply = ttk.Button(self.frame_window, text="Appliquer les changement", style='TkPlotCanvas.TButton')

        self.padx_echelle = (5, 5)
        self.pady_echelle = (5, 5)

        self.list_police = []
        if frame_to_modifiy == "cartouche" : 
            # Filter to only fonts available in both Tkinter
            for family in tk.font.families():
                try:
                    tk.font.Font(family=family)
                    self.list_police.append(family)
                except tk.TclError:
                    pass
        else : 
            # Filter to only fonts available in both Matplotlib
            self.list_police = self.master.master.list_font_matplotlib

        self.list_police.sort()  # Sort the list of fonts alphabetically
            

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
        
        combo_police = ttk.Combobox(label_frame, values= self.list_police, state="readonly", width=20)
        combo_police.grid(row=row_start, column=column_start + 1, sticky="w", columnspan=2, padx=5, pady=5)
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

        
        try :
            int(style_font[1])
        except ValueError :
            # If the second element is not an integer, it means the font string is in a different format (e.g., ['{Arial', 'Greek}', '14', 'bold']), so we need to parse it differently.
            style_font_buff = style["font"].split(" ")
            style_font = ["","",""]
            style_font[0] = style_font_buff[0][1:] + " " + style_font_buff[1][:-1]
            style_font[1] = style_font_buff[2]
            style_font[2] = style_font_buff[3]
            
        try:
            int(style_font[1])
        except ValueError:
            style_font = [self.master.master.font_default, "12", "normal"]  # Default values if parsing fails

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

        index_police = self.list_police.index(current_font.get_name()) if current_font.get_name() in self.list_police else 0
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
            index_police = self.list_police.index(axe.get_ticklabels()[0].get_fontname()) if axe.get_ticklabels()[0].get_fontname() in self.list_police else 0
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
                objet_axis.set_xlabel(self.master.dict_axis_widget["x"]["label_var"].get(), fontfamily= police, fontsize=size, fontstyle=style, fontweight=weight, color=color)
                axe = objet_axis.xaxis
                for tick in axe.get_ticklabels():
                    tick.set_fontname(police_tick)
                    tick.set_fontsize(size_tick)
                    tick.set_fontstyle(style_tick)
                    tick.set_fontweight(weight_tick)
                    tick.set_color(color_tick)

            elif nom_axe == "ylabel":
                objet_axis.set_ylabel(self.master.dict_axis_widget["y"]["label_var"].get(), fontfamily= police, fontsize=size, fontstyle=style, fontweight=weight, color=color)
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
        color_code = colorchooser.askcolor(parent = self, title="Choisir une couleur de police")
        if color_code:
            # Update the color button background
           widget.configure(bg=color_code[1])  # Update button color

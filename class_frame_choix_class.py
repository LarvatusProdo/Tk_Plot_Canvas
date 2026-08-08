import tkinter as tk
from tkinter import ttk

class choix_classe(ttk.Frame):

    def __init__(self, master, *args, classes = [], **kwargs):

        super().__init__(master, *args, **kwargs)

        # Frame : choix du type de classe : Auto / Manuel / Aucune
        self._frame_choix_class = ttk.LabelFrame(self, text="Choix du type de classe", style='TkPlotCanvas.TLabelframe')
        self._frame_choix_class.pack(side="top", fill="x", padx=5, pady=5)

        # Label : Choix du type de classe
        self._label_choix_class = ttk.Label(self._frame_choix_class, text="Choisir le type de classe :", style='TkPlotCanvas.TLabel')
        self._label_choix_class.pack(side="left", padx=5, pady=5)

        # Combobox : Choix du type de classe
        self._combobox_choix_class = ttk.Combobox(self._frame_choix_class, values=["Auto", "Manuel", "Aucune"], state="readonly", style='TkPlotCanvas.TCombobox')
        self._combobox_choix_class.current(0)  # Set default value to "Auto"
        self._combobox_choix_class.pack(side="left", padx=5, pady=5)
        self._combobox_choix_class.bind("<<ComboboxSelected>>", self.show_frame_choix_class)
        
        self.padx_label = (10, 5)
        self.pady_label = (5, 5)

        # Frame pour la classe : Auto
        self.frame_auto = ttk.Frame(self)
        self.fill_frame_auto(n_classes=10)  # Fill the frame for the 'Auto' class with default number of classes
        

        # Frame pour la classe : Manuel
        self.frame_manuel = ttk.Frame(self)
        self.fill_frame_manuel(classes = classes)  # Fill the frame for the 'Manuel' class

        self.show_frame_choix_class()  # Show the appropriate frame based on the default selection in the combobox

    def fill_frame_auto(self, n_classes=10):
        """Fill the frame for the 'Auto' class with the specified number of classes."""
        
        self.label_auto = ttk.Label(self.frame_auto, text="Paramètres pour la classe Auto", style='Titre_parammetre.TLabel')
        self.label_auto.grid(row=0, column=0, columnspan=2, pady=5)

        ttk.Label(self.frame_auto, text="Nombre de classes :", style='TkPlotCanvas.TLabel').grid(row=1, column=0, sticky="e", padx=self.padx_label, pady=self.pady_label)
        self.spinner_n_classes = ttk.Spinbox(self.frame_auto, from_=1, to=10000, width=5, style='TkPlotCanvas.TSpinbox')
        self.spinner_n_classes.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.spinner_n_classes.set(n_classes)  # Set default value to 10

    def fill_frame_manuel(self, classes=[]):
        """Fill the frame for the 'Manuel' class with the appropriate widgets.
        if classes = [0, 1, 2, 3] : 
        
        - n°1 : [0 , 1]
        - n°2 : [1* , 2]  # * indicates that the class is selected by default
        - n°3 : [2* , 3]  # * indicates that the class is selected by default
        
        
        """
        
        self.label_manuel = ttk.Label(self.frame_manuel, text="Paramètres pour la classe Manuel", style='Titre_parammetre.TLabel')
        self.label_manuel.grid(row=0, column=0, columnspan=2, pady=5)

        if classes == [] : 
            # if no classes are provided, default class is created
            classes = [0, 1, 2]

        for i, class_value in enumerate(classes):

            if i == 0:
                ttk.Label(self.frame_manuel, text=f"n°{i+1} :", style='TkPlotCanvas.TLabel').grid(row=i+1, column=0, sticky="e", padx=self.padx_label, pady=self.pady_label)
                entry_class = ttk.Entry(self.frame_manuel, width=10, style='TkPlotCanvas.TEntry')
                entry_class.grid(row=i+1, column=1, sticky="w", padx=5, pady=5)
                entry_class.insert(0, str(class_value))  # Insert the class value into the entry

            elif i > 0 and i < len(classes) - 1:
                ttk.Label(self.frame_manuel, text=f"n°{i+1} :", style='TkPlotCanvas.TLabel').grid(row=i+1, column=0, sticky="e", padx=self.padx_label, pady=self.pady_label)
                entry_class = ttk.Entry(self.frame_manuel, width=10, style='TkPlotCanvas.TEntry')
                entry_class.grid(row=i+1, column=1, sticky="w", padx=5, pady=5)
                entry_class.insert(0, str(class_value))  # Insert the class value into the entry

            else : 
                ttk.Label(self.frame_manuel, text=f"n°{i+1} :", style='TkPlotCanvas.TLabel').grid(row=i+1, column=0, sticky="e", padx=self.padx_label, pady=self.pady_label)
                entry_class = ttk.Entry(self.frame_manuel, width=10, style='TkPlotCanvas.TEntry')
                entry_class.grid(row=i+1, column=1, sticky="w", padx=5, pady=5)
                entry_class.insert(0, str(class_value))  # Insert the class value into the entry


    def show_frame_choix_class(self, event=None):
        """Show the frame with the appropriate widgets based on the selected class type."""

        if self._combobox_choix_class.get() == "Auto":
            self.frame_manuel.pack_forget()
            self.frame_auto.pack(fill="x", padx=5, pady=5)

        elif self._combobox_choix_class.get() == "Manuel":
            self.frame_auto.pack_forget()
            self.frame_manuel.pack(fill="x", padx=5, pady=5)

        elif self._combobox_choix_class.get() == "Aucune":
            self.frame_auto.pack_forget()
            self.frame_manuel.pack_forget()

        
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test choix_class")
    choix_class_frame = choix_classe(root)
    choix_class_frame.pack(fill="both", expand=True)
    root.mainloop()
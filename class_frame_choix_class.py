import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox

class choix_classe(ttk.Frame):
    _initialized_style: bool = False

    def __init__(self, master, *args, classes = [], with_buttons=False, v_max = 1.0, v_min = 0.0, **kwargs):

        super().__init__(master, *args, **kwargs)

        if not self._initialized_style :
            self._initialized_style = True
            self._setup_styles()

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
        self.pady_label = (10, 10)

        # Frame pour la classe : Auto
        self.frame_auto = ttk.Frame(self)
        self.fill_frame_auto(n_classes=10, v_min = v_min, v_max = v_max)  # Fill the frame for the 'Auto' class with default number of classes
        

        # Frame pour la classe : Manuel
        self.frame_manuel = ttk.Frame(self)
        # state for manuel entries: list of (left_entry, right_entry, left_var, right_var)
        self.list_entries_manuel = []

        # flag to avoid recursion when programmatically updating linked entries
        self._updating_link = False

        self.fill_frame_manuel(classes = classes)  # Fill the frame for the 'Manuel' class

        self.show_frame_choix_class()  # Show the appropriate frame based on the default selection in the combobox

        if with_buttons:
            # Frame for buttons
            self.frame_buttons = ttk.Frame(self)
            self.frame_buttons.pack(side="bottom", fill="x", padx=5, pady=5)

            # Button: OK
            self.button_ok = ttk.Button(self.frame_buttons, text="Get classes", command=self.get_classes, style='TkPlotCanvas.TButton')
            self.button_ok.pack(side="right", padx=5, pady=5)

            # Button: Cancel
            self.button_cancel = ttk.Button(self.frame_buttons, text="Quitter", command=self.destroy, style='TkPlotCanvas.TButton')
            self.button_cancel.pack(side="right", padx=5, pady=5)

    def _setup_styles(self):
        """Setup custom styles for the widgets in this frame."""

        # Frame for "Manuel" classes : 
        self.style = ttk.Style()

        self.bg_frame_default = self.style.lookup("TFrame", "background")
        self.bg_frame_hover = "#e6f2ff"

        self.style.configure("choix_classe.TFrame", background=self.bg_frame_default)
        self.style.map(
            'choix_classe.TFrame',
            background=[('active', self.bg_frame_hover), ('!active', self.bg_frame_default)]
        )

        self.style.configure("choix_classe.TLabel", background=self.bg_frame_default)
        self.style.map(
            'choix_classe.TLabel',
            background=[('active', self.bg_frame_hover), ('!active', self.bg_frame_default)]
        )

        self.style.configure("choix_classe.TEntry", fieldbackground=self.bg_frame_default, background=self.bg_frame_default)
        self.style.map(
            'choix_classe.TEntry',
            fieldbackground=[('active', self.bg_frame_hover), ('!active', self.bg_frame_default)]
        )

    def fill_frame_auto(self, n_classes=10, v_max = 1.0, v_min = 0.0):
        """Fill the frame for the 'Auto' class with the specified number of classes."""
        
        self.label_auto = ttk.Label(self.frame_auto, text="Paramètres pour la classe : Auto", style='Titre_parammetre.TLabel')
        self.label_auto.grid(row=0, column=0, columnspan=2, sticky="w", padx=self.padx_label, pady=self.pady_label)

        # Nombre de classes :
        ttk.Label(self.frame_auto, text="Nombre de classes :", style='TkPlotCanvas.TLabel').grid(row=1, column=0, sticky="w", padx=self.padx_label, pady=self.pady_label)
        self.spinner_n_classes = ttk.Spinbox(self.frame_auto, from_=1, to=10000, width=10, style='TkPlotCanvas.TSpinbox', justify="center")
        self.spinner_n_classes.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.spinner_n_classes.set(n_classes)  # Set default value to 10

        # Valeur minimale :
        ttk.Label(self.frame_auto, text="Valeur minimale :", style='TkPlotCanvas.TLabel').grid(row=2, column=0, sticky="w", padx=self.padx_label, pady=self.pady_label)
        self.entry_v_min = ttk.Entry(self.frame_auto, width=10, style='TkPlotCanvas.TEntry', justify="center")
        self.entry_v_min.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.entry_v_min.insert(0, str(v_min))  # Set default value

        # Valeur maximale :
        ttk.Label(self.frame_auto, text="Valeur maximale :", style='TkPlotCanvas.TLabel').grid(row=3, column=0, sticky="w", padx=self.padx_label, pady=self.pady_label)
        self.entry_v_max = ttk.Entry(self.frame_auto, width=10, style='TkPlotCanvas.TEntry', justify="center")
        self.entry_v_max.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        self.entry_v_max.insert(0, str(v_max))  # Set default value

    def fill_frame_manuel(self, classes=[]):
        """Fill the frame for the 'Manuel' class with two Entry widgets per line.

        Behavior:
        - Each line shows two entries: left and right.
        - For middle lines (0 < i < n-1) the left entry is linked to the previous
          line's right entry and is disabled for user editing.
        - The first and last line left entries are editable.
        """

        if classes == []:
            classes = [0, 1, 2]  # Default values if no classes provided

        # Rebuild the manuel frame widgets from scratch
        self._build_manuel_frame(classes)


    def _build_manuel_frame(self, classes):
        """Build the frame for the 'Manuel' class with two Entry widgets per line."""
        # clear existing widgets
        for child in self.frame_manuel.winfo_children():
            child.destroy()

        self.list_entries_manuel = []

        # header label spans 3 columns now (label + left + right)
        self.label_manuel = ttk.Label(self.frame_manuel, text="Paramètres pour la classe : Manuel", style='Titre_parammetre.TLabel')
        self.label_manuel.pack(side="top", fill="x", padx=5, pady=5)

        frame_buttons = ttk.Frame(self.frame_manuel)
        frame_buttons.pack(side="top", fill="x", padx=5, pady=5)
        # Add a row at the end : 
        button_add_row_end = ttk.Button(frame_buttons, text="Ajouter une ligne à la fin", style='TkPlotCanvas.TButton', command=lambda: self._add_row_manuel(where="end", reconfigure_states=True))
        button_add_row_end.pack(side="left", padx=5, pady=5)

        """# Add a row at the beginning : 
        button_add_row_end = ttk.Button(frame_buttons, text="Ajouter une ligne au début", style='TkPlotCanvas.TButton', command=lambda: self._add_row_manuel(where="beginning", reconfigure_states=True))
        button_add_row_end.pack(side="left", padx=5, pady=5)"""

        n = len(classes)
        for i in range(n-1):
        
            # values: left is classes[i], right is classes[i+1] if exists else empty
            left_val = classes[i]
            right_val = classes[i+1] if i + 1 < n else ""

            self._add_row_manuel( n_row=i, left_val=left_val, right_val=right_val)

        # Configure the states of the entries after all rows are added
        self._configure_row_states()  # Configure the states of the entries after all rows are added

    def _add_row_manuel(self, n_row=None, left_val = None , right_val = None, where="end", reconfigure_states=False):
        """Add a new row of entries in the 'Manuel' frame, either above or below the current frame."""

        if n_row is None:
            n_row = len(self.list_entries_manuel)  # Default to adding at the end if no row index is provided

        if left_val is None:
            left_val = self.list_entries_manuel[n_row-1][3].get() if n_row > 0 else ""  # Default to previous row's right value if exists
        if right_val is None:
            right_val = ""  # Default to empty if no right value is provided

        # Frame for each row of entries
        frame_row = ttk.Frame(self.frame_manuel, style='choix_classe.TFrame')
        frame_row._hover_count = 0

        self.bind_hover(frame_row, row=frame_row)      

        ttk.Label(frame_row, text=f"n°{n_row+1} :", style='choix_classe.TLabel').grid(row=0, column=0, sticky="e", padx=self.padx_label, pady=self.pady_label)
        self.bind_hover(frame_row.winfo_children()[-1], row=frame_row)

        left_var = tk.StringVar(value=str(left_val))
        right_var = tk.StringVar(value=str(right_val))

        ttk.Label(frame_row, text="[", style='choix_classe.TLabel').grid(row=0, column=1, sticky="e", padx=0, pady=0)
        self.bind_hover(frame_row.winfo_children()[-1], row=frame_row)

        left_entry = ttk.Entry(frame_row, width=10, style='choix_classe.TEntry', textvariable=left_var, justify= "center")
        left_entry.grid(row=0, column=2, sticky="w", padx=(2,0), pady=5)
        self.bind_hover(left_entry)

        ttk.Label(frame_row, text="; ", style='choix_classe.TLabel').grid(row=0, column=3, sticky="w", padx=0, pady=0)
        self.bind_hover(frame_row.winfo_children()[-1], row=frame_row)

        right_entry = ttk.Entry(frame_row, width=10, style='choix_classe.TEntry', textvariable=right_var, justify= "center")
        right_entry.grid(row=0, column=4, sticky="w", padx=2, pady=5)
        self.bind_hover(right_entry)

        ttk.Label(frame_row, text="]", style='choix_classe.TLabel').grid(row=0, column=5, sticky="w", padx=0, pady=0)
        self.bind_hover(frame_row.winfo_children()[-1], row=frame_row)

        # Add buttons for adding/removing rows
        self._add_button_row_frame_manuel(frame_row, n_row)

        
        # store tuple: (left_entry, right_entry, left_var, right_var)
        if where == "end" :
            self.list_entries_manuel.append((left_entry, right_entry, left_var, right_var))
            frame_row.pack(side="top", fill="x", padx=5, pady=5)

        if where == "beginning" and n_row is not None:
            self.list_entries_manuel.insert(n_row, (left_entry, right_entry, left_var, right_var))
            frame_row.pack(side="bottom", fill="x", padx=5, pady=5)


        if reconfigure_states:
            self._configure_row_states()  # Reconfigure the states of the entries after adding a new row

    def _configure_row_states(self):
        """Configure the states of the left and right entries in the 'Manuel' frame based on their position."""
        # configure states and traces after creating all rows
        for i, (left_entry, right_entry, left_var, right_var) in enumerate(self.list_entries_manuel):
            # middle rows: left is disabled and linked to previous right
            if i > 0 and i < len(self.list_entries_manuel):
                left_entry.configure(state="disabled")
            else:
                left_entry.configure(state="normal")

            # attach trace to right_var to update next row's left_var when changed
            # use default lambda capturing index via default arg
            def make_trace(idx):
                return lambda *a: self._on_right_changed(idx)

            right_var.trace_add("write", make_trace(i))

    def bind_hover(self, widget, row=None):
        """Bind hover events to a widget, changing its style when hovered."""
        if row is not None:
            widget.bind("<Enter>", lambda event, row=row: self._on_row_hover(row, True))
            widget.bind("<Leave>", lambda event, row=row: self._on_row_hover(row, False))

    def _on_right_changed(self, i):
        # when right entry at row i changes, copy its value to left of row i+1 (if exists)
        if self._updating_link:
            return

        next_idx = i + 1
        if next_idx >= len(self.list_entries_manuel):
            return

        self._updating_link = True
        try:
            val = self.list_entries_manuel[i][3].get()
            next_left_var = self.list_entries_manuel[next_idx][2]
            next_left_var.set(val)
        finally:
            self._updating_link = False

    def _set_row_state(self, row_index, left_state="normal", right_state="normal"):
        if 0 <= row_index < len(self.list_entries_manuel):
            left_entry, right_entry, _, _ = self.list_entries_manuel[row_index]
            left_entry.configure(state=left_state)
            right_entry.configure(state=right_state)

    def _on_row_hover(self, row, enter: bool):
        """Handle hover events for a row of entries in the 'Manuel' frame."""
        if enter:
            row._hover_count += 1
        else:
            row._hover_count = max(0, row._hover_count - 1)

        state = ['active'] if row._hover_count > 0 else ['!active']
        try:
            row.state(state)
        except tk.TclError:
            pass

        for child in row.winfo_children():
            try:
                child.state(state)
            except tk.TclError:
                pass

        if hasattr(row, '_buttons'):
            if row._hover_count > 0:
                for button, info in zip(row._buttons, row._button_grid_info):
                    button.grid(**info)
            else:
                for button in row._buttons:
                    button.grid_forget()

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

    def get_classes(self):
        """Return the list of classes based on the selected class type."""
        classes = []
        if self._combobox_choix_class.get() == "Auto":
            n_classes = int(self.spinner_n_classes.get())

            v_min = self.safe_float_value (self.entry_v_min.get())
            v_max = self.safe_float_value (self.entry_v_max.get())

            if v_min is None or v_max is None:
                return []  # Return empty list if min or max values are invalid

            classes = [v_min + i * (v_max - v_min) / (n_classes - 1) for i in range(n_classes)] if n_classes > 1 else [v_min]


        elif self._combobox_choix_class.get() == "Manuel":
            # Add the first left value to the classes list
            left_val = self.list_entries_manuel[0][2].get()
            float_left_val = self.safe_float_value (left_val)
            if float_left_val is not None:
                classes.append(float_left_val) 

            # Add the right values from each row to the classes list, validating them as floats
            for left_entry, right_entry, left_var, right_var in self.list_entries_manuel:

                right_val = right_var.get()

                float_right_val = self.safe_float_value (right_val)

                if float_right_val is not None :
                    classes.append(float_right_val) 

        print(classes)

        return classes

    def safe_float_value(self, value_str):
        """Convert a string to a float, returning None if conversion fails."""
        try:
            return float(value_str)
        except ValueError:
            messagebox.showerror("Erreur", f"Valeur invalide pour la classe : {value_str}")
            return None

    def _add_button_row_frame_manuel(self, frame, i_row):

        list_buttons = []

        # Button to remove the current row from the frame
        button_remove_row = ttk.Button(frame, text="x", width=3, style='TkPlotCanvas.TButton', command=lambda: self._remove_row_manuel(frame))
        button_remove_row.grid(row=0, column=8, sticky="w", padx=5, pady=5)
        self.bind_hover(button_remove_row, row=frame)
        list_buttons.append(button_remove_row)

        frame._buttons = list_buttons
        frame._button_grid_info = [button.grid_info() for button in frame._buttons]
        for button in frame._buttons:
            button.grid_forget()


    def _remove_row_manuel(self, frame_row):
        """Remove a row of entries from the 'Manuel' frame."""
        for i, (left_entry, right_entry, left_var, right_var) in enumerate(self.list_entries_manuel):
            if left_entry.master == frame_row:
                # Remove the row from the list and destroy the widgets
                self.list_entries_manuel.pop(i)
                frame_row.destroy()
                break

    
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test choix_class")
    choix_class_frame = choix_classe(root, with_buttons=True, classes=[0, 10, 20, 30])
    choix_class_frame.pack(fill="both", expand=True)
    root.mainloop()
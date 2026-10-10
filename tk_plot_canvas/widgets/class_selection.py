"""Frame used to choose contour classes: automatic, manual or none."""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Optional, Sequence

from ..config import (
    CLASS_MODE_AUTO,
    CLASS_MODE_MANUAL,
    CLASS_MODE_NONE,
    CLASS_MODES,
    HOVER_BACKGROUND,
    STYLE_BUTTON,
    STYLE_COMBOBOX,
    STYLE_ENTRY,
    STYLE_HOVER_ENTRY,
    STYLE_HOVER_FRAME,
    STYLE_HOVER_LABEL,
    STYLE_LABEL,
    STYLE_LABELFRAME,
    STYLE_SECTION_TITLE,
    STYLE_SPINBOX,
)
from .manual_classes import ManualClassesEditor

LABEL_PADX = (10, 5)
LABEL_PADY = (10, 10)
MAX_CLASS_COUNT = 10000
FIELD_WIDTH = 10

ClassSelection = tuple[str, list[float]]


def configure_class_selection_styles() -> None:
    """Configure the hover styles used by the manual class rows."""
    style = ttk.Style()
    default_background = style.lookup("TFrame", "background")
    hover_map = [("active", HOVER_BACKGROUND), ("!active", default_background)]
    style.configure(STYLE_HOVER_FRAME, background=default_background)
    style.map(STYLE_HOVER_FRAME, background=hover_map)
    style.configure(STYLE_HOVER_LABEL, background=default_background)
    style.map(STYLE_HOVER_LABEL, background=hover_map)
    style.configure(
        STYLE_HOVER_ENTRY,
        fieldbackground=default_background,
        background=default_background,
    )
    style.map(STYLE_HOVER_ENTRY, fieldbackground=hover_map)


def parse_class_value(text: str) -> Optional[float]:
    """Convert a class bound to float, reporting invalid input to the user.

    Args:
        text: Raw text typed by the user.

    Returns:
        The value, or None when the text is not a number.
    """
    try:
        return float(text)
    except ValueError:
        messagebox.showerror("Erreur", f"Valeur invalide pour la classe : {text}")
        return None


class ClassSelectionFrame(ttk.Frame):
    """Let the user choose how contour classes are computed.

    Attributes:
        class_mode: Last mode returned by :meth:`get_classes`.
    """

    def __init__(
        self,
        master: tk.Misc,
        *args: Any,
        type_class: str = CLASS_MODE_AUTO,
        classes: Sequence[float] = (),
        with_buttons: bool = False,
        v_max: Any = 1.0,
        v_min: Any = 0.0,
        nb_classes: int = 10,
        **kwargs: Any,
    ) -> None:
        """Build the frame.

        Args:
            master: Parent widget.
            *args: Passed to ``ttk.Frame``.
            type_class: Initially displayed mode ("Auto", "Manuel", "Aucune").
            classes: Initial bounds of the manual classes.
            with_buttons: Whether to add "Get classes" / "Quitter" buttons.
            v_max: Initial maximum of the automatic classes.
            v_min: Initial minimum of the automatic classes.
            nb_classes: Initial number of automatic classes.
            **kwargs: Passed to ``ttk.Frame``.
        """
        super().__init__(master, *args, **kwargs)
        configure_class_selection_styles()
        self.class_mode = type_class
        self._build_mode_selector()
        self.auto_frame = ttk.Frame(self)
        self._fill_auto_frame(nb_classes, v_min, v_max)
        self.manual_editor = ManualClassesEditor(self, list(classes))
        self.show_mode_frame(mode=self.class_mode)
        if with_buttons:
            self._build_buttons()

    def _build_mode_selector(self) -> None:
        """Create the combobox selecting the class mode."""
        frame = ttk.LabelFrame(self, text="Choix du type de classe", style=STYLE_LABELFRAME)
        frame.pack(side="top", fill="x", padx=5, pady=5)
        ttk.Label(frame, text="Choisir le type de classe :", style=STYLE_LABEL).pack(
            side="left", padx=5, pady=5
        )
        self.mode_combobox = ttk.Combobox(
            frame, values=CLASS_MODES, state="readonly", style=STYLE_COMBOBOX
        )
        self.mode_combobox.current(0)
        self.mode_combobox.pack(side="left", padx=5, pady=5)
        self.mode_combobox.bind("<<ComboboxSelected>>", self.show_mode_frame)

    def _fill_auto_frame(self, class_count: int, v_min: Any, v_max: Any) -> None:
        """Create the widgets of the automatic mode.

        Args:
            class_count: Initial number of classes.
            v_min: Initial minimum value.
            v_max: Initial maximum value.
        """
        ttk.Label(
            self.auto_frame,
            text="Paramètres pour la classe : Auto",
            style=STYLE_SECTION_TITLE,
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=LABEL_PADX, pady=LABEL_PADY)
        self._add_auto_label("Nombre de classes :", 1)
        self.class_count_spinbox = ttk.Spinbox(
            self.auto_frame,
            from_=1,
            to=MAX_CLASS_COUNT,
            width=FIELD_WIDTH,
            style=STYLE_SPINBOX,
            justify="center",
        )
        self.class_count_spinbox.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.class_count_spinbox.set(class_count)
        self._add_auto_label("Valeur minimale :", 2)
        self.min_entry = self._add_auto_entry(2, v_min)
        self._add_auto_label("Valeur maximale :", 3)
        self.max_entry = self._add_auto_entry(3, v_max)

    def _add_auto_label(self, text: str, row: int) -> None:
        """Add a field label to the automatic-mode frame.

        Args:
            text: Label text.
            row: Grid row.
        """
        ttk.Label(self.auto_frame, text=text, style=STYLE_LABEL).grid(
            row=row, column=0, sticky="w", padx=LABEL_PADX, pady=LABEL_PADY
        )

    def _add_auto_entry(self, row: int, value: Any) -> ttk.Entry:
        """Add a centered entry to the automatic-mode frame.

        Args:
            row: Grid row.
            value: Initial value.

        Returns:
            The created entry.
        """
        entry = ttk.Entry(self.auto_frame, width=FIELD_WIDTH, style=STYLE_ENTRY, justify="center")
        entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        entry.insert(0, str(value))
        return entry

    def _build_buttons(self) -> None:
        """Create the optional "Get classes" and "Quitter" buttons."""
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        ttk.Button(
            buttons_frame,
            text="Get classes",
            command=self.get_classes,
            style=STYLE_BUTTON,
        ).pack(side="right", padx=5, pady=5)
        ttk.Button(buttons_frame, text="Quitter", command=self.destroy, style=STYLE_BUTTON).pack(
            side="right", padx=5, pady=5
        )

    def show_mode_frame(
        self, event: Optional[tk.Event] = None, mode: Optional[str] = None
    ) -> None:
        """Display the frame matching the selected mode.

        Args:
            event: Combobox event (unused).
            mode: Mode to select before refreshing, if any.
        """
        if mode is not None:
            self.mode_combobox.set(mode)
        selected_mode = self.mode_combobox.get()
        if selected_mode == CLASS_MODE_AUTO:
            self.manual_editor.pack_forget()
            self.auto_frame.pack(fill="x", padx=5, pady=5)
        elif selected_mode == CLASS_MODE_MANUAL:
            self.auto_frame.pack_forget()
            self.manual_editor.pack(fill="both", padx=5, pady=5, expand=True)
        elif selected_mode == CLASS_MODE_NONE:
            self.auto_frame.pack_forget()
            self.manual_editor.pack_forget()

    def get_classes(self) -> Optional[ClassSelection]:
        """Return the class bounds for the selected mode.

        Returns:
            ``(mode, bounds)``; bounds are empty in "Aucune" mode. Returns None
            when the automatic minimum or maximum is invalid.
        """
        selected_mode = self.mode_combobox.get()
        classes: list[float] = []
        if selected_mode == CLASS_MODE_AUTO:
            auto_classes = self._automatic_classes()
            if auto_classes is None:
                return None
            classes = auto_classes
            self.class_mode = CLASS_MODE_AUTO
        elif selected_mode == CLASS_MODE_MANUAL:
            classes = self._manual_classes()
            self.class_mode = CLASS_MODE_MANUAL
        return self.class_mode, classes

    def _automatic_classes(self) -> Optional[list[float]]:
        """Compute evenly spaced class bounds.

        Returns:
            ``class_count + 1`` bounds (only the minimum for a single class),
            or None when the minimum or maximum is invalid.
        """
        class_count = int(self.class_count_spinbox.get())
        v_min = parse_class_value(self.min_entry.get())
        v_max = parse_class_value(self.max_entry.get())
        if v_min is None or v_max is None:
            return None
        if class_count <= 1:
            return [v_min]
        value_range = v_max - v_min
        return [v_min + index * value_range / class_count for index in range(class_count + 1)]

    def _manual_classes(self) -> list[float]:
        """Collect the valid bounds typed in the manual editor.

        Returns:
            The first left bound followed by every right bound.
        """
        raw_values = [self.manual_editor.first_left_value()]
        raw_values += [row.right_var.get() for row in self.manual_editor.rows]
        classes = []
        for raw_value in raw_values:
            if raw_value is None:
                continue
            value = parse_class_value(raw_value)
            if value is not None:
                classes.append(value)
        return classes

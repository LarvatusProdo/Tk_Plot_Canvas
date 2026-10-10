"""Dialogs editing the fonts of the title, axes, cartouche and colorbar."""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from typing import TYPE_CHECKING, Any, Callable, Optional

from matplotlib.text import Text

from ..config import (
    DEFAULT_FONT_COLOR,
    DEFAULT_FONT_SIZE,
    DIALOG_SIZE,
    FONT_TARGET_CARTOUCHE,
    FONT_TARGET_COLORBAR,
    FONT_TARGET_TITLE,
    FONT_TARGET_XLABEL,
    STYLE_BUTTON,
    STYLE_CARTOUCHE_CELL,
    STYLE_CARTOUCHE_HEADER,
    STYLE_FRAME,
    STYLE_LABELFRAME,
)
from ..fonts import parse_tk_font_spec
from .font_controls import FontChoice, FontControls
from .window_placement import place_window

if TYPE_CHECKING:
    from ..canvas.plot_canvas import TkPlotCanvas

NAME_SECTION = "name"
TICK_SECTION = "tick"
HEADER_SECTION = "header"
CELL_SECTION = "cell"
SECTION_PADDING = 10


def usable_tk_font_families() -> list[str]:
    """List the font families Tk can actually instantiate.

    Returns:
        The usable families, sorted.
    """
    families = []
    for family in tkfont.families():
        try:
            tkfont.Font(family=family)
            families.append(family)
        except tk.TclError:
            pass
    return sorted(families)


class FontDialog(tk.Toplevel):
    """Base dialog: font sections followed by an "apply" button."""

    def __init__(
        self, parent: tk.Misc, canvas: "TkPlotCanvas", target: str, font_families: list[str]
    ) -> None:
        """Create the dialog.

        Args:
            parent: Window the dialog is positioned against.
            canvas: The plot canvas being edited.
            target: Edited element, shown in the window title.
            font_families: Choices of the font family comboboxes.
        """
        super().__init__(parent)
        self.title(f"Modification du {target}")
        place_window(self, parent, DIALOG_SIZE)
        self.canvas = canvas
        self.target = target
        self.font_families = font_families
        self.sections: dict[str, FontControls] = {}
        self.content = ttk.Frame(self, style=STYLE_FRAME)
        self.content.pack(fill="both", expand=True, anchor="nw")
        apply_button = ttk.Button(
            self.content, text="Appliquer les changements", style=STYLE_BUTTON, command=self.apply
        )
        self.build_sections()
        apply_button.pack(fill="x", side="top", padx=SECTION_PADDING, pady=SECTION_PADDING)

    def add_section(self, key: str, title: str) -> FontControls:
        """Add a titled group of font controls.

        Args:
            key: Identifier of the section.
            title: Title shown on the label frame.

        Returns:
            The created controls.
        """
        frame = ttk.LabelFrame(self.content, text=title, style=STYLE_LABELFRAME)
        frame.pack(fill="both", side="top", padx=SECTION_PADDING, pady=SECTION_PADDING)
        self.sections[key] = FontControls(frame, self.font_families, self)
        return self.sections[key]

    def build_sections(self) -> None:
        """Create and initialize the font sections.

        Raises:
            NotImplementedError: Always; subclasses must implement it.
        """
        raise NotImplementedError

    def apply(self) -> None:
        """Apply the selected fonts.

        Raises:
            NotImplementedError: Always; subclasses must implement it.
        """
        raise NotImplementedError


def load_text_font(controls: FontControls, text: Text) -> None:
    """Show the font of a Matplotlib text in font controls.

    Args:
        controls: Controls to initialize.
        text: Title, axis label or colorbar label.
    """
    font = text.get_fontproperties()
    controls.set_family(font.get_name())
    controls.set_style(font.get_style())
    controls.set_size(int(font.get_size()))
    controls.set_bold(font.get_weight() == "bold")
    controls.set_color(text.get_color())


def text_font_kwargs(choice: FontChoice) -> dict[str, Any]:
    """Convert a font choice into Matplotlib text keyword arguments.

    Args:
        choice: Selected font.

    Returns:
        fontfamily, fontsize, fontstyle, fontweight and color arguments.
    """
    return dict(
        fontfamily=choice.family,
        fontsize=choice.size,
        fontstyle=choice.style,
        fontweight=choice.weight,
        color=choice.color,
    )


class AxisFontDialog(FontDialog):
    """Edit the font of the title, or of an axis label and its ticks."""

    def __init__(
        self, parent: tk.Misc, canvas: "TkPlotCanvas", target: str, label_text: Callable[[], str]
    ) -> None:
        """Create the dialog.

        Args:
            parent: Window the dialog is positioned against.
            canvas: The plot canvas being edited.
            target: "Graphique title", "xlabel" or "ylabel".
            label_text: Returns the text to display with the new font.
        """
        self.label_text = label_text
        super().__init__(parent, canvas, target, list(canvas.matplotlib_fonts))

    def _target_text(self) -> Text:
        """Return the Matplotlib text edited by this dialog.

        Returns:
            The title or the axis label.
        """
        axes = self.canvas.axes
        if self.target == FONT_TARGET_TITLE:
            return axes.title
        return axes.xaxis.label if self.target == FONT_TARGET_XLABEL else axes.yaxis.label

    def _target_axis(self) -> Any:
        """Return the Matplotlib axis whose ticks are edited.

        Returns:
            The x or y axis.
        """
        axes = self.canvas.axes
        return axes.xaxis if self.target == FONT_TARGET_XLABEL else axes.yaxis

    def build_sections(self) -> None:
        """Create the label (and tick) sections from the current fonts."""
        if self.target == FONT_TARGET_TITLE:
            load_text_font(
                self.add_section(NAME_SECTION, "Paramètres du titre :"), self._target_text()
            )
            return
        name_controls = self.add_section(NAME_SECTION, "Paramètres du nom de l'axe :")
        tick_controls = self.add_section(TICK_SECTION, "Paramètres de l'échelle :")
        load_text_font(name_controls, self._target_text())
        self._load_tick_font(tick_controls)

    def _load_tick_font(self, controls: FontControls) -> None:
        """Show the font of the first tick label.

        Args:
            controls: Controls to initialize.
        """
        first_tick = self._target_axis().get_ticklabels()[0]
        controls.set_family(first_tick.get_fontname())
        controls.set_style(first_tick.get_fontstyle())
        controls.set_size(int(first_tick.get_fontsize()))
        controls.set_bold(first_tick.get_fontweight() == "bold")
        controls.set_color(first_tick.get_color())

    def apply(self) -> None:
        """Apply the fonts to the title or to the axis label and ticks."""
        font_kwargs = text_font_kwargs(self.sections[NAME_SECTION].read())
        axes = self.canvas.axes
        if self.target == FONT_TARGET_TITLE:
            axes.set_title(self.label_text(), **font_kwargs)
        else:
            setter = axes.set_xlabel if self.target == FONT_TARGET_XLABEL else axes.set_ylabel
            setter(self.label_text(), **font_kwargs)
            self._apply_tick_font(self.sections[TICK_SECTION].read())
        self.canvas.figure_canvas.draw()
        self.destroy()

    def _apply_tick_font(self, choice: FontChoice) -> None:
        """Apply a font to every tick label of the edited axis.

        Args:
            choice: Selected font.
        """
        for tick in self._target_axis().get_ticklabels():
            tick.set_fontname(choice.family)
            tick.set_fontsize(choice.size)
            tick.set_fontstyle(choice.style)
            tick.set_fontweight(choice.weight)
            tick.set_color(choice.color)


class CartoucheFontDialog(FontDialog):
    """Edit the fonts of the cartouche column titles and values."""

    def __init__(self, parent: tk.Misc, canvas: "TkPlotCanvas") -> None:
        """Create the dialog.

        Args:
            parent: Window the dialog is positioned against.
            canvas: The plot canvas being edited.
        """
        super().__init__(parent, canvas, FONT_TARGET_CARTOUCHE, usable_tk_font_families())

    def build_sections(self) -> None:
        """Create both sections and load the current cartouche styles."""
        header = self.add_section(HEADER_SECTION, "Paramètres pour le nom des colonnes :")
        cell = self.add_section(CELL_SECTION, "Paramètres pour les lignes :")
        self._load_style(header, STYLE_CARTOUCHE_HEADER)
        self._load_style(cell, STYLE_CARTOUCHE_CELL)

    def _load_style(self, controls: FontControls, style_name: str) -> None:
        """Show the font of a ttk style in font controls.

        Args:
            controls: Controls to initialize.
            style_name: ttk style holding the font.
        """
        style = self.canvas.style.configure(style_name)
        parts = parse_tk_font_spec(style["font"], self.canvas.default_font)
        controls.set_family(parts[0])
        controls.set_size(int(parts[1]))
        controls.set_bold(len(parts) > 2 and parts[2] == "bold")
        controls.set_color(style["foreground"])

    def apply(self) -> None:
        """Apply both fonts to the cartouche ttk styles."""
        for key, style_name in (
            (HEADER_SECTION, STYLE_CARTOUCHE_HEADER),
            (CELL_SECTION, STYLE_CARTOUCHE_CELL),
        ):
            choice = self.sections[key].read()
            if choice.style != "normal":
                font = (choice.family, int(choice.size), choice.style, choice.weight)
            else:
                font = (choice.family, int(choice.size), choice.weight)
            self.canvas.style.configure(style_name, font=font)
            self.canvas.style.configure(style_name, foreground=choice.color)
        self.destroy()


class ColorbarFontDialog(FontDialog):
    """Edit the font of the colorbar label."""

    def __init__(self, parent: tk.Misc, canvas: "TkPlotCanvas") -> None:
        """Create the dialog.

        Args:
            parent: Window the dialog is positioned against.
            canvas: The plot canvas being edited.
        """
        self.colorbar: Optional[Any] = canvas.colorbar
        super().__init__(parent, canvas, FONT_TARGET_COLORBAR, list(canvas.matplotlib_fonts))

    def build_sections(self) -> None:
        """Create the section and load the current colorbar label font."""
        controls = self.add_section(NAME_SECTION, "Paramètres du label de la colorbar :")
        if self.colorbar is None or not hasattr(self.colorbar, "ax"):
            controls.set_family("")
            controls.set_style("normal")
            controls.set_size(DEFAULT_FONT_SIZE)
            controls.set_bold(False)
            controls.set_color(DEFAULT_FONT_COLOR)
            return
        load_text_font(controls, self.colorbar.ax.yaxis.label)

    def apply(self) -> None:
        """Apply the font to the colorbar label (creating the colorbar if needed)."""
        choice = self.sections[NAME_SECTION].read()
        colorbar = self.colorbar
        if colorbar is None or not hasattr(colorbar, "ax"):
            colorbar = self._create_colorbar()
        if colorbar is not None and hasattr(colorbar, "ax"):
            label = colorbar.ax.yaxis.label
            label.set_fontfamily(choice.family)
            label.set_fontsize(int(choice.size))
            label.set_fontstyle(choice.style)
            label.set_fontweight(choice.weight)
            label.set_color(choice.color)
            self.canvas.figure_canvas.draw()
        self.destroy()

    def _create_colorbar(self) -> Optional[Any]:
        """Create a colorbar for the first plot, if possible.

        Returns:
            The new colorbar, or None.
        """
        if len(self.canvas.lines) == 0:
            return None
        try:
            self.canvas.colorbar = self.canvas.figure.colorbar(
                self.canvas.lines[0], ax=self.canvas.axes
            )
        except Exception:  # noqa: BLE001 - Matplotlib may refuse the mappable
            return None
        return self.canvas.colorbar

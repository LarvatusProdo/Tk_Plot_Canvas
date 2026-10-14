"""Dialogs editing the fonts of the title, axes, cartouche and colorbar.

Every change is previewed immediately; "Annuler" (or Escape) restores the
fonts shown when the dialog opened, "Fermer" keeps the changes.
"""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from typing import TYPE_CHECKING, Any, Callable, Optional

from matplotlib.font_manager import FontProperties
from matplotlib.text import Text

from ..config import (
    DEFAULT_FONT_COLOR,
    DEFAULT_FONT_SIZE,
    DIALOG_SIZE,
    FONT_DIALOG_TITLES,
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
from .window_placement import setup_dialog

if TYPE_CHECKING:
    from ..canvas.plot_canvas import TkPlotCanvas

NAME_SECTION = "name"
TICK_SECTION = "tick"
HEADER_SECTION = "header"
CELL_SECTION = "cell"
SECTION_PADDING = 10
TextFont = tuple[FontProperties, Any]


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


def capture_text_font(text: Text) -> TextFont:
    """Remember the font and color of a Matplotlib text.

    Args:
        text: Title, axis label or colorbar label.

    Returns:
        A copy of its font properties and its color.
    """
    return text.get_fontproperties().copy(), text.get_color()


def restore_text_font(text: Text, font: TextFont) -> None:
    """Give back to a Matplotlib text a font remembered by :func:`capture_text_font`.

    Args:
        text: Text to restore.
        font: Remembered font properties and color.
    """
    properties, color = font
    text.set_fontproperties(properties)
    text.set_color(color)


class FontDialog(tk.Toplevel):
    """Base dialog: font sections previewed live, then "Annuler" and "Fermer"."""

    def __init__(
        self, parent: tk.Misc, canvas: "TkPlotCanvas", target: str, font_families: list[str]
    ) -> None:
        """Create the dialog.

        Args:
            parent: Window the dialog is positioned against.
            canvas: The plot canvas being edited.
            target: Edited element (see ``FONT_DIALOG_TITLES``).
            font_families: Choices of the font family comboboxes.
        """
        super().__init__(parent)
        self.title(FONT_DIALOG_TITLES.get(target, "Police"))
        setup_dialog(self, parent, DIALOG_SIZE, on_escape=self.cancel)
        self.canvas = canvas
        self.target = target
        self.font_families = font_families
        self.sections: dict[str, FontControls] = {}
        self.content = ttk.Frame(self, style=STYLE_FRAME)
        self.content.pack(fill="both", expand=True, anchor="nw")
        self.build_sections()
        self._initial_state = self.capture_state()
        self._build_buttons()

    def _build_buttons(self) -> None:
        """Create the "Annuler" and "Fermer" buttons."""
        frame = ttk.Frame(self.content, style=STYLE_FRAME)
        frame.pack(fill="x", side="top", padx=SECTION_PADDING, pady=SECTION_PADDING)
        ttk.Button(frame, text="Fermer", style=STYLE_BUTTON, command=self.destroy).pack(
            side="right"
        )
        ttk.Button(frame, text="Annuler", style=STYLE_BUTTON, command=self.cancel).pack(
            side="right", padx=SECTION_PADDING
        )

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
        self.sections[key] = FontControls(frame, self.font_families, self, self.apply)
        return self.sections[key]

    def cancel(self) -> None:
        """Restore the fonts shown when the dialog opened, then close it."""
        self.restore_state(self._initial_state)
        self.destroy()

    def build_sections(self) -> None:
        """Create and initialize the font sections.

        Raises:
            NotImplementedError: Always; subclasses must implement it.
        """
        raise NotImplementedError

    def apply(self) -> None:
        """Apply the selected fonts (called after each change).

        Raises:
            NotImplementedError: Always; subclasses must implement it.
        """
        raise NotImplementedError

    def capture_state(self) -> Any:
        """Remember the current fonts of the edited element.

        Raises:
            NotImplementedError: Always; subclasses must implement it.
        """
        raise NotImplementedError

    def restore_state(self, state: Any) -> None:
        """Give back the fonts remembered by :meth:`capture_state`.

        Args:
            state: Remembered fonts.

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
            load_text_font(self.add_section(NAME_SECTION, "Titre"), self._target_text())
            return
        name_controls = self.add_section(NAME_SECTION, "Libellé de l'axe")
        tick_controls = self.add_section(TICK_SECTION, "Graduations")
        load_text_font(name_controls, self._target_text())
        self._load_tick_font(tick_controls)

    def _tick_font(self) -> Optional[FontChoice]:
        """Return the font of the first tick label.

        Returns:
            The tick font, or None when the axis has no tick label.
        """
        tick_labels = self._target_axis().get_ticklabels()
        if not tick_labels:
            return None
        first_tick = tick_labels[0]
        return FontChoice(
            family=first_tick.get_fontname(),
            size=str(first_tick.get_fontsize()),
            style=first_tick.get_fontstyle(),
            weight="bold" if first_tick.get_fontweight() == "bold" else "normal",
            color=first_tick.get_color(),
        )

    def _load_tick_font(self, controls: FontControls) -> None:
        """Show the font of the first tick label.

        Args:
            controls: Controls to initialize.
        """
        font = self._tick_font()
        if font is None:
            return
        controls.set_family(font.family)
        controls.set_style(font.style)
        controls.set_size(int(float(font.size)))
        controls.set_bold(font.weight == "bold")
        controls.set_color(font.color)

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
        self.canvas.figure_canvas.draw_idle()

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

    def capture_state(self) -> tuple[TextFont, Optional[FontChoice]]:
        """Remember the fonts of the edited text and of its ticks.

        Returns:
            The text font and the tick font (None for the title).
        """
        is_title = self.target == FONT_TARGET_TITLE
        return capture_text_font(self._target_text()), None if is_title else self._tick_font()

    def restore_state(self, state: tuple[TextFont, Optional[FontChoice]]) -> None:
        """Give back the remembered fonts.

        Args:
            state: Text font and tick font.
        """
        text_font, tick_font = state
        restore_text_font(self._target_text(), text_font)
        if tick_font is not None:
            self._apply_tick_font(tick_font)
        self.canvas.figure_canvas.draw_idle()


class CartoucheFontDialog(FontDialog):
    """Edit the fonts of the cartouche column titles and values."""

    STYLE_NAMES = (STYLE_CARTOUCHE_HEADER, STYLE_CARTOUCHE_CELL)

    def __init__(self, parent: tk.Misc, canvas: "TkPlotCanvas") -> None:
        """Create the dialog.

        Args:
            parent: Window the dialog is positioned against.
            canvas: The plot canvas being edited.
        """
        super().__init__(parent, canvas, FONT_TARGET_CARTOUCHE, usable_tk_font_families())

    def build_sections(self) -> None:
        """Create both sections and load the current cartouche styles."""
        header = self.add_section(HEADER_SECTION, "Titres des colonnes")
        cell = self.add_section(CELL_SECTION, "Valeurs")
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
        for key, style_name in zip((HEADER_SECTION, CELL_SECTION), self.STYLE_NAMES):
            choice = self.sections[key].read()
            if choice.style != "normal":
                font = (choice.family, int(choice.size), choice.style, choice.weight)
            else:
                font = (choice.family, int(choice.size), choice.weight)
            self.canvas.style.configure(style_name, font=font, foreground=choice.color)

    def capture_state(self) -> dict[str, tuple[Any, Any]]:
        """Remember the font and color of both cartouche styles.

        Returns:
            ``{style name: (font, foreground)}``.
        """
        state = {}
        for style_name in self.STYLE_NAMES:
            style = self.canvas.style.configure(style_name)
            state[style_name] = (style["font"], style["foreground"])
        return state

    def restore_state(self, state: dict[str, tuple[Any, Any]]) -> None:
        """Give back the remembered styles.

        Args:
            state: ``{style name: (font, foreground)}``.
        """
        for style_name, (font, foreground) in state.items():
            self.canvas.style.configure(style_name, font=font, foreground=foreground)


class ColorbarFontDialog(FontDialog):
    """Edit the font of the colorbar label."""

    def __init__(self, parent: tk.Misc, canvas: "TkPlotCanvas") -> None:
        """Create the dialog.

        Args:
            parent: Window the dialog is positioned against.
            canvas: The plot canvas being edited.
        """
        super().__init__(parent, canvas, FONT_TARGET_COLORBAR, list(canvas.matplotlib_fonts))

    def _label(self) -> Optional[Text]:
        """Return the label of the displayed colorbar.

        Returns:
            The label, or None when no colorbar is displayed.
        """
        from ..canvas.colorbar import colorbar_label_axis

        colorbar = self.canvas.colorbar
        if colorbar is None or not hasattr(colorbar, "ax"):
            return None
        return colorbar_label_axis(colorbar).label

    def build_sections(self) -> None:
        """Create the section and load the current colorbar label font."""
        controls = self.add_section(NAME_SECTION, "Label de la colorbar")
        label = self._label()
        if label is not None:
            load_text_font(controls, label)
            return
        controls.set_family("")
        controls.set_style("normal")
        controls.set_size(DEFAULT_FONT_SIZE)
        controls.set_bold(False)
        controls.set_color(DEFAULT_FONT_COLOR)

    def apply(self) -> None:
        """Apply the font to the colorbar label, if a colorbar is displayed."""
        label = self._label()
        if label is None:
            return
        choice = self.sections[NAME_SECTION].read()
        label.set_fontfamily(choice.family)
        label.set_fontsize(int(choice.size))
        label.set_fontstyle(choice.style)
        label.set_fontweight(choice.weight)
        label.set_color(choice.color)
        self.canvas.figure_canvas.draw_idle()

    def capture_state(self) -> Optional[TextFont]:
        """Remember the font of the colorbar label.

        Returns:
            Its font, or None without colorbar.
        """
        label = self._label()
        return capture_text_font(label) if label is not None else None

    def restore_state(self, state: Optional[TextFont]) -> None:
        """Give back the remembered colorbar label font.

        Args:
            state: Remembered font, or None.
        """
        label = self._label()
        if state is not None and label is not None:
            restore_text_font(label, state)
            self.canvas.figure_canvas.draw_idle()

"""ttk styles used by the plot canvas, its cartouche and its dialogs."""

from tkinter import ttk

from ..config import (
    STYLE_BUTTON,
    STYLE_CARTOUCHE_CELL,
    STYLE_CARTOUCHE_FRAME,
    STYLE_CARTOUCHE_HEADER,
    STYLE_CHECKBUTTON,
    STYLE_COLUMN_HEADER,
    STYLE_ENTRY,
    STYLE_FRAME,
    STYLE_LABEL,
    STYLE_LABELFRAME,
    STYLE_LABELFRAME_LABEL,
    STYLE_NOTEBOOK,
    STYLE_NOTEBOOK_TAB,
    STYLE_SECTION_TITLE,
    UI_FONT_SIZE,
)

TEXT_COLOR = "black"
UNSELECTED_TAB_COLOR = "gray"
NOTEBOOK_TAB_PADDING = (10, 5)


def configure_canvas_styles(
    style: ttk.Style, font_family: str, graph_background: str, frame_background: str
) -> None:
    """Configure every ttk style used by the package.

    Args:
        style: ttk style database.
        font_family: Default UI font family.
        graph_background: Background color of the graph and the cartouche.
        frame_background: Background color of regular frames.
    """
    bold_font = (font_family, UI_FONT_SIZE, "bold")
    style.configure(STYLE_FRAME)
    style.configure(STYLE_NOTEBOOK)
    style.configure(STYLE_NOTEBOOK_TAB, font=bold_font, padding=NOTEBOOK_TAB_PADDING)
    style.map(
        STYLE_NOTEBOOK_TAB,
        foreground=[("selected", TEXT_COLOR), ("!selected", UNSELECTED_TAB_COLOR)],
        background=[("selected", frame_background), ("!selected", frame_background)],
    )
    for name in (STYLE_LABEL, STYLE_CHECKBUTTON, STYLE_LABELFRAME):
        style.configure(name)
    style.configure(STYLE_LABELFRAME_LABEL, font=bold_font)
    _configure_cartouche_styles(style, font_family, graph_background)
    style.configure(STYLE_SECTION_TITLE, font=bold_font, foreground=TEXT_COLOR)
    style.configure(STYLE_ENTRY)
    style.configure(STYLE_BUTTON)
    style.configure(STYLE_COLUMN_HEADER, font=bold_font, foreground=TEXT_COLOR)


def _configure_cartouche_styles(style: ttk.Style, font_family: str, graph_background: str) -> None:
    """Configure the cartouche header, cell and frame styles.

    Args:
        style: ttk style database.
        font_family: Default UI font family.
        graph_background: Background color of the cartouche.
    """
    style.configure(
        STYLE_CARTOUCHE_HEADER,
        font=(font_family, UI_FONT_SIZE, "bold"),
        foreground=TEXT_COLOR,
        background=graph_background,
    )
    style.configure(
        STYLE_CARTOUCHE_CELL,
        font=(font_family, UI_FONT_SIZE, "normal"),
        foreground=TEXT_COLOR,
        background=graph_background,
    )
    style.configure(STYLE_CARTOUCHE_FRAME, background=graph_background)

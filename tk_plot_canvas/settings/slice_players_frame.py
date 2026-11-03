"""Label frame of the "Axes et titre" tab browsing the other dimensions of a 3D plot.

A variable with more than two dimensions is shown at one index of each
dimension plotted along neither x nor y. Each such dimension gets a player:
a ``ttk.Scale`` choosing the index, previous/next buttons and a play button
stepping through the values (applied live).
"""

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Callable, Optional

from ..config import (
    SLICE_PLAYER_DELAY_MS,
    SLICE_SCALE_LENGTH,
    STYLE_BUTTON,
    STYLE_LABEL,
    STYLE_LABELFRAME,
)
from ..widgets import ToolTip
from .axis_frame import FRAME_PADDING, PADDING

if TYPE_CHECKING:
    from ..canvas.plot_canvas import TkPlotCanvas
    from .axes_tab import AxesTab

PLAY_TEXT = "Lecture"
PAUSE_TEXT = "Pause"
STEP_BUTTON_WIDTH = 3
PLAY_BUTTON_WIDTH = 8
SCALE_HELP = "Valeur affichée de cette dimension (glisser pour la changer)."
PLAY_HELP = "Faire défiler les valeurs de cette dimension (en boucle)."


class SlicePlayer:
    """Widgets choosing the index shown along one dimension, on two grid rows.

    The first row shows the dimension name and its displayed value, the second
    one the previous, play and next buttons and the scale.
    """

    def __init__(
        self, parent: ttk.LabelFrame, canvas: "TkPlotCanvas", dimension: str, row: int
    ) -> None:
        """Create the player.

        Args:
            parent: Label frame receiving the widgets.
            canvas: The plot canvas.
            dimension: Dimension browsed by the player.
            row: First grid row of the player.
        """
        self._canvas = canvas
        self._dimension = dimension
        self._last_index = canvas.slice_size(dimension) - 1
        self._after_id: Optional[str] = None
        self.index_var = tk.DoubleVar(value=canvas.slice_index(dimension))
        self.value_var = tk.StringVar()
        self._build(parent, row)
        self._show_value()

    def _build(self, parent: ttk.LabelFrame, row: int) -> None:
        """Create the name and value labels, the buttons and the scale.

        Args:
            parent: Label frame receiving the widgets.
            row: First grid row of the player.
        """
        ttk.Label(parent, text=f"{self._dimension} :", style=STYLE_LABEL).grid(
            row=row, column=0, sticky="e", padx=PADDING, pady=PADDING
        )
        ttk.Label(parent, textvariable=self.value_var, style=STYLE_LABEL).grid(
            row=row, column=1, columnspan=4, sticky="w", padx=PADDING, pady=PADDING
        )
        controls_row = row + 1
        self._add_step_button(parent, controls_row, 1, "◀", -1)
        self._play_button = self._add_button(parent, controls_row, 2, PLAY_TEXT, self.toggle_play)
        self._play_button.configure(width=PLAY_BUTTON_WIDTH)
        ToolTip(self._play_button, PLAY_HELP)
        self._add_step_button(parent, controls_row, 3, "▶", 1)
        self._add_scale(parent, controls_row)
        self._play_button.bind("<Destroy>", lambda _event: self.stop())
        self._disable_if_single_value(parent, controls_row)

    def _add_scale(self, parent: ttk.LabelFrame, row: int) -> None:
        """Create the scale choosing the index along the dimension.

        Args:
            parent: Label frame receiving the scale.
            row: Grid row of the controls.
        """
        scale = ttk.Scale(
            parent,
            from_=0,
            to=self._last_index,
            variable=self.index_var,
            length=SLICE_SCALE_LENGTH,
            command=self._on_scale_moved,
        )
        scale.grid(row=row, column=4, sticky="we", padx=PADDING, pady=PADDING)
        ToolTip(scale, SCALE_HELP)

    def _add_button(
        self, parent: ttk.LabelFrame, row: int, column: int, text: str, command: Callable[[], None]
    ) -> ttk.Button:
        """Add a button to the player row.

        Args:
            parent: Label frame receiving the button.
            row: Grid row.
            column: Grid column.
            text: Button text.
            command: Button callback.

        Returns:
            The created button.
        """
        button = ttk.Button(parent, text=text, command=command, style=STYLE_BUTTON)
        button.grid(row=row, column=column, padx=(0, 2), pady=PADDING)
        return button

    def _add_step_button(
        self, parent: ttk.LabelFrame, row: int, column: int, text: str, step: int
    ) -> None:
        """Add a button showing the previous or next value.

        Args:
            parent: Label frame receiving the button.
            row: Grid row.
            column: Grid column.
            text: Button text.
            step: -1 for the previous value, 1 for the next one.
        """
        button = self._add_button(parent, row, column, text, lambda: self.step(step))
        button.configure(width=STEP_BUTTON_WIDTH)

    def _disable_if_single_value(self, parent: ttk.LabelFrame, row: int) -> None:
        """Disable the player of a dimension having a single value.

        Args:
            parent: Label frame holding the player.
            row: Grid row of the controls.
        """
        if self._last_index > 0:
            return
        for widget in parent.grid_slaves(row=row):
            if isinstance(widget, (ttk.Button, ttk.Scale)):
                widget.state(["disabled"])

    def _on_scale_moved(self, value: str) -> None:
        """Show the slice under the scale cursor, snapped to a whole index.

        Args:
            value: Scale position given by Tk.
        """
        self.show_index(round(float(value)))

    def show_index(self, index: int) -> None:
        """Plot the slice at ``index`` and move the scale there.

        Args:
            index: Index along the dimension.
        """
        self.index_var.set(index)
        self._canvas.set_slice_index(self._dimension, index)
        self._show_value()

    def step(self, step: int) -> None:
        """Show the previous or next value, wrapping around at both ends.

        Args:
            step: -1 for the previous value, 1 for the next one.
        """
        index = self._canvas.slice_index(self._dimension) + step
        self.show_index(index % (self._last_index + 1))

    def toggle_play(self) -> None:
        """Start stepping through the values, or stop when already playing."""
        if self._after_id is not None:
            self.stop()
            return
        self._play_button.configure(text=PAUSE_TEXT)
        self._play_next()

    def _play_next(self) -> None:
        """Show the next value and schedule the following one."""
        self.step(1)
        self._after_id = self._play_button.after(SLICE_PLAYER_DELAY_MS, self._play_next)

    def stop(self) -> None:
        """Stop playing (does nothing when not playing)."""
        if self._after_id is None:
            return
        self._play_button.after_cancel(self._after_id)
        self._after_id = None
        if self._play_button.winfo_exists():
            self._play_button.configure(text=PLAY_TEXT)

    def _show_value(self) -> None:
        """Display the value shown along the dimension and its position."""
        index = self._canvas.slice_index(self._dimension)
        text = self._canvas.slice_value_text(self._dimension)
        self.value_var.set(f"{text}  ({index + 1}/{self._last_index + 1})")


class SlicePlayersFrame:
    """Label frame holding one :class:`SlicePlayer` per sliced dimension.

    Attributes:
        players: Players indexed by dimension name.
    """

    def __init__(self, tab: "AxesTab", parent: tk.Misc, row: int) -> None:
        """Create the label frame in a column of the tab (nothing when no dimension is sliced).

        Args:
            tab: The "Axes et titre" tab.
            parent: Frame of the tab holding the label frame.
            row: Grid row of the label frame in ``parent``.
        """
        self.players: dict[str, SlicePlayer] = {}
        dimensions = tab.canvas.slice_dimensions()
        if len(dimensions) == 0:
            return
        frame = ttk.LabelFrame(
            parent,
            text="Autres dimensions",
            padding=FRAME_PADDING,
            style=STYLE_LABELFRAME,
        )
        frame.grid(row=row, column=0, sticky="nwe", padx=PADDING, pady=PADDING)
        for position, dimension in enumerate(dimensions):
            self.players[dimension] = SlicePlayer(frame, tab.canvas, dimension, 2 * position)

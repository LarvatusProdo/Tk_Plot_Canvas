"""High-DPI support: sharp text and figures on scaled Windows screens.

Without DPI awareness, Windows renders Tk windows at 96 DPI and stretches
them on scaled screens (125 %, 150 %...), which makes text and figures blurry.
"""

import ctypes
import sys
import tkinter as tk

# PROCESS_SYSTEM_DPI_AWARE: Tk reads the system DPI once at startup, which it
# supports; per-monitor awareness would need DPI change events Tk ignores.
SYSTEM_DPI_AWARE = 1
WINDOWS_STANDARD_DPI = 96
TK_POINTS_PER_INCH = 72


def enable_high_dpi() -> None:
    """Make the process DPI aware on Windows (does nothing elsewhere).

    Must run before the first Tk window is created; afterwards Tk has already
    chosen its scaling and the call is skipped.
    """
    if sys.platform != "win32" or getattr(tk, "_default_root", None) is not None:
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(SYSTEM_DPI_AWARE)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


def ui_scale(widget: tk.Misc) -> float:
    """Return the screen scale factor seen by Tk (1.0 at 96 DPI).

    Args:
        widget: Any widget of the application.

    Returns:
        1.0 at 100 %, 1.5 at 150 %...
    """
    dots_per_point = float(widget.tk.call("tk", "scaling"))
    return dots_per_point * TK_POINTS_PER_INCH / WINDOWS_STANDARD_DPI

"""Command-line entry point: ``python -m tk_plot_canvas [demo]``.

Examples:
    python -m tk_plot_canvas                  # xarray demo (default)
    python -m tk_plot_canvas standard         # x/y curves demo
    python -m tk_plot_canvas class-selection  # contour class selector
"""

import argparse
from typing import Optional, Sequence

from .demos import DEMOS

DEFAULT_DEMO = "xarray"


def parse_arguments(arguments: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse the command-line arguments.

    Args:
        arguments: Arguments to parse (defaults to ``sys.argv[1:]``).

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        prog="python -m tk_plot_canvas", description="TkPlotCanvas demos."
    )
    parser.add_argument(
        "demo", nargs="?", default=DEFAULT_DEMO, choices=sorted(DEMOS), help="demo to run"
    )
    return parser.parse_args(arguments)


def main(arguments: Optional[Sequence[str]] = None) -> None:
    """Run the requested demo.

    Args:
        arguments: Command-line arguments (defaults to ``sys.argv[1:]``).
    """
    DEMOS[parse_arguments(arguments).demo]()


if __name__ == "__main__":
    main()

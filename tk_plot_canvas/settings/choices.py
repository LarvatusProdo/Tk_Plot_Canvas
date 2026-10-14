"""Conversion between Matplotlib/Tk values and the French names shown in combo boxes."""

from typing import Any


def displayed_names(names: dict[Any, str]) -> list[str]:
    """Return the names to put in a combo box.

    Args:
        names: Values mapped to their displayed names.

    Returns:
        The displayed names, in order.
    """
    return list(names.values())


def name_of(names: dict[Any, str], value: Any) -> str:
    """Return the displayed name of a value.

    Args:
        names: Values mapped to their displayed names.
        value: Value to name.

    Returns:
        Its name, or the value as text when it has none.
    """
    return names.get(value, str(value))


def value_of(names: dict[Any, str], name: str) -> Any:
    """Return the value of a displayed name.

    Args:
        names: Values mapped to their displayed names.
        name: Name selected in a combo box.

    Returns:
        The matching value, or ``name`` itself when it names no value.
    """
    return next((value for value, text in names.items() if text == name), name)

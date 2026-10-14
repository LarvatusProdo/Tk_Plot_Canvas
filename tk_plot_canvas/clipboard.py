"""Copy of an image to the Windows clipboard, as a device-independent bitmap (DIB).

Only Windows is supported: Tk itself can only put text in the clipboard.
"""

import ctypes
import struct
import sys
from typing import Any

import numpy as np

CF_DIB = 8
GMEM_MOVEABLE = 0x0002
BITMAP_INFO_HEADER_SIZE = 40
BITS_PER_PIXEL = 32
BI_RGB = 0
# Channel order of a 32-bit DIB pixel (blue, green, red, reserved) taken from RGBA.
BGRA_FROM_RGBA = [2, 1, 0, 3]


def is_image_copy_supported() -> bool:
    """Tell whether images can be copied to the clipboard on this system.

    Returns:
        True on Windows.
    """
    return sys.platform == "win32"


def rgba_to_dib(rgba: np.ndarray) -> bytes:
    """Encode an RGBA image as a bottom-up 32-bit DIB.

    Args:
        rgba: Array of shape ``(height, width, 4)`` with 8-bit channels.

    Returns:
        The BITMAPINFOHEADER followed by the pixels.
    """
    height, width = rgba.shape[:2]
    pixels = np.ascontiguousarray(rgba[::-1, :, BGRA_FROM_RGBA]).tobytes()
    header = struct.pack(
        "<IiiHHIIiiII",
        BITMAP_INFO_HEADER_SIZE,
        width,
        height,
        1,
        BITS_PER_PIXEL,
        BI_RGB,
        len(pixels),
        0,
        0,
        0,
        0,
    )
    return header + pixels


def _windows_libraries() -> tuple[Any, Any]:
    """Load kernel32 and user32 with the signatures used here.

    Returns:
        ``(kernel32, user32)``.
    """
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
    user32.OpenClipboard.argtypes = [ctypes.c_void_p]
    user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
    user32.SetClipboardData.restype = ctypes.c_void_p
    return kernel32, user32


def _global_memory(kernel32: Any, data: bytes) -> int:
    """Copy bytes into movable global memory, as the clipboard requires.

    Args:
        kernel32: Loaded kernel32 library.
        data: Bytes to copy.

    Returns:
        The memory handle.

    Raises:
        OSError: If the memory cannot be allocated.
    """
    handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    pointer = kernel32.GlobalLock(handle)
    ctypes.memmove(pointer, data, len(data))
    kernel32.GlobalUnlock(handle)
    return handle


def copy_image_to_clipboard(rgba: np.ndarray) -> None:
    """Put an RGBA image in the Windows clipboard.

    Args:
        rgba: Array of shape ``(height, width, 4)`` with 8-bit channels.

    Raises:
        OSError: If the clipboard cannot be opened or filled.
    """
    kernel32, user32 = _windows_libraries()
    handle = _global_memory(kernel32, rgba_to_dib(rgba))
    if not user32.OpenClipboard(None):
        kernel32.GlobalFree(handle)
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        user32.EmptyClipboard()
        if not user32.SetClipboardData(CF_DIB, handle):
            kernel32.GlobalFree(handle)
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        user32.CloseClipboard()

"""
Clipboard Keyboard Simulator

Reads text from the Windows clipboard and simulates typing it out
keystroke-by-keystroke using the Win32 SendInput API.

Usage:
    python clipboard_typer.py [--delay SECONDS] [--interval MS]

    --delay     Seconds to wait before typing starts (default: 3).
                Gives you time to focus the target window.
    --interval  Milliseconds between each keystroke (default: 5).
                Increase if the target app drops characters.

No pip dependencies required — uses only the Python standard library + ctypes.
"""

import argparse
import ctypes
import ctypes.wintypes
import sys
import time

# ── Win32 constants ──────────────────────────────────────────────────────────

CF_UNICODETEXT = 13

INPUT_KEYBOARD = 1
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_KEYUP = 0x0002

VK_RETURN = 0x0D
VK_ESCAPE = 0x1B


# ── Win32 structures for SendInput ──────────────────────────────────────────
# All three union members must be present so that sizeof(INPUT) matches what
# Windows expects (40 bytes on x64).  Without MOUSEINPUT (the largest member),
# the struct is too small and SendInput silently ignores every call.

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.wintypes.LONG),
        ("dy", ctypes.wintypes.LONG),
        ("mouseData", ctypes.wintypes.DWORD),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.wintypes.WORD),
        ("wScan", ctypes.wintypes.WORD),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.wintypes.DWORD),
        ("wParamL", ctypes.wintypes.WORD),
        ("wParamH", ctypes.wintypes.WORD),
    ]


class INPUT(ctypes.Structure):
    class _INPUT_UNION(ctypes.Union):
        _fields_ = [
            ("mi", MOUSEINPUT),
            ("ki", KEYBDINPUT),
            ("hi", HARDWAREINPUT),
        ]

    _fields_ = [
        ("type", ctypes.wintypes.DWORD),
        ("union", _INPUT_UNION),
    ]


# ── Clipboard helpers ───────────────────────────────────────────────────────

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Set correct 64-bit-safe return types for Win32 clipboard/memory functions.
# Without these, ctypes defaults to c_int (32-bit) and truncates 64-bit
# handles/pointers on x64 Windows, causing access violations.
user32.GetClipboardData.restype = ctypes.c_void_p
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]


def get_clipboard_text() -> str:
    """Return the current Unicode text on the clipboard, or empty string."""
    if not user32.OpenClipboard(0):
        raise RuntimeError("Cannot open clipboard")
    try:
        handle = user32.GetClipboardData(CF_UNICODETEXT)
        if not handle:
            return ""
        ptr = kernel32.GlobalLock(handle)
        if not ptr:
            return ""
        try:
            return ctypes.wstring_at(ptr)
        finally:
            kernel32.GlobalUnlock(handle)
    finally:
        user32.CloseClipboard()


# ── Typing simulation ──────────────────────────────────────────────────────

def _make_unicode_key_events(char: str) -> list[INPUT]:
    """Create a press + release INPUT pair for a single Unicode character."""
    code = ord(char)
    down = INPUT()
    down.type = INPUT_KEYBOARD
    down.union.ki.wVk = 0
    down.union.ki.wScan = code
    down.union.ki.dwFlags = KEYEVENTF_UNICODE

    up = INPUT()
    up.type = INPUT_KEYBOARD
    up.union.ki.wVk = 0
    up.union.ki.wScan = code
    up.union.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP

    return [down, up]


def _make_vk_key_events(vk: int) -> list[INPUT]:
    """Create a press + release INPUT pair for a virtual-key code."""
    down = INPUT()
    down.type = INPUT_KEYBOARD
    down.union.ki.wVk = vk
    down.union.ki.dwFlags = 0

    up = INPUT()
    up.type = INPUT_KEYBOARD
    up.union.ki.wVk = vk
    up.union.ki.dwFlags = KEYEVENTF_KEYUP

    return [down, up]


def _escape_pressed() -> bool:
    """Return True if the Escape key is currently held down."""
    # GetAsyncKeyState returns a SHORT; the high bit (0x8000) means
    # the key is currently down.
    return bool(user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000)


def type_text(text: str, interval_ms: float = 5) -> None:
    """Simulate typing *text* one character at a time.  Press Escape to stop."""
    interval_s = interval_ms / 1000.0
    total = len(text)

    for i, char in enumerate(text, 1):
        if _escape_pressed():
            print(f"\n  Escape pressed — stopped after {i - 1}/{total} characters.")
            return

        # For newlines, press the Enter virtual key so apps that don't
        # respond to a unicode U+000A still get a proper newline.
        if char in ("\n", "\r"):
            events = _make_vk_key_events(VK_RETURN)
        else:
            events = _make_unicode_key_events(char)

        arr = (INPUT * len(events))(*events)
        user32.SendInput(len(events), arr, ctypes.sizeof(INPUT))

        if interval_s > 0:
            time.sleep(interval_s)

        # Progress feedback every 500 chars (printed to the console).
        if i % 500 == 0 or i == total:
            print(f"\r  Typed {i}/{total} characters", end="", flush=True)

    print()  # final newline after progress


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Type clipboard contents via simulated keystrokes."
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3,
        help="Seconds to wait before typing begins (default: 3).",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5,
        help="Milliseconds between keystrokes (default: 5).",
    )
    args = parser.parse_args()

    # 1. Read clipboard
    try:
        text = get_clipboard_text()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not text:
        print("Clipboard is empty — nothing to type.", file=sys.stderr)
        sys.exit(1)

    lines = text.count("\n")
    print(f"Clipboard: {len(text)} characters, {lines} line(s).")

    # 2. Countdown so the user can focus the target window
    delay = args.delay
    print(f"Typing will begin in {delay:.0f} seconds — switch to the target window!")
    print("Press Escape at any time to stop.")
    deadline = time.time() + delay
    while True:
        remaining = deadline - time.time()
        if remaining <= 0:
            break
        print(f"\r  Starting in {remaining:.1f}s ... ", end="", flush=True)
        time.sleep(0.1)
    print("\r  Go!                          ")

    # 3. Type it out
    type_text(text, interval_ms=args.interval)
    print("Done.")


if __name__ == "__main__":
    main()

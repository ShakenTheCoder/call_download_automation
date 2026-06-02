#!/usr/bin/env python3
"""
kb_core.py
----------
Shared helpers for the KEYBOARD-FIRST (hybrid) NICE Web Player call download automation.

Philosophy (hybrid):
  * KEYBOARD is used for the practical, fast actions:
      - selecting exactly N rows (Shift + Down)
      - opening the right-click context menu (Shift + F10)
      - navigating to the 4th menu item "Save Calls" (Down x4 + Enter)
      - closing the final "Done" dialog (Enter)
  * MOUSE (calibrated coordinates, captured once via kb_calibrate.py) is used only
    for the 3 fields inside the custom "Save Calls" dialog whose Tab order is unknown:
      - Location field
      - "WAV - Voice only" radio button
      - "Save" button
"""

import os
import sys
import json
import time
import pyautogui

try:
    import pygetwindow as gw
except ImportError:
    gw = None

# Slamming the mouse into any screen corner aborts the script instantly.
pyautogui.FAILSAFE = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "kb_config.json")


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
def load_config():
    """Load configuration from kb_config.json."""
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(cfg):
    """Persist configuration back to kb_config.json (used by the calibrator)."""
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


CONFIG = load_config()


def _delay(name, default=0.2):
    return CONFIG.get("delays", {}).get(name, default)


# ---------------------------------------------------------------------------
# Window activation
# ---------------------------------------------------------------------------
def activate_window():
    """Bring the target VM / Internet Explorer (NICE) window to the foreground."""
    cfg = CONFIG.get("window_activation", {})
    if not cfg.get("enable", True):
        return True

    title_part = cfg.get("title_contains", "NICE")
    print(f"[*] Searching for a window containing: \"{title_part}\"...")

    if gw is not None and sys.platform.startswith("win"):
        candidates = gw.getWindowsWithTitle(title_part) or [
            w for w in gw.getAllWindows() if title_part.lower() in w.title.lower()
        ]
        for win in candidates:
            try:
                if win.isMinimized:
                    win.restore()
                win.activate()
                print(f"[+] Activated window: \"{win.title}\"")
                time.sleep(1.0)
                return True
            except Exception:
                continue
        print(f"[-] Warning: no window containing \"{title_part}\" was found.")

    print("[*] Please click inside the NICE / VM window now. Starting in 3 seconds...")
    for i in range(3, 0, -1):
        print(f"    ...{i}")
        time.sleep(1.0)
    return True


# ---------------------------------------------------------------------------
# Keyboard primitives
# ---------------------------------------------------------------------------
def press(key, times=1, desc=None):
    """Press a single key one or more times."""
    for _ in range(times):
        pyautogui.press(key)
        time.sleep(_delay("after_key", 0.12))
    if desc:
        print(f"[kb] {desc}: pressed '{key}' x{times}")


def hotkey(*keys, desc=None):
    """Press a key combination, e.g. hotkey('shift', 'f10')."""
    pyautogui.hotkey(*keys)
    time.sleep(_delay("after_key", 0.12))
    if desc:
        print(f"[kb] {desc}: {' + '.join(keys)}")


def shift_press(key, times=1, desc=None):
    """Press a key while holding Shift (used to extend a row selection)."""
    pyautogui.keyDown("shift")
    try:
        for _ in range(times):
            pyautogui.press(key)
            time.sleep(_delay("after_key", 0.12))
    finally:
        pyautogui.keyUp("shift")
    if desc:
        print(f"[kb] {desc}: Shift + '{key}' x{times}")


def type_text(text, desc=None):
    """Type a string of text."""
    pyautogui.typewrite(text, interval=0.02)
    time.sleep(_delay("after_type", 0.4))
    if desc:
        print(f"[kb] {desc}: typed \"{text}\"")


# ---------------------------------------------------------------------------
# Mouse primitives (calibrated coordinates only)
# ---------------------------------------------------------------------------
def get_coord(name):
    """Return the [x, y] coordinate stored in config for `name`, or None."""
    c = CONFIG.get("coords", {}).get(name)
    if isinstance(c, (list, tuple)) and len(c) == 2:
        return int(c[0]), int(c[1])
    return None


def click_coord(name, desc=None, clicks=1):
    """Move to and click a calibrated coordinate. Returns False if not calibrated."""
    coord = get_coord(name)
    if coord is None:
        print(f"[-] Coordinate '{name}' is not calibrated. Run kb_calibrate.py first.")
        return False
    x, y = coord
    pyautogui.moveTo(x, y, duration=0.3)
    pyautogui.click(clicks=clicks)
    time.sleep(_delay("after_field_click", 0.4))
    print(f"[mouse] {desc or name}: clicked ({x}, {y})")
    return True


def coords_ready(required):
    """Verify that every coordinate name in `required` has been calibrated."""
    missing = [name for name in required if get_coord(name) is None]
    if missing:
        print(f"[-] Missing calibrated coordinates: {', '.join(missing)}")
        print("[-] Run:  python kb_calibrate.py")
        return False
    return True


# ---------------------------------------------------------------------------
# Shared WORKFLOW steps (used by every download script)
# ---------------------------------------------------------------------------
# Coordinates that MUST be calibrated before any download can run.
REQUIRED_COORDS = ["first_row", "save_calls_menu_item", "location_field", "wav_radio", "save_button"]


def resolve_location():
    """Return the path to type into the Location field of the Save Calls dialog."""
    loc = CONFIG.get("download", {}).get("location_path", "").strip()
    if loc:
        return loc
    # Default to the (Windows) user's Downloads folder.
    return os.path.join(os.path.expanduser("~"), "Downloads")


def select_rows(num_rows, is_first_selection):
    """
    Select exactly `num_rows` rows using Windows keyboard shortcuts.

    is_first_selection=True  -> click the first row (focus), then Shift+Down xN-1
    is_first_selection=False -> Down x1 (advance past previous batch, auto-scrolls),
                                then Shift+Down xN-1
    """
    delays = CONFIG.get("delays", {})
    if is_first_selection:
        print("[*] Focusing the first row of the grid...")
        if not click_coord("first_row", "First call row"):
            return False
        if num_rows > 1:
            shift_press(CONFIG["keys"]["select_extend_key"], num_rows - 1,
                        desc=f"Select {num_rows} rows")
    else:
        press(CONFIG["keys"]["advance_key"], 1, desc="Advance to next unselected row")
        if num_rows > 1:
            shift_press(CONFIG["keys"]["select_extend_key"], num_rows - 1,
                        desc=f"Select next {num_rows} rows")
    time.sleep(delays.get("after_select", 0.6))
    return True


def open_save_calls_menu():
    """Right-click the selected batch and click the calibrated 'Save Calls' menu item."""
    delays = CONFIG.get("delays", {})
    coord = get_coord("first_row")
    if coord is None:
        print("[-] Error: first_row is not calibrated.")
        return False

    print("[*] Right-clicking on the selected batch...")
    pyautogui.moveTo(coord[0], coord[1], duration=0.3)
    pyautogui.rightClick()
    time.sleep(delays.get("context_menu_load", 0.9))

    print("[*] Clicking the 'Save Calls' menu item...")
    if not click_coord("save_calls_menu_item", "Save Calls menu item"):
        return False

    time.sleep(delays.get("dialog_load", 1.8))
    return True


def fill_dialog(location_path, set_location=True):
    """Handle the Save Calls dialog: Location + WAV radio + Save (calibrated clicks)."""
    if set_location:
        print(f"[*] Setting download Location -> {location_path}")
        if not click_coord("location_field", "Location field"):
            return False
        hotkey("ctrl", "a", desc="Select existing location text")
        press("delete", 1, desc="Clear location")
        type_text(location_path, desc="Type download location")

    print("[*] Selecting format: WAV - Voice only")
    if not click_coord("wav_radio", "WAV - Voice only radio"):
        return False

    print("[*] Clicking Save...")
    if not click_coord("save_button", "Save button"):
        return False
    return True


def wait_and_close():
    """Wait ~32s for the save to finish, then close the 'Done' dialog."""
    wait_s = CONFIG.get("timeouts", {}).get("save_complete_wait", 32.0)
    print(f"[*] Waiting ~{wait_s:.0f}s for the calls to finish saving...")
    time.sleep(wait_s)

    # Prefer a calibrated Close click; fall back to the keyboard close key.
    if not click_coord("close_button", "Close button"):
        close_key = CONFIG["keys"].get("close_dialog_key", "enter")
        print(f"[*] No 'close_button' coord; pressing '{close_key}' to close the dialog.")
        press(close_key, 1, desc="Close Done dialog")
    time.sleep(0.8)


def do_batch(num_rows, is_first_selection, location_path, set_location):
    """Run one full save cycle for `num_rows` calls."""
    if not select_rows(num_rows, is_first_selection):
        return False
    open_save_calls_menu()
    if not fill_dialog(location_path, set_location=set_location):
        return False
    wait_and_close()
    return True

#!/usr/bin/env python3
"""
kb_calibrate.py
---------------
One-time calibration helper for the hybrid keyboard automation.

It captures the screen coordinates of the few elements that the automation
clicks with the mouse (because their keyboard Tab order is unknown):

  1. first_row       -> the very FIRST call row in the grid (used once to focus
                        the grid before keyboard selection begins)
  2. location_field  -> the "Location" text field inside the Save Calls dialog
  3. wav_radio       -> the "WAV - Voice only" radio button
  4. save_button     -> the "Save" button in the Save Calls dialog
  5. close_button    -> the "Close" button in the final "Done" dialog

On Windows, hover your mouse over each item and press F9. The keypress is captured globally in the background, meaning you do NOT need to click back on the terminal! On other systems, the script uses a 5-second countdown.
"""

import time
import sys
import pyautogui
from kb_core import load_config, save_config

# Background key listener for Windows using built-in ctypes
IS_WINDOWS = sys.platform.startswith("win")
if IS_WINDOWS:
    import ctypes
    import winsound
else:
    ctypes = None

# (key in config["coords"], human description, hint on how to set up the screen)
STEPS = [
    ("first_row", "FIRST call row in the grid",
     "Make sure the NICE results grid is visible. Hover over the first call row."),
    ("save_calls_menu_item", "'Save Calls' option in right-click context menu",
     "Right-click a row manually to show the context menu. Hover over 'Save Calls'."),
    ("location_field", "'Location' text field in Save Calls dialog",
     "Open the Save Calls dialog (Right-click -> Save Calls). Hover over the Location text box."),
    ("wav_radio", "'WAV - Voice only' radio button",
     "Same dialog open. Hover over the WAV - Voice only radio circle."),
    ("save_button", "'Save' button in Save Calls dialog",
     "Same dialog open. Hover over the blue Save button."),
    ("close_button", "'Close' button in the 'Done' dialog",
     "This appears after a save completes. If not visible now, you can re-run "
     "calibration later for just this item."),
]


def capture(description, setup_hint):
    print("\n" + "=" * 60)
    print(f"  CALIBRATE: {description}")
    print("=" * 60)
    print(f"  Hint: {setup_hint}")
    
    if IS_WINDOWS:
        print("  --> Hover the mouse over the target, then press [F9] on your keyboard.")
        print("      (You do NOT need to switch back to this terminal. Just press F9!)")
        print("      * To SKIP this item, press [ESC] instead.")
        print("      Waiting for your keypress...")
        
        # Flush key state before waiting
        ctypes.windll.user32.GetAsyncKeyState(0x78) # F9
        ctypes.windll.user32.GetAsyncKeyState(0x1B) # ESC
        
        while True:
            # Check F9 (0x78)
            if (ctypes.windll.user32.GetAsyncKeyState(0x78) & 0x8000) != 0:
                x, y = pyautogui.position()
                # Play a system beep to confirm capture
                winsound.MessageBeep(winsound.MB_OK)
                print(f"  [+] Captured ({x}, {y})")
                
                # Crucial Fix: Wait for F9 to be released to prevent rapid multi-triggering
                while (ctypes.windll.user32.GetAsyncKeyState(0x78) & 0x8000) != 0:
                    time.sleep(0.05)
                
                return [int(x), int(y)]
            # Check ESC (0x1B)
            if (ctypes.windll.user32.GetAsyncKeyState(0x1B) & 0x8000) != 0:
                print("  [*] Skipped.")
                
                # Wait for ESC release
                while (ctypes.windll.user32.GetAsyncKeyState(0x1B) & 0x8000) != 0:
                    time.sleep(0.05)
                    
                return None
            time.sleep(0.05)
    else:
        # Non-Windows countdown fallback (robust, no focus needed)
        print("  --> Hover the mouse over the target.")
        print("      Capturing automatically in 5 seconds (no focus switch needed)...")
        for i in range(5, 0, -1):
            print(f"      {i}...")
            time.sleep(1.0)
        x, y = pyautogui.position()
        print("\a") # System beep on Mac/Linux
        print(f"  [+] Captured ({x}, {y})")
        return [int(x), int(y)]


def main():
    print("##############################################")
    print("   Hybrid Keyboard Automation - CALIBRATION   ")
    print("##############################################")
    print("\nYou will hover over a few screen elements and capture their position.")
    if IS_WINDOWS:
        print("On Windows, just hover your mouse on the target and press F9.")
        print("There is NO need to switch back to this terminal!")
    else:
        print("On Mac/Linux, the script will countdown from 5 seconds for each item.")
    print("Tip: keep this terminal and the NICE/VM window both visible.\n")

    cfg = load_config()
    cfg.setdefault("coords", {})

    for key, desc, hint in STEPS:
        existing = cfg["coords"].get(key)
        if existing:
            print(f"\n[i] '{key}' is already set to {existing}.")
            answer = input("    Re-calibrate it? [y/N]: ").strip().lower()
            if answer != "y":
                continue
        else:
            print(f"\n[i] '{key}' is NOT set yet.")
            answer = input("    Calibrate it now? [Y/n]: ").strip().lower()
            if answer == "n":
                continue
        result = capture(desc, hint)
        if result is not None:
            cfg["coords"][key] = result
            save_config(cfg)  # save incrementally so progress is never lost
            print(f"  [saved] coords.{key} = {result}")

    print("\n[+] Calibration finished. Current coordinates:")
    for key, _, _ in STEPS:
        print(f"    {key:14s} = {cfg['coords'].get(key)}")
    print("\nYou can now run:  python kb_download_all.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Calibration cancelled.")

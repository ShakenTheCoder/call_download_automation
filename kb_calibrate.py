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

For each item: hover your mouse over it, then press ENTER in this terminal.
The position is read live with pyautogui.position() and saved to kb_config.json.
"""

import time
import pyautogui
from kb_core import load_config, save_config

# (key in config["coords"], human description, hint on how to set up the screen)
STEPS = [
    ("first_row", "FIRST call row in the grid",
     "Make sure the NICE results grid is visible. Hover over the first call row."),
    ("location_field", "'Location' text field in Save Calls dialog",
     "Open the Save Calls dialog once (select a row -> right-click -> Save Calls)."),
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
    print("  -> Hover the mouse over the target, then press ENTER here.")
    print("     (type 's' then ENTER to SKIP this item)")
    choice = input("  Ready? [ENTER to capture / s to skip]: ").strip().lower()
    if choice == "s":
        print("  [*] Skipped.")
        return None
    x, y = pyautogui.position()
    print(f"  [+] Captured ({x}, {y})")
    return [int(x), int(y)]


def main():
    print("##############################################")
    print("   Hybrid Keyboard Automation - CALIBRATION   ")
    print("##############################################")
    print("\nYou will hover over a few screen elements and press ENTER to record them.")
    print("Tip: keep this terminal and the NICE/VM window both visible.\n")

    cfg = load_config()
    cfg.setdefault("coords", {})

    for key, desc, hint in STEPS:
        existing = cfg["coords"].get(key)
        if existing:
            print(f"\n[i] '{key}' is already set to {existing}.")
            if input("    Re-calibrate it? [y/N]: ").strip().lower() != "y":
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

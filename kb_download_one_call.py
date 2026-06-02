#!/usr/bin/env python3
"""
kb_download_one_call.py
-----------------------
Downloads exactly ONE call from the NICE Web Player using the hybrid
keyboard + calibrated-click workflow. Ideal for a quick end-to-end test.

Windows keybinds used:
  - click first row (focus)        -> calibrated mouse click
  - Shift+F10                      -> open right-click context menu
  - Down x4 + Enter                -> choose the 4th item "Save Calls"
  - Location / WAV / Save          -> calibrated mouse clicks (+ typing)
  - wait ~32s, then Enter/Close    -> close the "Done" dialog
"""

import sys
from kb_core import (
    CONFIG,
    activate_window,
    coords_ready,
    do_batch,
    resolve_location,
    REQUIRED_COORDS,
)


def main():
    print("=============================================")
    print("   Hybrid Keyboard Automation - ONE CALL     ")
    print("=============================================")

    if not coords_ready(REQUIRED_COORDS):
        sys.exit(1)

    location = resolve_location()
    print(f"[i] Format: WAV - Voice only   Location: {location}")
    print("[!] Make sure the NICE grid is visible with the first row in view.")
    input("[*] Press ENTER to download one call...")

    if not activate_window():
        sys.exit(1)

    ok = do_batch(num_rows=1, is_first_selection=True,
                  location_path=location, set_location=True)
    print("\n[+] One call downloaded successfully!" if ok
          else "\n[-] Failed - check your calibration and timings.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Interrupted by user.")

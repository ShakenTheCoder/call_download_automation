#!/usr/bin/env python3
"""
kb_download_batch_20.py
-----------------------
Downloads ONE batch of 20 calls from the NICE Web Player using the hybrid
keyboard + calibrated-click workflow. Use this to verify the full batch flow
before launching the complete 1500-call run.

Windows keybinds used:
  - click first row (focus)        -> calibrated mouse click
  - Shift+Down x19                 -> extend selection to exactly 20 rows
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
    print("   Hybrid Keyboard Automation - BATCH OF 20  ")
    print("=============================================")

    if not coords_ready(REQUIRED_COORDS):
        sys.exit(1)

    rows = CONFIG["batch"]["rows_per_batch"]
    location = resolve_location()
    print(f"[i] Rows: {rows}   Format: WAV - Voice only   Location: {location}")
    print("[!] Scroll the NICE grid to the TOP so the first row is in view.")
    input("[*] Press ENTER to download a batch of 20...")

    if not activate_window():
        sys.exit(1)

    ok = do_batch(num_rows=rows, is_first_selection=True,
                  location_path=location, set_location=True)
    print("\n[+] Batch of 20 downloaded successfully!" if ok
          else "\n[-] Failed - check your calibration and timings.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Interrupted by user.")

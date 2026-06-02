#!/usr/bin/env python3
"""
kb_download_all_1500.py
-----------------------
Downloads ALL calls from the NICE Web Player in batches of 20 until 1500 calls
(75 batches) are saved, using the hybrid keyboard + calibrated-click workflow.

Per batch:
  - first batch : click first row + Shift+Down x19         (select 20)
  - later batches: Down x1 + Shift+Down x19                 (scroll 20, select 20)
  - Shift+F10 -> Down x4 -> Enter                            (open "Save Calls")
  - Location / WAV / Save (calibrated clicks)
  - wait ~32s -> Close

Resumable: progress is saved to kb_session.json after every batch, so a VPN/VM
drop can be resumed from the next batch.
Fail-safe: slam the mouse into any screen corner to abort instantly.
"""

import os
import sys
import json

from kb_core import (
    CONFIG,
    activate_window,
    coords_ready,
    do_batch,
    resolve_location,
    REQUIRED_COORDS,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_PATH = os.path.join(BASE_DIR, "kb_session.json")


def load_session():
    if os.path.exists(SESSION_PATH):
        try:
            with open(SESSION_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_completed_batch": 0}


def save_session(batch_num):
    try:
        with open(SESSION_PATH, "w") as f:
            json.dump({"last_completed_batch": batch_num}, f, indent=2)
    except Exception as e:
        print(f"[-] Warning: could not save session: {e}")


def main():
    print("==================================================")
    print("   NICE Hybrid Keyboard Automation - ALL (1500)    ")
    print("==================================================")

    if not coords_ready(REQUIRED_COORDS):
        sys.exit(1)

    rows = CONFIG["batch"]["rows_per_batch"]
    total_calls = CONFIG["batch"]["total_calls"]
    total_batches = (total_calls + rows - 1) // rows
    location = resolve_location()

    print(f"[i] Rows per batch : {rows}")
    print(f"[i] Total calls    : {total_calls}  ->  {total_batches} batches")
    print(f"[i] Format         : WAV - Voice only")
    print(f"[i] Location       : {location}")

    session = load_session()
    last_completed = session.get("last_completed_batch", 0)
    start_batch = 1

    if last_completed > 0:
        print(f"\n[!] Previous session found. Last completed batch: {last_completed}")
        if input(f"[?] Resume from batch {last_completed + 1}? (y/n): ").strip().lower() == "y":
            start_batch = last_completed + 1
            print(f"[!] Scroll the grid so the NEXT unselected row "
                  f"(call #{last_completed * rows + 1}) is the active/highlighted row.")
            input("[*] Press ENTER when the grid is positioned correctly...")
        else:
            print("[*] Starting fresh from batch 1 (grid must be at the TOP).")
            input("[*] Press ENTER to start...")
    else:
        print("\n[!] Ensure the NICE results grid is scrolled to the very TOP.")
        input("[*] Press ENTER to start...")

    if not activate_window():
        sys.exit(1)

    print(f"\n[*] Running batches {start_batch} -> {total_batches}...\n")

    batch_num = start_batch
    while batch_num <= total_batches:
        print("--------------------------------------------------")
        print(f">>> Batch {batch_num}/{total_batches} "
              f"(calls {(batch_num - 1) * rows + 1}-{batch_num * rows}) <<<")
        print("--------------------------------------------------")

        activate_window()
        # The first batch of THIS run re-focuses the first visible row; the rest
        # advance with Down to scroll exactly 20 rows. Location only set once.
        is_first = (batch_num == start_batch)
        ok = do_batch(num_rows=rows, is_first_selection=is_first,
                      location_path=location, set_location=is_first)

        if not ok:
            print(f"\n[-] Batch {batch_num} failed.")
            print("    1) Retry this batch")
            print("    2) Stop (progress saved through the previous batch)")
            if input("    Choice (1/2): ").strip() == "1":
                start_batch = batch_num  # treat retry as a fresh re-focus
                continue
            print(f"[-] Stopping. Progress saved through batch {batch_num - 1}.")
            sys.exit(1)

        save_session(batch_num)
        print(f"[+] Batch {batch_num} done. Progress saved.")
        batch_num += 1

    if os.path.exists(SESSION_PATH):
        try:
            os.remove(SESSION_PATH)
        except Exception:
            pass

    print("\n==================================================")
    print("   ALL BATCHES COMPLETE - 1500 calls downloaded!   ")
    print("==================================================")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Interrupted by user.")
    except Exception as e:
        print(f"\n[-] Unexpected error: {e}")

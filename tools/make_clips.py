# SPDX-FileCopyrightText: 2026 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Cut song clips for the board from tools/songs.csv (runs on the PC, not the board)

Each row with a start time becomes sounds/<name>_22k.mp3: 22050 Hz mono,
48 kbps, tags stripped, to match the mixer in sound.py, with a short fade in
and a fade out. Rows with no start are skipped. length is optional.

    python tools/make_clips.py
"""

import csv
import os
import subprocess
import sys

SOURCE_DIR = r"D:\Muzak\JohnsMusic"
HERE = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(HERE, "..", "sounds")
SONGS_CSV = os.path.join(HERE, "songs.csv")

LENGTH = 90  # seconds, when the row gives none
FADE_IN = 0.5  # seconds
FADE_OUT = 3  # seconds
BOARD_SPACE_KB = 7000  # roughly what CIRCUITPY holds, code & libraries included


def make_clip(row):
    """Cut one clip with ffmpeg; returns its file name"""
    start = float(row["start"])
    length = float(row["length"] or LENGTH)
    out_name = row["name"] + "_22k.mp3"
    fades = "afade=t=in:d={},afade=t=out:st={}:d={}".format(
        FADE_IN, length - FADE_OUT, FADE_OUT
    )
    subprocess.run(
        [
            "ffmpeg", "-v", "error", "-y",
            "-ss", str(start), "-t", str(length),
            "-i", os.path.join(SOURCE_DIR, row["source"]),
            "-af", fades, "-ac", "1", "-ar", "22050", "-b:a", "48k",
            "-map_metadata", "-1", "-id3v2_version", "0", "-write_xing", "0",
            os.path.join(SOUNDS_DIR, out_name),
        ],
        check=True,
    )
    return out_name


def main():
    with open(SONGS_CSV, encoding="utf-8", newline="") as f:
        rows = [row for row in csv.DictReader(f) if row["start"].strip()]
    if not rows:
        sys.exit("No start times in " + SONGS_CSV)

    made = []
    for row in rows:
        made.append(make_clip(row))
        print("made", made[-1])

    total_kb = sum(
        os.path.getsize(os.path.join(SOUNDS_DIR, name)) for name in made
    ) // 1024
    print("\n{} clips, {} KB (board holds about {} KB in all)".format(
        len(made), total_kb, BOARD_SPACE_KB
    ))
    print("\nFor mp3files in config.py:")
    for name in made:
        print('    "{}",'.format(name))


if __name__ == "__main__":
    main()

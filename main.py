#!/usr/bin/env python3
"""Entry for make.fun news-image-20261123.

Writes the entry image to /output/entry.png. The image is a newspaper
front page summing up the world news of Monday 23 November 2026: a
burning Russian cargo ship in the Baltic, a drone strike on homes in
the Kyiv region, Iran's strikes on US bases in Bahrain, COP31's draft
dropping the words "fossil fuels", and a deadly factory fire in
Indonesia, plus a ticker of the day's other stories.

The image was composed by build_image.py (same repository) from four
news-style photos generated during the build session and one drawn
stat panel, and is shipped here as entry.png. This program only copies
it, using the standard library, so both grader runs write identical
bytes. No network is used.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(HERE, "entry.png")
    os.makedirs("/output", exist_ok=True)
    dst = os.path.join("/output", "entry.png")
    shutil.copyfile(src, dst)
    print("wrote %s (%d bytes)" % (dst, os.path.getsize(dst)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

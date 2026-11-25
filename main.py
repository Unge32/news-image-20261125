#!/usr/bin/env python3
"""THE ATLAS LEDGER - Wednesday 25 November 2026.

Entrypoint: copies the finished 1024x1024 broadsheet (entry.png,
rendered at build time from 36 stories first reported 25 Nov 2026)
to $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png on the
grader, or ./out/entry.png when run by hand).

Pure Python 3 standard library, no network. The copy is
byte-identical every run, because the file copied never changes.
"""
import hashlib
import os
import shutil


def _sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        raise SystemExit(
            "entry.png is missing next to main.py - it must be committed "
            "to the repo, not just present at build time; rebuild it with "
            "render.py from stories.json, then commit it")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or (
        "/output" if os.path.isdir("/output") else "out")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    src_hash = _sha256(src)
    dst_hash = _sha256(dst)
    if src_hash != dst_hash:
        raise SystemExit(
            "copy mismatch: %s != %s" % (src_hash, dst_hash))
    print("wrote %s %d bytes sha256=%s"
          % (dst, os.path.getsize(dst), dst_hash))


if __name__ == "__main__":
    main()

"""Stall check: share of pixels that changed between consecutive screenshots, inside the content box only.

    uv run --with pillow python frame_diff.py shot1.png shot2.png ... [--box x0,y0,x1,y1]   (CSS px; default = whole image)

A pair with changed share below 0.1 % is a STALL: frozen, paused, modal, or input not reaching the content.
Mean diff alone is not enough: a small looping animation in a static scene scores like noise, so the metric is the
share of pixels whose gray value changed by more than 12.
"""
import os, sys

try:
    from PIL import Image
except ImportError:
    sys.exit("needs Pillow: run with `uv run --with pillow python frame_diff.py ...`")

STALL, PIXEL_DELTA, W = 0.001, 12, 160


def gray(path, box):
    im = Image.open(path).convert("L")
    if box:
        im = im.crop(box)
    small = im.resize((W, max(1, im.height * W // max(1, im.width))))
    return list(small.get_flattened_data() if hasattr(small, "get_flattened_data") else small.getdata())


def main():
    args, box = sys.argv[1:], None
    if "--box" in args:
        i = args.index("--box"); box = tuple(int(v) for v in args[i + 1].split(",")); del args[i:i + 2]
    if len(args) < 2:
        sys.exit(__doc__)
    frames = [gray(p, box) for p in args]
    stalled = 0
    for p, a, b in zip(args[1:], frames, frames[1:]):
        n = min(len(a), len(b)); d = [abs(a[i] - b[i]) for i in range(n)]
        share = sum(v > PIXEL_DELTA for v in d) / n; stalled += share < STALL
        print(f"{os.path.basename(p)}\tmean {sum(d) / n:.2f}\tchanged {share:.2%}\t{'STALL' if share < STALL else 'moving'}")
    print(f"moving intervals: {len(frames) - 1 - stalled}/{len(frames) - 1}")


if __name__ == "__main__":
    main()

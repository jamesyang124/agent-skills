#!/usr/bin/env python3
"""Function complexity for the pre-PR review (ado-open-pr Step 1.7).

Runs lizard on the changed source files at HEAD and at the base, and prints the functions that are new or grew
and are over the threshold (CCN above 15, or more than 80 lines).

usage: complexity.py --base <rev> [--repo <path>]
       complexity.py --self-test

Exit codes: 0 measured (the list may be empty), 3 lizard not available (neither `lizard` nor `uvx`),
2 other error. Run with `python3 -I`; it changes no file in the repository (the base copies go to a temp folder).
"""
import argparse
import csv
import io
import os
import shutil
import subprocess
import sys
import tempfile

EXTS = (".go", ".ts", ".tsx", ".js", ".jsx")
SKIP = ("_test.go", ".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx", ".test.js", ".spec.js", ".d.ts")
SKIP_DIRS = ("docs/", "specs/", "vendor/", "node_modules/", "mocks/", "testdata/", "fixtures/")
CCN_MAX, LEN_MAX = 15, 80


def lizard_cmd():
    if shutil.which("lizard"):
        return ["lizard"]
    if shutil.which("uvx"):
        return ["uvx", "lizard"]
    return None


def measure(cmd, cwd, files):
    if not files:
        return {}
    out = subprocess.run(cmd + ["--csv", *files], cwd=cwd, capture_output=True, text=True, check=True).stdout
    # CSV: NLOC, CCN, tokens, params, length, location, file, function, signature, start, end
    return {(r[6].lstrip("./"), r[7]): (int(r[1]), int(r[4]), int(r[9])) for r in csv.reader(io.StringIO(out)) if len(r) > 9}


def over(head, base):
    rows = []
    for key, (ccn, length, start) in sorted(head.items()):
        old = base.get(key)
        grew = old is None or ccn > old[0] or length > old[1]
        if grew and (ccn > CCN_MAX or length > LEN_MAX):
            was = f"{old[0]}/{old[1]}" if old else "new"
            rows.append(f"{key[0]}:{start} {key[1]} CCN {ccn} length {length} (base CCN/length {was})")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        head = {("a.go", "f"): (20, 10, 1), ("a.go", "g"): (16, 10, 5), ("a.go", "h"): (3, 90, 9), ("a.go", "k"): (5, 5, 20)}
        base = {("a.go", "f"): (20, 10, 1), ("a.go", "g"): (12, 10, 5)}
        assert over(head, base) == [
            "a.go:5 g CCN 16 length 10 (base CCN/length 12/10)",
            "a.go:9 h CCN 3 length 90 (base CCN/length new)",
        ], over(head, base)
        print("self-test ok")
        return 0
    if not a.base:
        ap.error("--base is required")
    cmd = lizard_cmd()
    if cmd is None:
        print("lizard not available: install uv (`brew install uv`, then `uvx lizard` works) or `pipx install lizard`")
        return 3
    git = ["git", "-C", a.repo]
    names = subprocess.run(git + ["diff", "--name-only", "--diff-filter=AM", f"{a.base}...HEAD"],
                           capture_output=True, text=True, check=True).stdout.split()
    files = [f for f in names if f.endswith(EXTS) and not f.endswith(SKIP) and not f.startswith(SKIP_DIRS)
             and "/generated/" not in f]
    with tempfile.TemporaryDirectory() as tmp:
        base_files = []
        for f in files:
            r = subprocess.run(git + ["show", f"{a.base}:{f}"], capture_output=True)
            if r.returncode == 0:
                p = os.path.join(tmp, f)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "wb") as fh:
                    fh.write(r.stdout)
                base_files.append(f)
        head = measure(cmd, a.repo, files)
        base = measure(cmd, tmp, base_files)
    rows = over(head, base)
    print(f"measured {len(head)} functions in {len(files)} files; {len(rows)} new or grown over CCN {CCN_MAX} / {LEN_MAX} lines")
    print("\n".join(rows))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as e:
        print(f"error: {' '.join(e.cmd)} failed: {e.stderr}", file=sys.stderr)
        sys.exit(2)

"""Human-demo recorder: local mouse (and optionally keyboard) events to a JSONL file. Started and stopped by the human.

    uv run --with pynput python record_input.py --check                      # preflight: can this process see input?
    uv run --with pynput python record_input.py --out demo.jsonl [--seconds 180] [--keys]
    kill -TERM $(cat demo.jsonl.pid)                                          # stop (the orchestrator does this)

Records: press/release (position, button, held_ms, dist moved while held), drag samples every 50 ms while a button is
down, and scroll. Keyboard is OFF by default. With --keys, only game keys (WASD, arrows, space, shift, ctrl, enter,
escape, tab, digits) are kept by name; every other key is masked as "*". The keyboard listener is global, so it also sees
typing in other apps (for example the chat with the agent); masking is what keeps that text out. Ctrl+C, SIGTERM or
--seconds stops it. Writes <out>.pid while running. Nothing leaves this machine.
macOS: the terminal needs Accessibility + Input Monitoring permission (System Settings -> Privacy & Security).
"""
import argparse, ctypes, ctypes.util, json, math, os, signal, sys, threading, time

try:
    from pynput import keyboard, mouse
except ImportError:
    sys.exit("needs pynput: run with `uv run --with pynput python record_input.py ...`")


def trusted():
    """macOS: True when this process may monitor input (Accessibility). Other OSes: assume yes."""
    if sys.platform != "darwin":
        return True
    lib = ctypes.cdll.LoadLibrary(ctypes.util.find_library("ApplicationServices"))
    lib.AXIsProcessTrusted.restype = ctypes.c_bool
    return bool(lib.AXIsProcessTrusted())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out"); ap.add_argument("--seconds", type=int, default=180)
    ap.add_argument("--keys", action="store_true", help="also record game keys (others masked)")
    ap.add_argument("--check", action="store_true", help="only check input-monitoring permission")
    a = ap.parse_args()
    ok = trusted()
    if a.check or not ok:
        print("READY_CHECK " + ("ok" if ok else "NOT TRUSTED: grant Accessibility + Input Monitoring to the app running this "
              "(Terminal / iTerm / Claude) in System Settings -> Privacy & Security, then restart that app"))
        sys.exit(0 if ok else 2)
    if not a.out:
        ap.error("--out is required")
    t0, lock, down, last = time.monotonic(), threading.Lock(), {}, [0.0]
    f = open(a.out, "w")

    def emit(**r):
        r["t"] = round((time.monotonic() - t0) * 1000)
        with lock:
            f.write(json.dumps(r) + "\n"); f.flush()

    def on_click(x, y, button, pressed):
        b = str(button).split(".")[-1]
        if pressed:
            down[b] = (x, y, time.monotonic()); emit(type="down", x=x, y=y, btn=b)
        else:
            x0, y0, s = down.pop(b, (x, y, time.monotonic()))
            emit(type="up", x=x, y=y, btn=b, held_ms=round((time.monotonic() - s) * 1000), dist=round(math.hypot(x - x0, y - y0)))

    def on_move(x, y):
        if down and time.monotonic() - last[0] >= 0.05:
            last[0] = time.monotonic(); emit(type="drag", x=x, y=y)

    def on_scroll(x, y, dx, dy):
        emit(type="scroll", x=x, y=y, dx=dx, dy=dy)

    GAME = set("wasdWASD0123456789") | {"up", "down", "left", "right", "space", "shift", "shift_r", "ctrl", "ctrl_r",
                                       "enter", "esc", "tab", "alt", "alt_r"}

    def key_name(k):
        n = getattr(k, "char", None) or str(k).replace("Key.", "")
        return n if n in GAME else "*"

    listeners = [mouse.Listener(on_click=on_click, on_move=on_move, on_scroll=on_scroll)]
    if a.keys:
        listeners.append(keyboard.Listener(on_press=lambda k: emit(type="key_down", key=key_name(k)),
                                           on_release=lambda k: emit(type="key_up", key=key_name(k))))
    pid = a.out + ".pid"; open(pid, "w").write(str(os.getpid()))
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    for l in listeners:
        l.start()
    emit(type="start", seconds=a.seconds, keys=a.keys)
    print(f"GO recording to {a.out} for {a.seconds}s{' (+ game keys, others masked)' if a.keys else ' (mouse only)'} - Ctrl+C / SIGTERM to stop", flush=True)
    try:
        stop.wait(a.seconds)
    except KeyboardInterrupt:
        pass
    for l in listeners:
        l.stop()
    emit(type="stop"); f.close()
    os.path.exists(pid) and os.remove(pid)
    print("saved", a.out, file=sys.stderr)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Tiny builder for clean .excalidraw diagrams (Excalifont, skill palette, bound text and arrows).
Import it from a throwaway script:  sys.path.insert(0, "<skill>/scripts"); from excalidraw_lib import *

    d = D("Title")
    d.box("a", "Service A\nline two", 40, 110, 280, 90, color=GREEN)          # key, label, x, y, w, h
    d.box("b", "DB", 440, 110, 280, 90, color=GRAY, shape="rectangle")         # shape: rectangle | ellipse | diamond
    d.arrow("a", "b", "label", dashed=False, both=False, lx=0, ly=0)            # keep labels short: gap between boxes >= ~120
    d.note("note text", x, y, w, h, color=YELLOW)                               # free-standing box (failure notes, authority notes)
    # sequence diagrams: boxes for lifeline heads + d.line(x, y1, x, y2) + d.msg(x_from, x_to, y, "label", dashed=False)
    d.save("out.excalidraw")

Layout rules that avoided overlaps in practice: 5 columns at x = 40 + 400*i with 280 wide boxes, rows 180 apart,
2-3 line labels <= 28 chars, edge labels <= 14 chars per line. Render and LOOK before delivering (references/excalidraw.md)."""
import json, math, random, pathlib
BLUE, GREEN, YELLOW, RED, GRAY, PURPLE, WHITE = "#a5d8ff", "#b2f2bb", "#ffd43b", "#ffc9c9", "#e9ecef", "#d0bfff", "#ffffff"
random.seed(7)

class D:
    def __init__(self, title):
        self.els, self.n, self.ids = [], 0, {}
        self.title = title
    def _id(self, p="e"): self.n += 1; return f"{p}{self.n:03d}"
    def _base(self, typ, x, y, w, h, **kw):
        e = dict(id=self._id(), type=typ, x=x, y=y, width=w, height=h, angle=0, strokeColor="#1e1e1e",
                 backgroundColor="transparent", fillStyle="solid", strokeWidth=2, strokeStyle="solid", roughness=1,
                 opacity=100, groupIds=[], frameId=None, roundness=None, seed=random.randint(1, 2**31),
                 version=1, versionNonce=random.randint(1, 2**31), isDeleted=False, boundElements=[], updated=1,
                 link=None, locked=False)
        e.update(kw); self.els.append(e); return e
    def text(self, s, x, y, size=18, color="#1e1e1e", container=None, align="center", w=None, h=None):
        lines = s.split("\n"); cw = size * 0.6
        W = w or max(len(l) for l in lines) * cw; H = h or len(lines) * size * 1.25
        e = self._base("text", x, y, W, H, strokeColor=color, text=s, originalText=s, fontSize=size, fontFamily=5,
                       textAlign=align, verticalAlign="middle" if container else "top", containerId=container,
                       lineHeight=1.25, autoResize=True, baseline=int(size * 0.9))
        return e
    def box(self, key, label, x, y, w=240, h=84, color=BLUE, shape="rectangle", dashed=False, size=17):
        sh = self._base(shape, x, y, w, h, backgroundColor=color, strokeStyle="dashed" if dashed else "solid",
                        roundness={"type": 3} if shape == "rectangle" else None)
        lines = label.split("\n"); tw = max(len(l) for l in lines) * size * 0.6; th = len(lines) * size * 1.25
        t = self.text(label, x + (w - tw) / 2, y + (h - th) / 2, size, container=sh["id"], w=tw, h=th)
        sh["boundElements"].append({"id": t["id"], "type": "text"})
        self.ids[key] = sh; return sh
    def note(self, label, x, y, w, h, color=YELLOW, size=15, dashed=True):
        sh = self._base("rectangle", x, y, w, h, backgroundColor=color, strokeStyle="dashed" if dashed else "solid", roundness={"type": 3})
        lines = label.split("\n"); tw = max(len(l) for l in lines) * size * 0.6; th = len(lines) * size * 1.25
        t = self.text(label, x + (w - tw) / 2, y + (h - th) / 2, size, container=sh["id"], w=tw, h=th)
        sh["boundElements"].append({"id": t["id"], "type": "text"}); return sh
    def free(self, s, x, y, size=18, color="#1e1e1e", w=None): return self.text(s, x, y, size, color, w=w, align="left")
    def _edge(self, s, tx, ty):  # point on shape boundary toward (tx,ty)
        cx, cy = s["x"] + s["width"] / 2, s["y"] + s["height"] / 2; dx, dy = tx - cx, ty - cy
        if dx == 0 and dy == 0: return cx, cy
        if s["type"] == "ellipse":
            a, b = s["width"] / 2, s["height"] / 2; k = 1 / math.sqrt((dx / a) ** 2 + (dy / b) ** 2); return cx + dx * k, cy + dy * k
        k = min((s["width"] / 2) / abs(dx) if dx else 1e9, (s["height"] / 2) / abs(dy) if dy else 1e9); return cx + dx * k, cy + dy * k
    def arrow(self, a, b, label=None, dashed=False, color="#1e1e1e", lx=0, ly=0, both=False, size=14):
        sa, sb = self.ids[a], self.ids[b]
        ca = (sa["x"] + sa["width"] / 2, sa["y"] + sa["height"] / 2); cb = (sb["x"] + sb["width"] / 2, sb["y"] + sb["height"] / 2)
        x1, y1 = self._edge(sa, *cb); x2, y2 = self._edge(sb, *ca)
        gap = 5; L = math.hypot(x2 - x1, y2 - y1) or 1; ux, uy = (x2 - x1) / L, (y2 - y1) / L
        x1, y1, x2, y2 = x1 + ux * gap, y1 + uy * gap, x2 - ux * gap, y2 - uy * gap
        e = self._base("arrow", x1, y1, x2 - x1, y2 - y1, strokeColor=color, strokeStyle="dashed" if dashed else "solid",
                       roundness={"type": 2}, points=[[0, 0], [x2 - x1, y2 - y1]], lastCommittedPoint=None,
                       startBinding={"elementId": sa["id"], "focus": 0, "gap": gap}, endBinding={"elementId": sb["id"], "focus": 0, "gap": gap},
                       startArrowhead="arrow" if both else None, endArrowhead="arrow", elbowed=False)
        sa["boundElements"].append({"id": e["id"], "type": "arrow"}); sb["boundElements"].append({"id": e["id"], "type": "arrow"})
        if label:
            lines = label.split("\n"); tw = max(len(l) for l in lines) * size * 0.6; th = len(lines) * size * 1.25
            mx, my = (x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly
            bg = self._base("rectangle", mx - tw / 2 - 4, my - th / 2 - 2, tw + 8, th + 4, backgroundColor="#ffffff", strokeColor="transparent", opacity=85)
            self.text(label, mx - tw / 2, my - th / 2, size, "#343a40", w=tw, h=th)
    def line(self, x1, y1, x2, y2, dashed=True, color="#868e96"):
        self._base("line", x1, y1, x2 - x1, y2 - y1, strokeColor=color, strokeStyle="dashed" if dashed else "solid", strokeWidth=1,
                   points=[[0, 0], [x2 - x1, y2 - y1]], lastCommittedPoint=None, startBinding=None, endBinding=None, startArrowhead=None, endArrowhead=None)
    def msg(self, x1, x2, y, label, dashed=False, color="#1e1e1e", size=14):  # sequence message between lifeline x positions
        e = self._base("arrow", x1, y, x2 - x1, 0, strokeColor=color, strokeStyle="dashed" if dashed else "solid", roundness={"type": 2},
                       points=[[0, 0], [x2 - x1, 0]], lastCommittedPoint=None, startBinding=None, endBinding=None, startArrowhead=None, endArrowhead="arrow", elbowed=False)
        tw = len(label) * size * 0.6; self.text(label, (x1 + x2) / 2 - tw / 2, y - size * 1.25 - 4, size, "#343a40", w=tw, h=size * 1.25)
    def save(self, path):
        t = self.text(self.title, 40, 24, 28, "#1e1e1e")
        doc = {"type": "excalidraw", "version": 2, "source": "learn-resource", "elements": self.els,
               "appState": {"viewBackgroundColor": "#ffffff", "gridSize": 20}, "files": {}}
        pathlib.Path(path).write_text(json.dumps(doc, indent=1)); print(path, len(self.els), "elements")


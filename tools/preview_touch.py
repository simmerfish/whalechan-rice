#!/usr/bin/env python3
"""把触屏虚拟键和 HUD 的占位框画在一起，用来检查手机上会不会互相挡住。
输出 preview/check_touch.png，并打印一次重叠自检结果。用法： python3 tools/preview_touch.py"""
import sys, os, math, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from keyout import read_png_rgba, write_png
from preview_hitbox import (ocean, blend, draw_sprite, ellipse, rect,
                            ART_H, GROUND, SPR_CX)

SRC = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
W, H = 960, 540

# 从 index.html 里读 BTN_*（x 可能是 "W - 128" 这种表达式，所以 eval 一下）
BTN = {}
PAT = 'BTN_([A-Z]+)[ ]*=[ ]*[{][ ]*x:[ ]*([^,]+),[ ]*y:[ ]*([0-9.]+),[ ]*r:[ ]*([0-9.]+)'
for m in re.finditer(PAT, SRC):
    name, xs, ys, rs = m.group(1), m.group(2).strip(), m.group(3), m.group(4)
    BTN[name] = (eval(xs, {'W': W}), float(ys), float(rs))
print('虚拟键:', ', '.join('%s=(%g,%g,r%g)' % (k, v[0], v[1], v[2]) for k, v in sorted(BTN.items())))

art = {'closed': read_png_rgba(os.path.join(ROOT, 'art', 'whalechan-closed.png'))}
cv = ocean()
draw_sprite(cv, art['closed'], 480, 556)

CYAN, AMBER, GREY = (120, 220, 255), (255, 214, 120), (150, 200, 230)

# --- HUD 占位框（和游戏里的真实坐标一致）---
for x0, y0, x1, y1, col in [
    (0, 0, W - 1, 10, CYAN),      # 开饭进度条
    (752, 20, 920, 74, AMBER),    # 倒计时面板
    (40, 500, 920, 520, CYAN),    # 饱食度条
    (40, 8, 230, 60, GREY),       # 分数区
    (820, 134, 940, 186, AMBER),  # buff 盒（最多 5 个，这里画第 1 个）
]:
    rect(cv, x0, y0, x1, y1, col)

# --- 触屏虚拟键 ---
for name, col in [('L', CYAN), ('R', CYAN), ('MOUTH', CYAN), ('PAUSE', AMBER)]:
    x, y, r = BTN[name]
    ellipse(cv, x, y, r, r, col)
    ellipse(cv, x, y, r - 2, r - 2, col)
rect(cv, W - 276, H - 92, W - 40, H - 44, GREY)   # 标题页「全屏横屏」按钮
rect(cv, 380, 458, 580, 500, GREY)                # 开局 8 秒的手势提示（居中）

write_png(os.path.join(ROOT, 'preview', 'check_touch.png'), W, H, bytes(cv))

# --- 重叠自检：按键圆 vs HUD 矩形 ---
hud = {'进度条': (0, 0, W, 10), '倒计时': (752, 20, 920, 74), '饱食度条': (40, 500, 920, 520),
       '分数区': (40, 8, 230, 60), 'buff盒': (820, 134, 940, 186), '提示行': (380, 458, 580, 500)}
bad = []
for name, (x, y, r) in BTN.items():
    for hn, (x0, y0, x1, y1) in hud.items():
        cx, cy = min(max(x, x0), x1), min(max(y, y0), y1)
        if (x - cx) ** 2 + (y - cy) ** 2 < r * r:
            bad.append('%s x %s' % (name, hn))
print('按键与 HUD 重叠:', ', '.join(bad) if bad else '无')

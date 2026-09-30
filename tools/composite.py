#!/usr/bin/env python3
"""把抠好的透明立绘合成到品红底上，用来检查是否残留奶白晕边。
输出到 preview/halo-check-<name>.png。用法： python3 tools/composite.py"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from keyout import read_png_rgba, write_png

BG = (232, 96, 120)  # 品红：任何奶白晕边都会立刻现形

os.makedirs(os.path.join(ROOT, 'preview'), exist_ok=True)
for n in ['closed', 'open', 'happy']:
    w, h, px = read_png_rgba(os.path.join(ROOT, 'art', 'whalechan-%s.png' % n))
    # 缩到一半方便看
    ow, oh = w // 2, h // 2
    out = bytearray(ow * oh * 4)
    for y in range(oh):
        for x in range(ow):
            r = g = b = a = 0
            for dy in (0, 1):
                for dx in (0, 1):
                    j = ((y * 2 + dy) * w + (x * 2 + dx)) * 4
                    al = px[j + 3]
                    r += px[j] * al; g += px[j + 1] * al; b += px[j + 2] * al; a += al
            j = (y * ow + x) * 4
            if a == 0:
                out[j:j + 4] = bytes((BG[0], BG[1], BG[2], 255))
            else:
                out[j] = r // a; out[j + 1] = g // a; out[j + 2] = b // a; out[j + 3] = a // 4
    # 压到品红底上
    flat = bytearray(ow * oh * 4)
    for i in range(ow * oh):
        al = out[i * 4 + 3]
        for k in range(3):
            flat[i * 4 + k] = (out[i * 4 + k] * al + BG[k] * (255 - al)) // 255
        flat[i * 4 + 3] = 255
    dst = os.path.join(ROOT, 'preview', 'halo-check-%s.png' % n)
    write_png(dst, ow, oh, flat)
    print(n, '->', os.path.relpath(dst, ROOT), ow, oh)

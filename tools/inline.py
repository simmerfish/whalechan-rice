#!/usr/bin/env python3
"""把 art/ 里那三张立绘压缩后内联进 index.html，产出一个「自包含单文件版」。

生成的 whalechan-standalone.html 不需要 art/ 目录、不需要联网、不需要起服务器，
双击就能玩，也可以直接用微信 / QQ 发给别人（对方收到一个 html 文件就能玩）。

为什么要压一下：游戏里鲸鱼娘画 300 逻辑像素高，画布最多按 2 倍像素密度渲染，
也就是最多用到 600 物理像素。原始立绘有 830~850 高，内联进去白白多背 1.8M。
缩到 660 高后清晰度几乎没差别，三张合计从 1.74M 降到 0.94M。

用法： python3 tools/inline.py
"""
import os, sys, base64
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from keyout import read_png_rgba, write_png

NAMES = ['closed', 'open', 'happy']
TARGET_H = 660
SRC = os.path.join(ROOT, 'index.html')
DST = os.path.join(ROOT, 'whalechan-standalone.html')
TMP = os.path.join(ROOT, 'preview', '_inline-tmp.png')
MARKER = 'var ART_INLINE = null;'


def resize(w, h, px, nh):
    """按面积平均的降采样（alpha 加权，避免透明边缘发黑）。"""
    nw = max(1, round(w * nh / h))
    out = bytearray(nw * nh * 4)
    for y in range(nh):
        y0 = y * h // nh
        y1 = max(y0 + 1, (y + 1) * h // nh)
        for x in range(nw):
            x0 = x * w // nw
            x1 = max(x0 + 1, (x + 1) * w // nw)
            r = g = b = a = 0
            n = 0
            for yy in range(y0, y1):
                base = yy * w
                for xx in range(x0, x1):
                    j = (base + xx) * 4
                    al = px[j + 3]
                    r += px[j] * al
                    g += px[j + 1] * al
                    b += px[j + 2] * al
                    a += al
                    n += 1
            j = (y * nw + x) * 4
            if a == 0:
                out[j + 3] = 0
            else:
                out[j] = r // a
                out[j + 1] = g // a
                out[j + 2] = b // a
                out[j + 3] = a // n
    return nw, nh, out


def main():
    src = open(SRC, encoding='utf-8').read()
    if MARKER not in src:
        print('!! 在 index.html 里找不到 %r，是不是那个 var 被改名了？' % MARKER)
        return 1

    os.makedirs(os.path.dirname(TMP), exist_ok=True)
    lines = ['/* ---- 下面这段是 tools/inline.py 自动塞进来的：三张立绘的 base64 ---- */',
             'var ART_INLINE = {']
    total = 0
    for n in NAMES:
        w, h, px = read_png_rgba(os.path.join(ROOT, 'art', 'whalechan-%s.png' % n))
        nw, nh, out = resize(w, h, px, TARGET_H)
        write_png(TMP, nw, nh, out)
        raw = open(TMP, 'rb').read()
        total += len(raw)
        b64 = base64.b64encode(raw).decode('ascii')
        lines.append("  %s: 'data:image/png;base64,%s'," % (n, b64))
        print('  %-7s %dx%d -> %dx%d   %6.1f KB' % (n, w, h, nw, nh, len(raw) / 1024))
    lines.append('};')
    os.remove(TMP)

    data_line = '\n'.join(lines)
    if not data_line.endswith('};'):
        pass
    out_html = src.replace(MARKER, data_line)
    banner = ('<!--\n'
              '  鲸鱼娘吃大白饭 —— 自包含单文件版（whalechan-standalone.html）\n'
              '  这个文件是 tools/inline.py 从 index.html 自动生成的，请不要直接改它。\n'
              '  要改游戏请改 index.html，然后重新跑一次 python3 tools/inline.py。\n'
              '  三张立绘已经用 base64 内联在文件里，所以：不需要 art/ 目录、不需要联网。\n'
              '-->\n')
    # 说明放在 <!DOCTYPE html> 之后，确保 doctype 仍然是文档的第一样东西
    if out_html.startswith('<!DOCTYPE'):
        nl = out_html.find('\n')
        if nl < 0:
            nl = len(out_html)
        out_html = out_html[:nl + 1] + banner + out_html[nl + 1:]
    else:
        print('!! index.html 没有以 <!DOCTYPE 开头，直接把说明插在最前面')
        out_html = banner + out_html
    open(DST, 'w', encoding='utf-8').write(out_html)
    print()
    print('立绘合计 %.1f KB -> base64 后约 %.1f KB' % (total / 1024, total * 4 / 3 / 1024))
    print('已生成 %s  (%.2f MB)' % (os.path.basename(DST), os.path.getsize(DST) / 1048576))
    return 0


if __name__ == '__main__':
    sys.exit(main())

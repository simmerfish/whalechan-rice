# 把判定框（嘴部椭圆 / 身体矩形）叠在立绘上渲染成 PNG，用来目视校准常量。
# 也可以被 preview_touch.py import 复用里面的绘制小工具（所以主程序放在 __main__ 里）。
import sys, os, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # whale-game/ 仓库根
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from keyout import read_png_rgba, write_png

SRC = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
CONSTS = {}
for line in SRC.split('\n'):
    s = line.strip()
    if not s.startswith('var '):
        continue
    s = s.split('//')[0]
    for part in s[4:].split(','):
        if '=' not in part:
            continue
        k, _, v = part.partition('=')
        k = k.strip(); v = v.strip().rstrip(';').strip()
        try:
            CONSTS[k] = float(v)
        except ValueError:
            pass

ART_H = CONSTS['ART_H']; GROUND = CONSTS['GROUND']
SPR_CX = CONSTS['SPR_CX']; SPR_MY = CONSTS['SPR_MY']
MOUTH_RX = CONSTS['MOUTH_RX']; MOUTH_RY = CONSTS['MOUTH_RY']
BODY_HW = CONSTS['BODY_HW']; BODY_TOP_F = CONSTS['BODY_TOP_F']

W, H = 960, 540
art = {n: read_png_rgba(os.path.join(ROOT, 'art', 'whalechan-%s.png' % n)) for n in ['closed', 'open', 'happy']}


def ocean():
    c = bytearray(W * H * 4)
    for y in range(H):
        t = y / (H - 1)
        r = int(11 + (4 - 11) * t); g = int(52 + (26 - 52) * t); b = int(88 + (58 - 88) * t)
        for x in range(W):
            i = (y * W + x) * 4
            c[i] = r; c[i + 1] = g; c[i + 2] = b; c[i + 3] = 255
    return c


def blend(cv, x, y, r, g, b, a):
    if 0 <= x < W and 0 <= y < H and a > 0:
        i = (y * W + x) * 4; sa = a / 255.0; ia = 1 - sa
        cv[i] = int(r * sa + cv[i] * ia)
        cv[i + 1] = int(g * sa + cv[i + 1] * ia)
        cv[i + 2] = int(b * sa + cv[i + 2] * ia)


def draw_sprite(cv, src, cx, ground):
    sw, sh, data = src
    k = ART_H / sh; dw, dh = sw * k, sh * k
    left = cx - dw * SPR_CX; top = ground - dh
    x0, y0 = int(left), int(top)
    for dy in range(int(dh)):
        sy = int(dy / k)
        if sy >= sh: continue
        for dx in range(int(dw)):
            sx = int(dx / k)
            if sx >= sw: continue
            i = (sy * sw + sx) * 4; a = data[i + 3]
            if a == 0: continue
            blend(cv, x0 + dx, y0 + dy, data[i], data[i + 1], data[i + 2], a)


def ellipse(cv, cx, cy, rx, ry, col):
    for t in range(3600):
        a = t * math.pi / 1800
        x = int(cx + rx * math.cos(a)); y = int(cy + ry * math.sin(a))
        for ox in (0, 1):
            for oy in (0, 1):
                blend(cv, x + ox, y + oy, col[0], col[1], col[2], 255)


def rect(cv, x0, y0, x1, y1, col):
    for x in range(int(x0), int(x1) + 1):
        for y in (int(y0), int(y0) + 1, int(y1), int(y1) + 1):
            blend(cv, x, y, col[0], col[1], col[2], 255)
    for y in range(int(y0), int(y1) + 1):
        for x in (int(x0), int(x0) + 1, int(x1), int(x1) + 1):
            blend(cv, x, y, col[0], col[1], col[2], 255)


def cross(cv, cx, cy, col):
    for d in range(-10, 11):
        blend(cv, int(cx) + d, int(cy), col[0], col[1], col[2], 255)
        blend(cv, int(cx), int(cy) + d, col[0], col[1], col[2], 255)


def main():
    print('读到: ART_H=%g GROUND=%g SPR_CX=%g SPR_MY=%g MOUTH=%gx%g BODY_HW=%g TOP_F=%g'
          % (ART_H, GROUND, SPR_CX, SPR_MY, MOUTH_RX, MOUTH_RY, BODY_HW, BODY_TOP_F))

    cv = ocean()
    Px = 480
    draw_sprite(cv, art['closed'], Px, GROUND)
    mx, my = Px, GROUND - ART_H + ART_H * SPR_MY
    ellipse(cv, mx, my, MOUTH_RX, MOUTH_RY, (255, 80, 80))
    cross(cv, mx, my, (255, 255, 0))
    rect(cv, Px - BODY_HW, GROUND - ART_H * BODY_TOP_F, Px + BODY_HW, GROUND + 8, (80, 240, 255))
    print('立绘顶 y=%.0f  嘴心 y=%.0f  椭圆 y %.0f..%.0f  身体框 y %.0f..%.0f'
          % (GROUND - ART_H, my, my - MOUTH_RY, my + MOUTH_RY, GROUND - ART_H * BODY_TOP_F, GROUND + 8))
    write_png(os.path.join(ROOT, 'preview', 'check_layout.png'), W, H, bytes(cv))

    cv = ocean()
    for idx, name in enumerate(['closed', 'open', 'happy']):
        draw_sprite(cv, art[name], 180 + idx * 300, 470)
    write_png(os.path.join(ROOT, 'preview', 'check_states.png'), W, H, bytes(cv))
    print('绘制宽度: closed %.1f  open %.1f  happy %.1f' % tuple(art[n][0] / art[n][1] * ART_H for n in ['closed', 'open', 'happy']))


if __name__ == '__main__':
    main()
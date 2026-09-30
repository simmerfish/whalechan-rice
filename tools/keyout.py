#!/usr/bin/env python3
"""Strip the flat cream backdrop from generated whale-chan art -> transparent PNG.
Pure stdlib (zlib). Usage: python3 keyout.py IN.png OUT.png [tol]"""
import sys, zlib, struct
from collections import Counter

def read_png_rgba(path):
    data = open(path, 'rb').read()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise SystemExit('not a png: ' + path)
    pos, idat = 8, []
    w = h = bd = ct = 0
    while pos < len(data):
        ln = struct.unpack('>I', data[pos:pos+4])[0]
        typ = data[pos+4:pos+8]
        chunk = data[pos+8:pos+8+ln]
        pos += 12 + ln
        if typ == b'IHDR':
            w, h, bd, ct, _c, _f, inter = struct.unpack('>IIBBBBB', chunk)
            if inter != 0: raise SystemExit('interlaced unsupported')
            if bd != 8: raise SystemExit('need 8-bit, got %d' % bd)
        elif typ == b'IDAT': idat.append(chunk)
        elif typ == b'IEND': break
    if ct not in (2, 6): raise SystemExit('need color type 2/6, got %d' % ct)
    nch = 3 if ct == 2 else 4
    stride = w * nch
    raw = zlib.decompress(b''.join(idat))
    out = bytearray(stride * h)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        ft = raw[p]; p += 1
        line = bytearray(raw[p:p+stride]); p += stride
        if ft == 1:
            for i in range(nch, stride): line[i] = (line[i] + line[i-nch]) & 255
        elif ft == 2:
            for i in range(stride): line[i] = (line[i] + prev[i]) & 255
        elif ft == 3:
            for i in range(nch): line[i] = (line[i] + (prev[i] >> 1)) & 255
            for i in range(nch, stride): line[i] = (line[i] + ((line[i-nch] + prev[i]) >> 1)) & 255
        elif ft == 4:
            for i in range(nch): line[i] = (line[i] + prev[i]) & 255
            for i in range(nch, stride):
                a = line[i-nch]; b = prev[i]; c = prev[i-nch]
                pa = b-c if b > c else c-b
                pb = a-c if a > c else c-a
                pc = a+b-2*c
                if pc < 0: pc = -pc
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        out[y*stride:(y+1)*stride] = line
        prev = line
    if ct == 6: return w, h, out
    n = w * h
    rgba = bytearray(n*4)
    j = 0
    for i in range(0, n*3, 3):
        rgba[j] = out[i]; rgba[j+1] = out[i+1]; rgba[j+2] = out[i+2]; rgba[j+3] = 255
        j += 4
    return w, h, rgba

def write_png(path, w, h, rgba):
    stride = w*4
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgba[y*stride:(y+1)*stride]
    def chunk(typ, d):
        return struct.pack('>I', len(d)) + typ + d + struct.pack('>I', zlib.crc32(typ+d) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += chunk(b'IEND', b'')
    open(path, 'wb').write(png)

def main():
    src, dst = sys.argv[1], sys.argv[2]
    tol = int(sys.argv[3]) if len(sys.argv) > 3 else 34
    w, h, rgba = read_png_rgba(src)
    cnt = Counter()
    for x in range(w):
        for y in (0, h-1):
            j = (y*w+x)*4
            cnt[(rgba[j]//6*6, rgba[j+1]//6*6, rgba[j+2]//6*6)] += 1
    for y in range(h):
        for x in (0, w-1):
            j = (y*w+x)*4
            cnt[(rgba[j]//6*6, rgba[j+1]//6*6, rgba[j+2]//6*6)] += 1
    (br, bgc, bb), _n = cnt.most_common(1)[0]
    print('bg = #%02X%02X%02X  tol=%d  %dx%d' % (br, bgc, bb, tol, w, h))

    BG = (br, bgc, bb)
    def ok(i):
        j = i*4
        if rgba[j]   - br  >  tol or br  - rgba[j]   > tol: return False
        if rgba[j+1] - bgc >  tol or bgc - rgba[j+1] > tol: return False
        if rgba[j+2] - bb  >  tol or bb  - rgba[j+2] > tol: return False
        return True

    mask = bytearray(w*h)
    stack = []
    for x in range(w):
        for y in (0, h-1):
            i = y*w+x
            if not mask[i] and ok(i): stack.append((x, y))
    for y in range(h):
        for x in (0, w-1):
            i = y*w+x
            if not mask[i] and ok(i): stack.append((x, y))
    while stack:
        x, y = stack.pop()
        row = y*w
        if mask[row+x] or not ok(row+x): continue
        xl = x
        while xl > 0 and not mask[row+xl-1] and ok(row+xl-1): xl -= 1
        xr = x
        while xr < w-1 and not mask[row+xr+1] and ok(row+xr+1): xr += 1
        for i in range(row+xl, row+xr+1): mask[i] = 1
        for ny in (y-1, y+1):
            if 0 <= ny < h:
                nrow = ny*w
                i = xl
                while i <= xr:
                    if not mask[nrow+i] and ok(nrow+i):
                        stack.append((i, ny))
                        while i <= xr and not mask[nrow+i] and ok(nrow+i): i += 1
                    i += 1
    print('background pixels: %d / %d (%.1f%%)' % (sum(mask), w*h, 100.0*sum(mask)/(w*h)))

    for y in range(h):
        row = y*w
        for x in range(w):
            i = row+x
            j = i*4
            if mask[i]:
                rgba[j+3] = 0
                continue
            if x == 0 or y == 0 or x == w-1 or y == h-1:
                edge = True
            else:
                edge = bool(mask[i-1] or mask[i+1] or mask[i-w] or mask[i+w])
            if not edge:
                rgba[j+3] = 255
                continue
            d = rgba[j]-br
            if d < 0: d = -d
            e = rgba[j+1]-bgc
            if e < 0: e = -e
            f = rgba[j+2]-bb
            if f < 0: f = -f
            if e > d: d = e
            if f > d: d = f
            if d >= 96:
                rgba[j+3] = 255
                continue
            a = (d - 6) / 90.0
            if a <= 0.05:
                rgba[j+3] = 0
                continue
            if a > 1.0: a = 1.0
            rgba[j+3] = int(a*255)
            for k in range(3):
                v = (rgba[j+k] - (1.0-a)*BG[k]) / a
                rgba[j+k] = 0 if v < 0 else (255 if v > 255 else int(v))

    x0, y0, x1, y1 = w, h, -1, -1
    for y in range(h):
        row = y*w
        for x in range(w):
            if rgba[(row+x)*4+3] > 4:
                if x < x0: x0 = x
                if x > x1: x1 = x
                if y < y0: y0 = y
                if y > y1: y1 = y
    print('alpha bbox: %d,%d - %d,%d' % (x0, y0, x1, y1))
    cw, ch = x1-x0+1, y1-y0+1
    crop = bytearray(cw*ch*4)
    for y in range(ch):
        s = ((y+y0)*w + x0)*4
        crop[y*cw*4:(y+1)*cw*4] = rgba[s:s+cw*4]
    write_png(dst, cw, ch, crop)
    print('wrote %s  %dx%d' % (dst, cw, ch))

if __name__ == '__main__':
    main()

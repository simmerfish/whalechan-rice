#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 README 配图：用 headless Chrome 把游戏各个界面截成 PNG。

用法：
    python3 tools/shots.py               # 全部重截
    python3 tools/shots.py play over-win # 只重截指定的几张

产物写到 whale-game/screenshots/。
原理：把一段「截图驱动」插进 index.html 的 IIFE 内部（这样能直接操作
state / G / P 等局部变量），存成 /tmp 下的临时副本再喂给 Chrome；仓库里的
index.html 一个字节都不动。

注意：不要指望 --virtual-time-budget 来推进游戏。实测虚拟时间跑掉 34 秒，
游戏里的 G.time 才走了 0.5 秒（rAF 在无头里不是按虚拟时钟喂的）。所以驱动
改成**同步跑帧**：自己 for 循环调 update(1/60) 把局面推到位，再把 update
换成空函数定格，剩下的交给页面自己的 rAF 循环去渲染。
"""
import os
import shutil
import subprocess
import sys
import time

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC    = os.path.join(ROOT, 'index.html')
OUTDIR = os.path.join(ROOT, 'screenshots')
TMPDIR = '/tmp/whalechan-shots'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
BUDGET = 12000          # 虚拟时间预算：只是为了让页面活够久、立绘来得及加载

DRIVER = """
/* ==== 截图驱动：只存在于临时副本里，不会进仓库 ==== */
(function(){
  var MODE = '%(mode)s';
  // 最高分页/难度页塞一组演示用成绩，不然三行全是 0 看着像坏了
  function demoBest(){ save.best = { easy: 1180, normal: 2340, hard: 960 }; }

  if (MODE === 'title')      { /* 主菜单就是默认状态 */ }
  else if (MODE === 'diff')  { demoBest(); state = 'diff';  diffReturnTo = 'title'; menuIdx = 1; }
  else if (MODE === 'codex') { state = 'codex'; codexPage = 0; }
  else if (MODE === 'best')  { demoBest(); state = 'best'; }
  else if (MODE === 'pause') { newGame('normal'); state = 'pause'; menuIdx = 0; }
  else {
    newGame('normal');
    state = 'play';
    if (MODE === 'play-touch') touchUI = true;

    var DT = 1 / 60;
    var isOver = MODE.indexOf('over') === 0;
    var isTouch = MODE === 'play-touch';

    function autopilot(){
      // 一直张嘴；朝最近的饭挪过去，垃圾躲开
      keys['Space'] = true;
      var tgt = null, bs = -1e9;
      for (var i = 0; i < G.items.length; i++){
        var it = G.items[i];
        if (it.y > 430) continue;
        var s = -Math.abs(it.x - P.x);
        if (it.def.kind === 'junk') s -= 900;
        if (it.def.kind === 'buff') s += 260;
        if (it.key === 'golden')    s += 120;
        if (s > bs) { bs = s; tgt = it; }
      }
      keys['ArrowLeft']  = !!(tgt && tgt.x < P.x - 10);
      keys['ArrowRight'] = !!(tgt && tgt.x > P.x + 10);
    }
    function step(){ autopilot(); update(DT); }
    function goodFrame(){
      var hasBuff = (G.shield > 0 || G.dbl > 0 || G.slow > 0 ||
                     G.magnet > 0 || G.gold > 0);
      return G.items.length >= 3 && G.combo >= 8 && hasBuff;
    }

    function run(){
      var limit = isOver ? 11 : (isTouch ? 9.5 : 26);   // 触屏 9.5s：等新手提示淡出
      var i, n = Math.round(limit * 60);
      for (i = 0; i < n; i++){
        step();
        if (G.time >= limit) break;
        if (!isOver && !isTouch && G.time >= 8 && goodFrame()) break;
      }
      if (isOver){
        if (MODE === 'over-win') G.time = G.goal; else G.fullness = 0;
        for (i = 0; i < 50; i++) step();     // 结算面板淡入
      }
      update = function(){};                 // 定格：之后只渲染不推进
      keys = Object.create(null);
    }

    // 等立绘加载出来再推局面，免得截到程序化兜底鲸鱼
    var tries = 0;
    var iv = setInterval(function(){
      tries++;
      if (!artOK && tries < 400) return;
      clearInterval(iv);
      run();
    }, 20);
  }
})();
"""

# 名字, 模式, 宽, 高
SHOTS = [
    ('title',      'title',      960, 540),
    ('diff',       'diff',       960, 540),
    ('codex',      'codex',      960, 540),
    ('best',       'best',       960, 540),
    ('play',       'play',       960, 540),
    ('play-touch', 'play-touch', 960, 540),
    ('over-win',   'over-win',   960, 540),
    ('over-lose',  'over-lose',  960, 540),
]

CHAR_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  html,body{margin:0;background:#f5eadd;}
  .row{display:flex;gap:34px;padding:22px 34px 6px;align-items:flex-end;justify-content:center;}
  figure{margin:0;text-align:center;}
  img{height:560px;display:block;}
  figcaption{margin-top:8px;font:600 21px "PingFang SC","Helvetica Neue",sans-serif;
             color:#1b3a63;letter-spacing:.08em;}
</style></head><body><div class="row">
  <figure><img src="ARTDIR/whalechan-closed.png"><figcaption>闭嘴 · 平时</figcaption></figure>
  <figure><img src="ARTDIR/whalechan-open.png"><figcaption>张嘴 · 接饭</figcaption></figure>
  <figure><img src="ARTDIR/whalechan-happy.png"><figcaption>开心 · 结算</figcaption></figure>
</div></body></html>
"""


def chrome_shot(html_path, png_path, w, h, budget=BUDGET, dsf='1', timeout=150):
    """跑一次 headless Chrome 截图。Chrome 不会自己退出，靠轮询文件出现 + kill。"""
    prof = png_path[:-4] + '-prof'
    shutil.rmtree(prof, ignore_errors=True)
    if os.path.exists(png_path):
        os.remove(png_path)
    cmd = [
        CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
        '--no-first-run', '--no-default-browser-check', '--disable-extensions',
        '--hide-scrollbars', '--mute-audio',
        '--window-size=%d,%d' % (w, h),
        '--force-device-scale-factor=%s' % dsf,
        '--screenshot=' + png_path,
        '--virtual-time-budget=%d' % budget,
        '--user-data-dir=' + prof,
        'file://' + html_path,
    ]
    with open(png_path[:-4] + '.log', 'w') as log:
        p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
    deadline = time.time() + timeout
    ok = False
    while time.time() < deadline:
        if os.path.exists(png_path) and os.path.getsize(png_path) > 2000:
            time.sleep(0.5)
            ok = True
            break
        if p.poll() is not None:
            ok = os.path.exists(png_path)
            break
        time.sleep(0.4)
    try:
        p.kill()
    except Exception:
        pass
    try:
        p.wait(timeout=10)
    except Exception:
        pass
    shutil.rmtree(prof, ignore_errors=True)
    return ok


def main():
    want = sys.argv[1:]
    for d in (TMPDIR, OUTDIR):
        if not os.path.isdir(d):
            os.makedirs(d)

    src = open(SRC, encoding='utf-8').read()
    cut = src.rfind('})();')          # 脚本最外层 IIFE 的收尾
    if cut < 0:
        print('!! 在 index.html 里找不到 IIFE 收尾，脚本结构变了？')
        return 1

    done = []
    for name, mode, w, h in SHOTS:
        if want and name not in want:
            continue
        hp = os.path.join(TMPDIR, name + '.html')
        html = src[:cut] + (DRIVER % {'mode': mode}) + src[cut:]
        # 临时副本在 /tmp 里，相对路径找不到 art/，用 <base> 指回 whale-game/
        html = html.replace('<meta charset="utf-8">',
                            '<meta charset="utf-8"><base href="file://' + ROOT + '/">', 1)
        open(hp, 'w', encoding='utf-8').write(html)
        pp = os.path.join(TMPDIR, name + '.png')
        t0 = time.time()
        if not chrome_shot(hp, pp, w, h):
            print('  x  %-11s 失败（看 %s.log）' % (name, pp[:-4]))
            continue
        shutil.copyfile(pp, os.path.join(OUTDIR, name + '.png'))
        print('  ok %-11s %4dx%-4d %7.1f KB  %4.1fs'
              % (name, w, h, os.path.getsize(pp) / 1024, time.time() - t0))
        done.append(name)

    if not want or 'characters' in want:
        hp = os.path.join(TMPDIR, 'characters.html')
        open(hp, 'w', encoding='utf-8').write(
            CHAR_HTML.replace('ARTDIR', 'file://' + os.path.join(ROOT, 'art')))
        pp = os.path.join(TMPDIR, 'characters.png')
        t0 = time.time()
        if chrome_shot(hp, pp, 1180, 640, 5000):
            shutil.copyfile(pp, os.path.join(OUTDIR, 'characters.png'))
            print('  ok %-11s %4dx%-4d %7.1f KB  %4.1fs'
                  % ('characters', 1180, 640, os.path.getsize(pp) / 1024, time.time() - t0))
            done.append('characters')
        else:
            print('  x  characters 失败')

    print()
    print('共 %d 张，输出到 %s' % (len(done), OUTDIR))
    return 0


if __name__ == '__main__':
    sys.exit(main())

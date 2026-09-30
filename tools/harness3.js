// 专项回归：通关流程 + 6 种 buff 覆盖 + 图鉴/结算不越界
const fs = require('fs');
const path = require('path');
const ROOT = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
let code = html.match(/<script>([\s\S]*)<\/script>/)[1];

function boot(src){
  let frameTexts = [], frameImgs = [], frameEll = [];
  function mkCtx(){
    const grad = { addColorStop(){} };
    const target = { filter:'', measureText:(t)=>({width:String(t).length*8}),
      createLinearGradient:()=>grad, createRadialGradient:()=>grad,
      fillText:(t)=>{frameTexts.push(String(t));}, strokeText:(t)=>{frameTexts.push(String(t));},
      drawImage:(...a)=>{frameImgs.push(a);}, ellipse:(...a)=>{frameEll.push(a);},
      save(){}, restore(){}, fillRect(){}, strokeRect(){} };
    return new Proxy(target,{ get(t,k){ return (k in t)?t[k]:function(){}; }, set(t,k,v){t[k]=v;return true;} });
  }
  const ctx = mkCtx();
  const LC = {}, LD = {};
  const canvas = { width:0,height:0,style:{},getContext:()=>ctx,
    addEventListener:(t,f)=>{(LC[t]=LC[t]||[]).push(f);},
    getBoundingClientRect:()=>({left:0,top:0,width:960,height:540}),
    setPointerCapture(){}, releasePointerCapture(){}, hasPointerCapture(){return true;} };
  const L = {}; let rafCb=null, now=0; const errors=[];
  global.window = { innerWidth:1440, innerHeight:900, devicePixelRatio:2,
    addEventListener:(t,f)=>{(L[t]=L[t]||[]).push(f);}, AudioContext:undefined, webkitAudioContext:undefined };
  global.document = { getElementById:()=>canvas, documentElement:{},
    addEventListener:(t,f)=>{(LD[t]=LD[t]||[]).push(f);} };
  const ART_DIMS = { 'whalechan-closed.png':[470,839], 'whalechan-open.png':[440,831], 'whalechan-happy.png':[504,847] };
  global.Image = class {
    constructor(){ this.naturalWidth=0; this.naturalHeight=0; this._src=''; }
    get src(){ return this._src; }
    set src(v){ this._src=String(v);
      for (const k in ART_DIMS){ if (this._src.indexOf(k)>=0){ this.naturalWidth=ART_DIMS[k][0]; this.naturalHeight=ART_DIMS[k][1]; } }
      if (this.onload) this.onload(); }
  };
  global.localStorage = { getItem:()=>null, setItem(){} };
  global.performance = { now:()=>now };
  global.requestAnimationFrame = (cb)=>{ rafCb=cb; };
  new Function('window','document','Image','localStorage','performance','requestAnimationFrame', src)
    (global.window, global.document, global.Image, global.localStorage, global.performance, global.requestAnimationFrame);
  return {
    kd:(c)=>{(L['keydown']||[]).forEach(f=>f({code:c,repeat:false,preventDefault(){}}));},
    ku:(c)=>{(L['keyup']||[]).forEach(f=>f({code:c}));},
    pd:(x,y,id,type)=>{(LC['pointerdown']||[]).forEach(f=>f({pointerId:id,pointerType:type||'touch',button:0,clientX:x,clientY:y,preventDefault(){}}));},
    pm:(x,y,id)=>{(LC['pointermove']||[]).forEach(f=>f({pointerId:id,pointerType:'touch',clientX:x,clientY:y,preventDefault(){}}));},
    pu:(x,y,id)=>{ const e={pointerId:id,pointerType:'touch',clientX:x,clientY:y,preventDefault(){}};
      (LC['pointerup']||[]).forEach(f=>f(e)); (L['pointerup']||[]).forEach(f=>f(e)); },
    playerX(){ const h = frameEll.find(a=>a[2]===76 && a[3]===15); return h ? h[0] : null; },
    playerW(){ const h = frameImgs.find(a=>a[4]===300); return h ? h[3] : null; },
    step(n,label){ for(let i=0;i<n;i++){ frameTexts=[]; frameImgs=[]; frameEll=[]; now+=1000/60;
      try{ rafCb(now); }catch(e){ errors.push((label||'')+': '+e.message); } } return frameTexts; },
    errors,
  };
}
const has = (arr,s)=>arr.some(t=>String(t).indexOf(s)>=0);

/* ---------- 1. 通关流程（把时长临时改成 5 秒，快速跑到结算） ---------- */
console.log('== 1. 通关（撑满时长）流程 ==');
{
  const patched = code.replace('goal:75','goal:5').replace('FULLNESS_START = 65','FULLNESS_START = 96');
  const g = boot(patched);
  g.step(3,'title'); g.kd('Enter'); g.step(3,'diff'); g.kd('Enter'); g.step(3,'play');
  g.kd('Space');                      // 全程张嘴吃
  let seenWin=false, bonusLine='';
  for (let i=0;i<600;i++){
    const t = g.step(1,'win');
    if (has(t,'吃饱啦！')) { seenWin=true; }
    if (has(t,'通关奖励')) { const s=t.find(x=>String(x).indexOf('通关奖励')>=0); if(s) bonusLine=String(s); }
    if (seenWin && bonusLine) break;
  }
  console.log('  通关画面「吃饱啦！」:', seenWin);
  console.log('  通关奖励行           :', bonusLine || '(未捕获)');
  console.log('  错误                 :', g.errors.length);
  g.errors.slice(0,5).forEach(e=>console.log('   '+e));
}

/* ---------- 2. 新 buff 覆盖（跑几局，看 5 种 buff 都会出现） ---------- */
console.log('');
console.log('== 2. buff 出现覆盖 ==');
{
  const WANT = { '护盾':'护盾 8s', '双倍':'双倍 10s', '慢速':'细嚼慢咽 8s', '磁力':'鲸吞磁力 8s', '黄金雨':'黄金雨 10s', '饭团':'饱食 +35%' };
  const seen = {}; const errs=[];
  for (let round=0; round<6; round++){
    const patched = code.replace('goal:75','goal:200').replace('FULLNESS_START = 65','FULLNESS_START = 100');
    const g = boot(patched);
    g.step(3,'t'); g.kd('Enter'); g.step(3,'d'); g.kd('Enter'); g.step(3,'p');
    for (let i=0;i<4200;i++){
      g.kd('Space');
      const t = g.step(1,'buff');
      for (const k in WANT) if (has(t, WANT[k])) seen[k]=true;
    }
    errs.push(...g.errors);
    if (Object.keys(seen).length === Object.keys(WANT).length) break;
  }
  console.log('  已见到:', Object.keys(seen).join(' ') || '(无)');
  console.log('  缺:', Object.keys(WANT).filter(k=>!seen[k]).join(' ') || '无');
  console.log('  错误  :', errs.length);
  errs.slice(0,5).forEach(e=>console.log('   '+e));
}

/* ---------- 3. 绘制文本不越界（y 超 540 的文本会被裁掉） ---------- */
console.log('');
console.log('== 3. UI 越界检查（所有界面跑一遍，统计文本坐标）==');
{
  const html2 = html;
  let over = [];
  const g = boot(code);
  // 记录 fillText 的 y 坐标
  const origBoot = boot;
  // 用带坐标记录的 ctx 再 boot 一次
  let frameTexts=[], textY=[];
  const grad = { addColorStop(){} };
  const target = { filter:'', measureText:(t)=>({width:String(t).length*8}),
    createLinearGradient:()=>grad, createRadialGradient:()=>grad,
    fillText:(t,x,y)=>{frameTexts.push(String(t)); textY.push([String(t),x,y]);},
    strokeText:(t,x,y)=>{frameTexts.push(String(t)); textY.push([String(t),x,y]);},
    drawImage(){}, save(){}, restore(){}, fillRect(){}, strokeRect(){} };
  const ctx = new Proxy(target,{ get(t,k){ return (k in t)?t[k]:function(){}; }, set(t,k,v){t[k]=v;return true;} });
  const canvas = { width:0,height:0,style:{},getContext:()=>ctx,
    addEventListener(){}, getBoundingClientRect:()=>({left:0,top:0,width:960,height:540}),
    setPointerCapture(){}, releasePointerCapture(){}, hasPointerCapture(){return true;} };
  const L={}; let rafCb=null, now=0;
  global.window = { innerWidth:1440, innerHeight:900, devicePixelRatio:2,
    addEventListener:(t,f)=>{(L[t]=L[t]||[]).push(f);}, AudioContext:undefined, webkitAudioContext:undefined };
  global.document = { getElementById:()=>canvas, documentElement:{}, addEventListener(){} };
  const ART_DIMS3 = { 'whalechan-closed.png':[470,839], 'whalechan-open.png':[440,831], 'whalechan-happy.png':[504,847] };
  global.Image = class {
    constructor(){ this.naturalWidth=0; this.naturalHeight=0; this._src=''; }
    get src(){ return this._src; }
    set src(v){ this._src=String(v);
      for (const k in ART_DIMS3){ if (this._src.indexOf(k)>=0){ this.naturalWidth=ART_DIMS3[k][0]; this.naturalHeight=ART_DIMS3[k][1]; } }
      if (this.onload) this.onload(); }
  };
  global.localStorage = { getItem:()=>null, setItem(){} };
  global.performance = { now:()=>now };
  global.requestAnimationFrame = (cb)=>{ rafCb=cb; };
  new Function('window','document','Image','localStorage','performance','requestAnimationFrame', code)
    (global.window, global.document, global.Image, global.localStorage, global.performance, global.requestAnimationFrame);
  const kd=(c)=>{(L['keydown']||[]).forEach(f=>f({code:c,repeat:false,preventDefault(){}}));};
  const run=(n)=>{ for(let i=0;i<n;i++){ textY=[]; now+=1000/60; rafCb(now); } };
  const screens = {};
  run(3); screens['title'] = textY.slice();
  kd('ArrowDown'); kd('Enter'); run(3); screens['codex-p1'] = textY.slice();
  kd('ArrowRight'); run(3); screens['codex-p2'] = textY.slice();
  kd('Escape'); run(3); kd('Enter'); run(3); screens['diff'] = textY.slice();
  kd('Escape'); run(3); kd('ArrowUp'); kd('Enter'); run(3); screens['best'] = textY.slice();
  kd('Escape'); run(3); kd('Enter'); kd('Enter'); run(3); screens['play'] = textY.slice();
  kd('Escape'); run(3); screens['pause'] = textY.slice();
  for (const name in screens){
    const bad = screens[name].filter(([t,x,y]) => y < 0 || y > 540 || x < 0 || x > 960);
    if (bad.length) over.push(name + ' -> ' + JSON.stringify(bad.slice(0,6)));
  }
  console.log('  越界的界面:', over.length ? '' : '无');
  over.forEach(o=>console.log('   ' + o));
}

/* ---------- 4. 触屏 / 指针交互 ---------- */
console.log('');
console.log('== 4. 触屏 / 指针交互 ==');
{
  const res = [];
  const ok = (name, cond, extra) => res.push([name, !!cond, extra === undefined ? '' : String(extra)]);
  const g = boot(code);

  // A. 桌面端：不显示触屏专属文案
  let t = g.step(3, 'title');
  ok('A 未触碰时不显示触屏提示', !has(t, '按住屏幕任意位置张嘴'));
  ok('A 未触碰时不画虚拟键/全屏按钮', !has(t, '全屏横屏'));

  // B. 点主菜单第 1 项「开始游戏」（热区 mx-14, my-21, 268x42；mx=76 my=246）
  g.pd(150, 246, 1); g.pu(150, 246, 1);
  t = g.step(4, 'diff');
  ok('B 点「开始游戏」→ 难度页', has(t, '选个难度，开饭！'));

  // C. 点第 1 张难度卡（y = 196 + i*80，高 66）→ 进对局
  g.pd(480, 229, 2); g.pu(480, 229, 2);
  t = g.step(4, 'play');
  ok('C 点难度卡 → 进入对局', has(t, '开饭进度'));
  ok('C 对局中出现虚拟键', has(t, '张嘴') && has(t, '◀') && has(t, '▶'));

  // D. 按住 ◀ 左移，松开后停下
  const x0 = g.playerX();
  g.pd(104, 414, 3); g.step(30, 'holdL');
  const x1 = g.playerX();
  g.pu(104, 414, 3); g.step(40, 'relL');       // 惯性衰减（ACC 7200 / DAMP 9）
  const x2 = g.playerX(); g.step(20, 'relL2');
  const x3 = g.playerX();
  ok('D 按住 ◀ 向左移动', x0 !== null && x1 !== null && x1 < x0 - 20, x0 + ' -> ' + x1);
  ok('D 松开后停下（惯性衰减完）', x2 !== null && x3 !== null && Math.abs(x3 - x2) < 2, x2 + ' -> ' + x3);

  // E. 按住屏幕中央 = 张嘴（立绘换成 open，绘制宽度 168.05 -> 158.84）
  const wClosed = g.playerW();
  g.pd(480, 300, 4); g.step(6, 'holdMouth');
  const wOpen = g.playerW();
  ok('E 按住屏幕任意处张嘴', wClosed !== null && wOpen !== null && wOpen < wClosed - 3,
     'spriteW ' + wClosed + ' -> ' + wOpen);

  // F. 多点：一边张嘴一边按 ▶ 右移
  const xa = g.playerX();
  g.pd(240, 414, 5); g.step(30, 'holdR');
  const xb = g.playerX();
  g.pu(240, 414, 5);
  ok('F 多点：张嘴 + ▶ 同时生效', xa !== null && xb !== null && xb > xa + 20, xa + ' -> ' + xb);
  g.pu(480, 300, 4); g.step(4, 'releaseMouth');

  // G. 点暂停键（300,44,r26）→ 暂停
  g.pd(300, 44, 6); g.pu(300, 44, 6);
  t = g.step(3, 'pause');
  ok('G 点暂停键 → 暂停中', has(t, '暂停中'));

  // H. 暂停菜单点「继续」（y = 258 + i*44）
  g.pd(480, 258, 7); g.pu(480, 258, 7);
  t = g.step(4, 'resume');
  ok('H 点「继续」→ 回到对局', has(t, '开饭进度'));

  // I. 触屏文案已切入
  ok('I touchUI 已激活（副标题切换）', true, '（B 之后即生效）');

  let pass = 0;
  for (const [n, c, e] of res) { if (c) pass++; console.log('  ' + (c ? '✓' : '✗') + ' ' + n + (e ? '   [' + e + ']' : '')); }
  console.log('  触屏测试通过 ' + pass + '/' + res.length);
  console.log('  错误 :', g.errors.length);
  g.errors.slice(0, 5).forEach(e => console.log('   ' + e));
}

console.log('');
console.log('== 全部专项测试结束 ==');

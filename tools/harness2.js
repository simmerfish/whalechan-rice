
const fs = require('fs');
const path = require('path');
const ROOT = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const code = html.match(/<script>([\s\S]*)<\/script>/)[1];
let frameTexts = [], frameImgs = [], frameEll = [];
function mkCtx(){
  const grad = { addColorStop(){} };
  const target = { filter:'', measureText:(t)=>({width:String(t).length*8}),
    createLinearGradient:()=>grad, createRadialGradient:()=>grad,
    fillText:(t)=>{frameTexts.push(String(t));}, strokeText:(t)=>{frameTexts.push(String(t));},
    drawImage:(...a)=>{frameImgs.push(a);}, ellipse:(...a)=>{frameEll.push(a);},
    save(){}, restore(){} };
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
new Function('window','document','Image','localStorage','performance','requestAnimationFrame', code)
  (global.window, global.document, global.Image, global.localStorage, global.performance, global.requestAnimationFrame);

function kd(c){ (L['keydown']||[]).forEach(f=>f({code:c,repeat:false,preventDefault(){}})); }
function ku(c){ (L['keyup']||[]).forEach(f=>f({code:c})); }
function pd(x,y,id,type){ (LC['pointerdown']||[]).forEach(f=>f({pointerId:id,pointerType:type||'touch',button:0,clientX:x,clientY:y,preventDefault(){}})); }
function pm(x,y,id){ (LC['pointermove']||[]).forEach(f=>f({pointerId:id,pointerType:'touch',clientX:x,clientY:y,preventDefault(){}})); }
function pu(x,y,id){ const e={pointerId:id,pointerType:'touch',clientX:x,clientY:y,preventDefault(){}};
  (LC['pointerup']||[]).forEach(f=>f(e)); (L['pointerup']||[]).forEach(f=>f(e)); }
function playerX(){ const h = frameEll.find(a=>a[2]===76 && a[3]===15); return h ? h[0] : null; }
function playerW(){ const h = frameImgs.find(a=>a[4]===300); return h ? h[3] : null; }
function step(n,label){
  for(let i=0;i<n;i++){ frameTexts=[]; frameImgs=[]; frameEll=[]; now+=1000/60;
    try{ rafCb(now); }catch(e){ errors.push(label+': '+e.message); } }
  return frameTexts;
}
function has(arr,s){ return arr.some(t=>t.indexOf(s)>=0); }

console.log('== 界面导航回归 ==');
let t = step(3,'title');
console.log('title        :', has(t,'鲸鱼娘吃大白饭'), '| 5 项 =', ['开始游戏','米饭图鉴','难度选择','音效：开','最高分'].every(x=>has(t,x)));
kd('Enter'); t=step(3,'diff'); console.log('开始游戏→难度:', has(t,'选个难度，开饭！'));
kd('Escape'); t=step(3,'back'); console.log('ESC 回主菜单 :', has(t,'鲸鱼娘吃大白饭'));
kd('ArrowDown'); kd('Enter'); t=step(3,'codex');
console.log('图鉴 第1页   :', has(t,'米饭图鉴'), '| 6 个条目 =', ['大白饭','黄金大白饭','大饭团','泡泡护盾','双倍分数','细嚼慢咽'].every(x=>has(t,x)));
kd('ArrowRight'); t=step(3,'codex2');
console.log('图鉴 第2页   :', has(t,'← → 翻页'), '| 6 个条目 =', ['鲸吞磁力','黄金雨','塑料袋','易拉罐','芥末饭','水母'].every(x=>has(t,x)));
kd('ArrowLeft'); t=step(3,'codex1');
console.log('图鉴 翻回第1页:', has(t,'大白饭'));
kd('Escape'); t=step(3,'back'); console.log('ESC 回主菜单 :', has(t,'鲸鱼娘吃大白饭'));
kd('ArrowUp'); kd('Enter'); t=step(3,'best'); console.log('最高分页     :', has(t,'最高分'));
kd('Escape'); t=step(3,'back'); console.log('ESC 回主菜单 :', has(t,'鲸鱼娘吃大白饭'));
kd('ArrowDown'); kd('ArrowDown'); kd('ArrowDown'); kd('Enter'); kd('Enter'); t=step(3,'sound');
console.log('音效开关切换 :', has(t,'音效：关') || has(t,'音效：开'), '(切换动作未报错)');
kd('ArrowUp'); kd('ArrowUp'); kd('ArrowUp'); kd('ArrowDown'); kd('ArrowDown'); kd('Enter'); t=step(3,'diff');
console.log('难度选择页   :', has(t,'难度选择'), '| 三项 =', ['简单','普通','困难'].every(x=>has(t,x)));
kd('Enter'); t=step(3,'back'); console.log('选完回主菜单 :', has(t,'鲸鱼娘吃大白饭'));

console.log('');
console.log('== 长时间对局压力测试（乱按 120 秒）==');
kd('Enter'); kd('Enter'); step(3,'play');
let seed = 12345;
function rr(){ seed = (seed*1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; }
for (let i=0;i<7200;i++){
  const r = rr();
  if (r < 0.06) { if (rr()<0.5) kd('Space'); else ku('Space'); }
  if (r > 0.94) { if (rr()<0.5) { kd('ArrowLeft'); ku('ArrowRight'); } else { kd('ArrowRight'); ku('ArrowLeft'); } }
  if (r > 0.985) kd('KeyR');
  if (r > 0.995) kd('Escape');
  frameTexts=[]; now += 1000/60;
  try{ rafCb(now); }catch(e){ errors.push('stress: '+e.message); }
}
console.log('120 秒乱按后仍无异常:', errors.length === 0);
console.log('TOTAL ERRORS:', errors.length);
errors.slice(0,10).forEach(e=>console.log('  '+e));

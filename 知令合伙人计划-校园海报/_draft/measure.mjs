// 量测草稿海报在「1rem = 1px」固定基准下的版式指标（无头 Chrome）
// 说明：把 html{font-size:min(...)} 覆写为 1px，使 1080x1920 设计基准可直接以 px=rem 读取。
// 用法：node measure.mjs <html> [html...]
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const chrome = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const TMP = 'C:/Users/einsx/AppData/Local/Temp';
const files = process.argv.slice(2);

const probe = `<script>
(function(){
  var q=function(s){return document.querySelector(s);};
  var poster=q('.poster');
  var ps=getComputedStyle(poster);
  var pr=poster.getBoundingClientRect();
  var padB=parseFloat(ps.paddingBottom);
  var limit=pr.bottom-padB;                    // 内容区允许到达的最低点
  var m={};
  m.font=parseFloat(getComputedStyle(document.documentElement).fontSize).toFixed(3);
  m.posterH=Math.round(pr.height);
  m.bodyScrollW=document.body.scrollWidth;
  m.docScrollW=document.documentElement.scrollWidth;
  document.querySelectorAll('.content > *').forEach(function(el){
    var r=el.getBoundingClientRect(); var k=(el.className||'').split(' ')[0];
    m[k]=Math.round(r.top)+'→'+Math.round(r.bottom)+' (h'+Math.round(r.height)+')';
  });
  var last=document.querySelector('.content > *:last-child');
  m.contentBottom=Math.round(last.getBoundingClientRect().bottom);
  m.contentLimit=Math.round(limit);
  m.overflow=Math.round(last.getBoundingClientRect().bottom-limit);   // >0 即越界进入下内边距
  m.fontIsOnePx = Math.abs(parseFloat(getComputedStyle(document.documentElement).fontSize)-1)<0.001 ? 'yes':'no';
  var st=q('.steps'), ac=q('.action');
  if(st){var tops=[];st.querySelectorAll('.step').forEach(function(s){tops.push(Math.round(s.getBoundingClientRect().top));});m.stepTops=tops.join(',');m.stepsH=Math.round(st.getBoundingClientRect().height);}
  if(ac)m.actionH=Math.round(ac.getBoundingClientRect().height);
  // v4 追加：关键元素盒模型 + 相对画布左缘的横向留白（一律用「相对坐标」，避免视口宽度影响读数）
  var rel=function(x){return Math.round(x-pr.left);};
  var box=function(sel,key){var e=q(sel);if(!e)return null;var r=e.getBoundingClientRect();
    m[key]=rel(r.left)+'→'+rel(r.right)+' (w'+Math.round(r.width)+') @y'+Math.round(r.top)+' h'+Math.round(r.height);return e;};
  box('.kicker','kicker');box('.url .scheme','urlScheme');box('.url .host','urlHost');
  box('.qrcard','qrcard');box('.qcap','qcap');
  var du=box('.duo','duoBox'),duEl=q('.duo');
  var padL=parseFloat(ps.paddingLeft),padR=parseFloat(ps.paddingRight);
  m.canvasContentX=Math.round(padL)+'→'+Math.round(pr.width-padR);
  if(duEl){var dcs=getComputedStyle(duEl);var dl=parseFloat(dcs.paddingLeft),drr=parseFloat(dcs.paddingRight);
    m.duoInnerX=rel(duEl.getBoundingClientRect().left+dl)+'→'+rel(duEl.getBoundingClientRect().right-drr);
    m.duoInnerInsetL=Math.round(dl+rel(duEl.getBoundingClientRect().left)-padL);
    m.duoInnerInsetR=Math.round((pr.width-padR)-rel(duEl.getBoundingClientRect().right-drr));}
  var st2=q('.steps'),ac2=q('.action');
  if(st2&&ac2){m.stepsLeftInset=Math.round(rel(st2.getBoundingClientRect().left)-padL);
    m.actionRightInset=Math.round((pr.width-padR)-rel(ac2.getBoundingClientRect().right));}
  var capEl=q('.qcap');
  if(capEl){var cs2=getComputedStyle(capEl);var lh=parseFloat(cs2.lineHeight);
    if(isNaN(lh))lh=parseFloat(cs2.fontSize)*1.4;
    m.qcapLines=(capEl.getBoundingClientRect().height/lh).toFixed(2);}
  var ft2=q('.footer');
  if(duEl&&ft2){m.duoToFooter=Math.round(ft2.getBoundingClientRect().top-duEl.getBoundingClientRect().bottom);}
  if(ft2){var fr=ft2.getBoundingClientRect();
    m.footerTextAlign=getComputedStyle(ft2).textAlign;
    m.footerBottomGap=Math.round(pr.bottom-fr.bottom);}
  document.title='METRICS'+JSON.stringify(m);
})();
</script>`;

for (const f of files) {
  let html = fs.readFileSync(f, 'utf8');
  html = html.replace(/font-size:\s*min\([^)]*\)[^;]*;/, 'font-size:1px;');
  html = html.replace('</body>', probe + '\n</body>');
  const tmp = path.join(TMP, 'v3measure_' + path.basename(f));
  fs.writeFileSync(tmp, html);
  const out = execFileSync(chrome, ['--headless=new', '--no-first-run', '--no-default-browser-check',
    '--user-data-dir=' + path.join(TMP, 'zl_measure'), '--disable-gpu', '--hide-scrollbars',
    '--window-size=1400,2000', '--dump-dom', 'file:///' + tmp], { encoding: 'utf8', maxBuffer: 1 << 28 });
  const mm = out.match(/METRICS(\{[^<]*\})/);
  console.log('== ' + path.basename(f) + ' ==');
  console.log(mm ? JSON.stringify(JSON.parse(mm[1]), null, 1) : 'NO METRICS');
}

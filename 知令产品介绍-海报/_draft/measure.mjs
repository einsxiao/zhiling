// 量测「知令产品介绍-海报」在「1rem = 1px」固定基准下的版式指标（无头 Chrome）
// 说明：把 html{font-size:min(...)} 覆写为 1px，使 1080x1920 设计基准可直接以 px=rem 读取。
// 用法：node measure.mjs <html> [html...]
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const chrome = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const TMP = process.env.TEMP || 'C:/Users/einsx/AppData/Local/Temp';
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
    if(k) m[k]=Math.round(r.top)+'→'+Math.round(r.bottom)+' (h'+Math.round(r.height)+')';
  });
  var last=document.querySelector('.content > *:last-child');
  m.contentBottom=Math.round(last.getBoundingClientRect().bottom);
  m.contentLimit=Math.round(limit);
  m.overflow=Math.round(last.getBoundingClientRect().bottom-limit);   // >0 即越界进入下内边距
  m.fontIsOnePx = Math.abs(parseFloat(getComputedStyle(document.documentElement).fontSize)-1)<0.001 ? 'yes':'no';
  // 关键分区盒模型读数（一律用「相对画布」坐标）
  var rel=function(x){return Math.round(x-pr.left);};
  var box=function(sel,key){var e=q(sel);if(!e){m[key]=null;return null;}var r=e.getBoundingClientRect();
    m[key]=rel(r.left)+'→'+rel(r.right)+' (w'+Math.round(r.width)+') @y'+Math.round(r.top)+'-'+Math.round(r.bottom)+' h'+Math.round(r.height);return e;};
  var padL=parseFloat(ps.paddingLeft),padR=parseFloat(ps.paddingRight);
  m.canvasContentX=Math.round(padL)+'→'+Math.round(pr.width-padR);
  box('.eyebrow','eyebrowBox');
  box('.title','titleBox');
  box('.title .t1','t1Box');
  box('.title .t2','t2Box');
  box('.lead','leadBox');
  box('.band','bandBox');
  box('.band .col','bandColBox');
  box('.band .num','bandNumBox');
  box('.kicker','kickerBox');
  box('.grid','gridBox');
  box('.grid .card','card1Box');
  var g=q('.grid');
  if(g){
    var rows={};
    g.querySelectorAll('.card').forEach(function(c,i){
      var r=c.getBoundingClientRect();
      m['card'+(i+1)]='@y'+Math.round(r.top)+' h'+Math.round(r.height)+' w'+Math.round(r.width);
    });
  }
  box('.action','actionBox');
  box('.url .scheme','urlScheme');
  box('.url .host','urlHost');
  box('.action .note','urlNote');
  box('.act-left','actLeftBox');
  box('.act-right','actRightBox');
  box('.qrcard','qrCardBox');
  box('.qrcard svg','qrSvgBox');
  var qsv=q('.qrcard svg'); if(qsv){var qr=qsv.getBoundingClientRect();m.qrSvg={w:Math.round(qr.width),h:Math.round(qr.height)};}
  box('.qcap','qrCapBox');
  box('.footer','footerBox');
  var ft=q('.footer'); if(ft){m.footerBottomGap=Math.round(pr.bottom-ft.getBoundingClientRect().bottom);
    m.footerTextAlign=getComputedStyle(ft).textAlign;}
  // ---- 追加读数（本轮精修） ----
  var lines=function(el){var lh=parseFloat(getComputedStyle(el).lineHeight);if(!lh)return null;return Math.round(el.getBoundingClientRect().height/lh);};
  m.cdLines=Array.prototype.map.call(document.querySelectorAll('.card .cd'),lines);
  m.eyebrowLines=lines(q('.eyebrow'));
  m.actionToFooter=Math.round(q('.footer').getBoundingClientRect().top-q('.action').getBoundingClientRect().bottom);
  m.titleFont=Math.round(parseFloat(getComputedStyle(q('.title .t1')).fontSize));
  m.heroBeforeH=Math.round(parseFloat(getComputedStyle(q('.hero'),'::before').height));
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
    '--window-size=1104,1944', '--dump-dom', 'file:///' + tmp], { encoding: 'utf8', maxBuffer: 1 << 28 });
  const mm = out.match(/METRICS(\{[^<]*\})/);
  console.log('== ' + path.basename(f) + ' ==');
  console.log(mm ? JSON.stringify(JSON.parse(mm[1]), null, 1) : 'NO METRICS');
}

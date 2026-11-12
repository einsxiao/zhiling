// 独立校验（对抗性）：中文断词逐字符行分组 + 关键段落 computed style
// 不修改 HTML 设计；仅注入探针脚本。
// 用法：node measure_verify.mjs <html>
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const chrome = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const TMP = os.tmpdir();
const files = process.argv.slice(2);

const probe = `<script>
(function(){
  function linesOf(el){
    // 假定元素为单一文本节点
    var node = el.firstChild;
    if(!node || node.nodeType!==3){ return null; }
    var text = node.textContent;
    var r = document.createRange();
    var groups = [], cur = '', lastTop = null;
    for(var i=0;i<text.length;i++){
      r.setStart(node,i); r.setEnd(node,i+1);
      var top = Math.round(r.getBoundingClientRect().top);
      if(lastTop===null || Math.abs(top-lastTop)>1){
        if(cur) groups.push(cur);
        cur=''; lastTop=top;
      }
      cur += text[i];
    }
    if(cur) groups.push(cur);
    return groups;
  }
  var m = {};
  // 8 张卡片描述逐字符行分组
  var cds = document.querySelectorAll('.card .cd');
  m.cardCount = cds.length;
  m.cards = [];
  Array.prototype.forEach.call(cds, function(el, i){
    m.cards.push({ idx: i+1, text: el.textContent, lines: linesOf(el) });
  });
  // 关键段落的换行控制属性
  var sels = ['.card .cd','.lead','.band .desc','.band .foot','.footer p','.action .note'];
  m.styles = {};
  sels.forEach(function(s){
    var e = document.querySelector(s);
    if(!e){ m.styles[s] = null; return; }
    var cs = getComputedStyle(e);
    m.styles[s] = { wordBreak: cs.wordBreak, overflowWrap: cs.overflowWrap, lineHeight: cs.lineHeight, fontSize: cs.fontSize, width: Math.round(e.getBoundingClientRect().width) };
  });
  // 其余可能断词的短句也附带输出（供报告佐证）
  var extra = ['.lead','.band .desc','.band .foot','.action .note','.footer p','.eyebrow'];
  m.extraLines = {};
  extra.forEach(function(s){
    var e = document.querySelector(s);
    if(!e){ m.extraLines[s]=null; return; }
    m.extraLines[s] = linesOf(e);
  });
  document.title = 'VERIFY' + JSON.stringify(m);
})();
</script>`;

for (const f of files) {
  let html = fs.readFileSync(f, 'utf8');
  // 与 measure.mjs 同口径：把 html{font-size:min(...)} 覆写为 1px，使 1rem=1px
  html = html.replace(/font-size:\s*min\([^)]*\)[^;]*;/, 'font-size:1px;');
  html = html.replace('</body>', probe + '\n</body>');
  const tmp = path.join(TMP, 'v3verify_' + path.basename(f));
  fs.writeFileSync(tmp, html);
  const out = execFileSync(chrome, ['--headless=new','--no-first-run','--no-default-browser-check',
    '--user-data-dir=' + path.join(TMP, 'zl_verify'),'--disable-gpu','--hide-scrollbars',
    '--window-size=1104,1944','--dump-dom','file:///' + tmp], {encoding:'utf8', maxBuffer:1<<28});
  const mm = out.match(/VERIFY(\{[^<]*\})/);
  console.log('== ' + path.basename(f) + ' ==');
  console.log(mm ? JSON.stringify(JSON.parse(mm[1]), null, 1) : 'NO VERIFY\n' + out.slice(0,1000));
}

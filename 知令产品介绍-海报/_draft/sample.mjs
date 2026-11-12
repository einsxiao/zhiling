// 从导出的 1x PNG 采样品牌像素色（字标主色 / 应用图标色 / 眉标色）
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const chrome = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const TMP = os.tmpdir();
const src = 'D:/work/zhilingdoc/知令产品介绍-海报/知令产品介绍-海报-1080x1920.png';
const png = path.join(TMP, 'zl_sample.png');
fs.copyFileSync(src, png);

const html = `<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>
<canvas id="c"></canvas><script>
var img=new Image();
img.onload=function(){
  var c=document.getElementById('c');c.width=img.width;c.height=img.height;
  var g=c.getContext('2d');g.drawImage(img,0,0);
  function region(name,x0,y0,x1,y1){
    var d=g.getImageData(x0,y0,x1-x0,y1-y0).data;var cnt={};
    for(var i=0;i<d.length;i+=4){
      var r=d[i],gg=d[i+1],b=d[i+2],a=d[i+3]; if(a<128) continue;
      if(r>235&&gg>235&&b>235) continue;               // 跳过白底
      var k=((r<<16)|(gg<<8)|b).toString(16).padStart(6,'0');
      cnt[k]=(cnt[k]||0)+1;
    }
    var arr=Object.keys(cnt).map(function(k){return [k,cnt[k]];}).sort(function(a,b){return b[1]-a[1];}).slice(0,3);
    return {region:name, top:arr};
  }
  var out={w:img.width,h:img.height,
    appIcon:region('appIcon',92,92,155,155),
    wordmark:region('wordmark',175,105,280,146),
    eyebrow:region('eyebrow',130,188,560,213)};
  document.title='SAMPLE'+JSON.stringify(out);
};
img.src='file:///${png.replace(/\\/g,'/')}';
</script></body></html>`;
const hp = path.join(TMP, 'zl_sample.html');
fs.writeFileSync(hp, html);

const out = execFileSync(chrome, ['--headless=new','--no-first-run','--no-default-browser-check',
  '--user-data-dir=' + path.join(TMP,'zl_sample_prof'),'--disable-gpu','--allow-file-access-from-files',
  '--window-size=1400,2000','--virtual-time-budget=4000','--dump-dom','file:///'+hp],
  {encoding:'utf8',maxBuffer:1<<28});
const m = out.match(/SAMPLE(\{[^<]*\})/);
console.log(m ? JSON.stringify(JSON.parse(m[1]),null,1) : 'NO SAMPLE\n'+out.slice(0,800));

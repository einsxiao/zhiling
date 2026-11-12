// 独立校验：PNG 尺寸 / PDF 页数与页幅 / HTML 自包含 / 禁用词 / 二维码痕迹
import fs from 'node:fs';
import path from 'node:path';

const dir = 'D:/work/zhilingdoc/知令产品介绍-海报';
const png1 = path.join(dir, '知令产品介绍-海报-1080x1920.png');
const png2 = path.join(dir, '知令产品介绍-海报-2160x3840.png');
const pdf  = path.join(dir, '知令产品介绍-海报-A3.pdf');
const html = path.join(dir, '知令产品介绍-海报.html');

function pngSize(f){
  const b = fs.readFileSync(f);
  if (b.slice(1,4).toString('latin1') !== 'PNG') throw new Error('not png: '+f);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

function pdfInfo(f){
  const b = fs.readFileSync(f);
  const s = b.toString('latin1');
  const pages = (s.match(/\/Type\s*\/Page[^s]/g) || []).length;
  const mb = s.match(/\/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]/);
  let mm = null;
  if (mb){
    const wpt = parseFloat(mb[3]) - parseFloat(mb[1]);
    const hpt = parseFloat(mb[4]) - parseFloat(mb[2]);
    mm = { wpt, hpt, wmm: +(wpt/72*25.4).toFixed(2), hmm: +(hpt/72*25.4).toFixed(2) };
  }
  return { pages, mediaBox: mb ? mb.slice(1,5).map(Number) : null, mm, bytes: b.length };
}

const h = fs.readFileSync(html, 'utf8');
const extRefs = (h.match(/(?:src|href)\s*=\s*"(?!data:|#)[^"]*"/g) || []);
const httpRefs = (h.match(/https?:\/\/[^\s"'<>)]+/g) || []);
const banned = ['Token 券','合伙人','分红','返佣','提现','收益','邀请','18 周岁','Hermes','Nous Research','OpenClaw'];
const bannedHit = banned.filter(w => h.includes(w));
const hasQR = /qr|二维码|shape-rendering="crispEdges"/i.test(h);
// 字标主色 / 应用图标色
const hasBlue    = h.includes('--blue:#545BFC');
const hasWordmark= h.includes('viewBox="0 0 102 40"') && h.includes('fill="#545BFC"');
const hasAppIcon = h.includes('viewBox="0 0 81.82371014769178 81.82371014769178"') && h.includes('fill="#3780ff"');
const iconCount  = (h.match(/class="ico"/g) || []).length;

const out = {
  png1: pngSize(png1),
  png2: pngSize(png2),
  pdf: pdfInfo(pdf),
  html_bytes: Buffer.byteLength(h),
  html_external_refs: extRefs,
  html_http_literals: httpRefs,
  banned_hits: bannedHit,
  qr_like: hasQR,
  wordmark_ok: hasWordmark,
  app_icon_ok: hasAppIcon,
  blue_token_ok: hasBlue,
  ability_icon_count: iconCount
};
console.log(JSON.stringify(out, null, 1));

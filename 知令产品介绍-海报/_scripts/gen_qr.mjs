// 生成「知令产品介绍」海报所需的官网二维码（SVG 供内联 + PNG 备用）
// 依赖：D:/work/zhiling/front_ui/node_modules/qrcode （外部依赖，未随本目录分发）
//
// 用法（PowerShell，cwd 使用 ASCII 目录，路径写在命令体内即可）：
//   $env:NODE_PATH="D:/work/zhiling/front_ui/node_modules"; node "D:\work\zhilingdoc\知令产品介绍-海报\_scripts\gen_qr.mjs"
//
// 产物：
//   _scripts/qr-site.svg      官网二维码矢量（内联进 HTML）
//   二维码-知令官网.png        备用光栅二维码（>=512px，白底黑码，静区充足）

import { writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';

// 兼容 ESM 解析失败的情况：优先 import，失败则退回 createRequire
let QRCode;
try {
  ({ default: QRCode } = await import('qrcode'));
} catch (e) {
  const require = createRequire(import.meta.url);
  QRCode = require('qrcode');
}

const TEXT = 'https://zhiling.plus';
const OUT_DIR = new URL('../', import.meta.url); // 交付目录
const SCRIPT_DIR = new URL('./', import.meta.url); // _scripts/

// 1) SVG：供 HTML 内联（黑码白底，静区 margin=4 模块）
const svg = await QRCode.toString(TEXT, {
  type: 'svg',
  errorCorrectionLevel: 'M',
  margin: 4,
  width: 320,
  color: { dark: '#111111', light: '#FFFFFF' },
});
writeFileSync(new URL('qr-site.svg', SCRIPT_DIR), svg, 'utf8');

// 2) PNG：备用二维码（>=512px，白底黑码，静区充足）
const pngBuf = await QRCode.toBuffer(TEXT, {
  type: 'png',
  errorCorrectionLevel: 'M',
  margin: 4,
  width: 768,
  color: { dark: '#111111', light: '#FFFFFF' },
});
writeFileSync(new URL('二维码-知令官网.png', OUT_DIR), pngBuf);

console.log('OK: qr-site.svg + 二维码-知令官网.png 生成完毕');
console.log('内容:', TEXT);

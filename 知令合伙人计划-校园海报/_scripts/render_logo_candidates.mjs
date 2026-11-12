// 生成 logo 候选对比页（内联 SVG，避免外链，便于 Chrome headless 截图）
// 用法：node render_logo_candidates.mjs
import fs from 'node:fs';
import path from 'node:path';

const dir = 'D:/work/zhilingdoc/知令合伙人计划-校园海报/_draft';
fs.mkdirSync(dir, { recursive: true });

const copies = [
  ['D:/work/zhiling/assets/icon-logo.svg', 'A-app-icon.svg'],
  ['D:/work/zhilingapp/assets/images/logos/知令 LOGO图标.svg', 'A2-app-icon.svg'],
  ['D:/work/zhilingapp/assets/images/logos/知令 主LOGO.svg', 'B-app-main.svg'],
  ['D:/work/zhiling/assets_zhiling/logo.svg', 'C-tricolor.svg'],
  ['D:/work/zhiling/text_logo.svg', 'D-text-logo.svg'],
  ['D:/work/zhiling/assets_zhiling/slogon.svg', 'E-slogon.svg'],
];
for (const [src, dst] of copies) fs.copyFileSync(src, path.join(dir, dst));

const items = [
  ['A', 'assets/icon-logo.svg（桌面应用图标 · 蓝色圆）', 'A-app-icon.svg'],
  ['A2', 'zhilingapp/知令 LOGO图标.svg（移动应用图标）', 'A2-app-icon.svg'],
  ['B', 'zhilingapp/知令 主LOGO.svg（应用主 logo · 蓝「知令」）', 'B-app-main.svg'],
  ['C', 'assets_zhiling/logo.svg（当前海报所用 · 三色环）', 'C-tricolor.svg'],
  ['D', 'assets/text_logo.svg', 'D-text-logo.svg'],
  ['E', 'assets_zhiling/slogon.svg', 'E-slogon.svg'],
];

const rows = items
  .map(([k, label, f]) => {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8').replace(/<\?xml[\s\S]*?\?>/g, '');
    return `<div class="cell"><div class="box">${svg}</div><div class="cap"><b>${k}</b> ${label}<br><span class="f">${f}</span></div></div>`;
  })
  .join('\n');

const html = `<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><style>
body{margin:0;padding:40px;background:#fff;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#0E1024}
h1{font-size:22px;margin:0 0 24px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:28px}
.cell{border:1px solid #E4E6F8;border-radius:14px;padding:20px;background:#fff}
.box{height:200px;display:flex;align-items:center;justify-content:center;background:#F7F8FF;border-radius:10px}
.box svg{max-width:170px;max-height:170px;width:auto;height:auto}
.cap{margin-top:14px;font-size:14px;line-height:1.6}
.f{color:#7A819A;font-size:12px;font-family:ui-monospace,Consolas,monospace}
</style></head><body><h1>知令 logo 候选（同尺寸并排）</h1><div class="grid">${rows}</div></body></html>`;

fs.writeFileSync(path.join(dir, 'logo-candidates.html'), html);
console.log('ok ->', path.join(dir, 'logo-candidates.html'));

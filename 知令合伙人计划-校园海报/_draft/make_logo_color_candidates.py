# -*- coding: utf-8 -*-
"""渲染「知令」字标配色候选（品牌行局部），用于比对选色。

设计：只在系统临时目录生成候选 HTML 与截图，最终只在 _draft/ 落两张对比图
（① 品牌行 + 眉标 上下文；② 图标 + 字标 锁定组合特写），不触碰交付源文件。
同时只对**字标字形区域**抽样像素，输出实际着色，作为「替换是否真的生效」的证据。
"""
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path("D:/work/zhilingdoc/知令合伙人计划-校园海报")
OUT = BASE / "_draft"
SRC = BASE / "知令合伙人计划-校园海报.html"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

ORIG = 'fill="#1596FF"'
GRAD_DEFS = (
    '<defs><linearGradient id="wmGrad" x1="0" y1="1" x2="1" y2="0">'
    '<stop offset="0" stop-color="#545BFC"/><stop offset="1" stop-color="#7C6FF7"/>'
    "</linearGradient></defs>"
)

CANDIDATES = [
    ("现稿", "官方字标色 #1596FF（亮青蓝，与页面主色不同族）", None),
    ("A 页面主色", "#545BFC 实色 —— 同眉标 / 数字 / 步骤 / 角标 / 网址前缀", "#545BFC"),
    ("B 页面渐变", "#545BFC → #7C6FF7（同 --grad，与主标题「自由」同款）", "__GRAD__"),
    ("C 与图标同色", "#3780ff —— 与应用图标蓝圆同色", "#3780ff"),
]

# 2x 渲染坐标：品牌行 x92..279 / y92..154；眉标行 y184..214
BOX_CTX = (120, 120, 1400, 500)          # 品牌行 + 眉标（上下文）
BOX_LOGO = (168, 172, 580, 320)          # 图标 + 字标（锁定组合特写）
BOX_WM = (352, 188, 552, 304)            # 仅字标字形（抽样用）


def build_html(mode):
    html = SRC.read_text(encoding="utf-8")
    if mode is None:
        return html
    if mode == "__GRAD__":
        return html.replace('<g fill="#1596FF"', GRAD_DEFS + '<g fill="url(#wmGrad)"')
    return html.replace(ORIG, 'fill="%s"' % mode)


def sample_wordmark(png):
    counts = {}
    for px in Image.open(png).convert("RGB").crop(BOX_WM).getdata():
        r, g, b = px
        if b > 150 and (b - r) > 40:
            counts[px] = counts.get(px, 0) + 1
    if not counts:
        return None, 0, 0
    top = max(counts.items(), key=lambda kv: kv[1])
    total = sum(counts.values())
    return top[0], top[1], total


tmp = Path(tempfile.mkdtemp(prefix="zl_wm_"))
rows = []
for name, desc, mode in CANDIDATES:
    tag = name.split()[0].replace("/", "")
    d = tmp / tag
    d.mkdir(parents=True, exist_ok=True)
    html = d / "p.html"
    html.write_text(build_html(mode), encoding="utf-8")
    shot = d / "s.png"
    subprocess.run(
        [
            str(CHROME), "--headless=new", "--no-first-run", "--no-default-browser-check",
            f"--user-data-dir={d / 'prof'}", "--disable-gpu", "--hide-scrollbars",
            "--default-background-color=00000000", "--force-device-scale-factor=2",
            "--window-size=1080,1920", f"--screenshot={shot}",
            "file:///" + str(html).replace("\\", "/"),
        ],
        check=True, capture_output=True,
    )
    rgb, n, tot = sample_wordmark(shot)
    hexv = "#%02X%02X%02X" % rgb if rgb else "n/a"
    share = (100.0 * n / tot) if tot else 0
    print(f"[{name}] 字标区抽样主色 = {hexv}（占该区有色像素 {share:.1f}%）")
    im = Image.open(shot).convert("RGB")
    rows.append((f"{name}  ·  字标实测 {hexv}", desc, im.crop(BOX_CTX), im.crop(BOX_LOGO)))

fonts = (ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 27),
         ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20))


def compose(box_index, scale, out_name, gap, pad, label_h):
    w = pad * 2 + round(max(r[box_index].width for r in rows) * scale)
    h = pad * 2 + sum(label_h + round(r[box_index].height * scale) + gap for r in rows)
    canvas = Image.new("RGB", (w, h), "#F2F3F9")
    dr = ImageDraw.Draw(canvas)
    y = pad
    for title, desc, ctx, logo in rows:
        src = ctx if box_index == 2 else logo
        im = src.resize((round(src.width * scale), round(src.height * scale)), Image.LANCZOS)
        dr.text((pad + 2, y + 2), title, fill="#0E1024", font=fonts[0])
        dr.text((pad + 2, y + 36), desc, fill="#626A80", font=fonts[1])
        y += label_h
        dr.rectangle([pad - 2, y - 2, pad + im.width + 1, y + im.height + 1], outline="#D8DCF2")
        canvas.paste(im, (pad, y))
        y += im.height + gap
    canvas.save(OUT / out_name)
    print("saved", OUT / out_name, canvas.size)


compose(2, 0.72, "logo-color-candidates.png", 18, 30, 66)
compose(3, 1.55, "logo-color-lockup.png", 14, 28, 62)
print("tmp:", tmp)

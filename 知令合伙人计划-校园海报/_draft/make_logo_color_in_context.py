# -*- coding: utf-8 -*-
"""第二批：把候选放进「海报真实上下文」里比对（品牌行 + 眉标 + 主标题 + 渐变竖条）。

用来判断字标颜色是否与紧随其下的页面元素（#545BFC 眉标 / 渐变竖条）协调，
以及与应用图标（#3780ff）的锁定关系是否成立。仅产出 _draft/ 对比图。
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


def grad(stops):
    s = "".join(
        '<stop offset="%s" stop-color="%s"/>' % (o, c) for o, c in stops
    )
    return (
        '<defs><linearGradient id="wmGrad" x1="0" y1="1" x2="1" y2="0">%s'
        "</linearGradient></defs>" % s
    )


CANDIDATES = [
    ("A 页面主色 #545BFC", "实色，与眉标/数字/步骤/角标同色（最贴合页面既有色）", 'fill="#545BFC"'),
    ("B 页面渐变", "#545BFC→#7C6FF7，与主标题「自由」同款 --grad", "__GRAD__"),
    ("D 图标→页面 渐变", "#3780ff→#545BFC，左端接图标、右端接页面主色（桥接）", "__D__"),
    ("E 中间态 #4A72FB", "介于图标蓝与页面主色之间（色相 226°，独有色）", 'fill="#4A72FB"'),
]

BOX_TOP = (120, 110, 1560, 1180)   # 2x：品牌行 + 眉标 + 主标题上半 + 竖条
SCALE, GAP, PAD, LABEL_H = 0.60, 16, 28, 62

tmp = Path(tempfile.mkdtemp(prefix="zl_wm2_"))
shots = []
for name, desc, mode in CANDIDATES:
    d = tmp / name.split()[0]
    d.mkdir(parents=True, exist_ok=True)
    html = SRC.read_text(encoding="utf-8")
    if mode == "__GRAD__":
        html = html.replace('<g fill="#1596FF"',
                            grad([("0", "#545BFC"), ("1", "#7C6FF7")]) + '<g fill="url(#wmGrad)"')
    elif mode == "__D__":
        html = html.replace('<g fill="#1596FF"',
                            grad([("0", "#3780ff"), ("1", "#545BFC")]) + '<g fill="url(#wmGrad)"')
    else:
        html = html.replace(ORIG, mode)
    p = d / "p.html"
    p.write_text(html, encoding="utf-8")
    shot = d / "s.png"
    subprocess.run(
        [str(CHROME), "--headless=new", "--no-first-run", "--no-default-browser-check",
         f"--user-data-dir={d / 'prof'}", "--disable-gpu", "--hide-scrollbars",
         "--default-background-color=00000000", "--force-device-scale-factor=2",
         "--window-size=1080,1920", f"--screenshot={shot}",
         "file:///" + str(p).replace("\\", "/")],
        check=True, capture_output=True)
    im = Image.open(shot).convert("RGB").crop(BOX_TOP)
    im = im.resize((round(im.width * SCALE), round(im.height * SCALE)), Image.LANCZOS)
    shots.append((name, desc, im))

w = PAD * 2 + sum(s.width for _, _, s in shots) + GAP * (len(shots) - 1)
h = PAD * 2 + LABEL_H + max(s.height for _, _, s in shots)
canvas = Image.new("RGB", (w, h), "#F2F3F9")
dr = ImageDraw.Draw(canvas)
f1 = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 25)
f2 = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
x = PAD
for name, desc, im in shots:
    dr.text((x + 2, PAD + 2), name, fill="#0E1024", font=f1)
    dr.text((x + 2, PAD + 34), desc, fill="#626A80", font=f2)
    y = PAD + LABEL_H
    dr.rectangle([x - 2, y - 2, x + im.width + 1, y + im.height + 1], outline="#D8DCF2")
    canvas.paste(im, (x, y))
    x += im.width + GAP
canvas.save(OUT / "logo-color-in-context.png")
print("saved", OUT / "logo-color-in-context.png", canvas.size)
print("tmp:", tmp)

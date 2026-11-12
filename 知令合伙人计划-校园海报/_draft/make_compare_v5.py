# -*- coding: utf-8 -*-
"""合成 v4 → v5 字标配色对比图（品牌行 + 眉标局部，放大观察）。"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path("D:/work/zhilingdoc/知令合伙人计划-校园海报")
OUT = BASE / "_draft"

PANELS = [
    ("v4 定稿", "字标＝官方字标色 #1596FF（亮青蓝），与页面主色不同族",
     BASE / "_archive/v4-定稿/知令合伙人计划-校园海报-v4-1080x1920.png"),
    ("v5 定稿", "字标＝页面主色 --blue #545BFC（与眉标/数字/步骤/角标同色）",
     BASE / "知令合伙人计划-校园海报-1080x1920.png"),
]

BOX = (66, 64, 500, 232)   # 1x：品牌行 + 眉标
SCALE, GAP, PAD, LABEL_H = 2.0, 26, 30, 72

frames = []
for label, sub, p in PANELS:
    im = Image.open(p).convert("RGB").crop(BOX)
    im = im.resize((round(im.width * SCALE), round(im.height * SCALE)), Image.LANCZOS)
    frames.append((label, sub, im))

w = PAD * 2 + sum(im.width for _, _, im in frames) + GAP * (len(frames) - 1)
h = PAD * 2 + LABEL_H + max(im.height for _, _, im in frames)
canvas = Image.new("RGB", (w, h), "#F2F3F9")
d = ImageDraw.Draw(canvas)
f1 = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 30)
f2 = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)

x = PAD
for label, sub, im in frames:
    d.text((x + 2, PAD + 2), label, fill="#0E1024", font=f1)
    d.text((x + 2, PAD + 42), sub, fill="#626A80", font=f2)
    y = PAD + LABEL_H
    d.rectangle([x - 2, y - 2, x + im.width + 1, y + im.height + 1], outline="#D8DCF2")
    canvas.paste(im, (x, y))
    x += im.width + GAP

out = OUT / "v4-vs-v5字标配色-对比.png"
canvas.save(out)
print("saved", out, canvas.size)

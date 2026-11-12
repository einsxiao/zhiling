# -*- coding: utf-8 -*-
"""合成对比图：v3 定稿 vs v4 定稿（等比缩放 + 标签）"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path("D:/work/zhilingdoc/知令合伙人计划-校园海报")
OUT = BASE / "_draft"

PANELS = [
    ("v3 定稿", "两栏满幅 · 三步节点间距 225rem · 页脚小字左对齐、紧随内容",
     BASE / "_archive/v3-定稿/知令合伙人计划-校园海报-v3-1080x1920.png"),
    ("v4 定稿", "中间区块左右各内缩 34rem · 节点间距 203rem · 页脚贴底靠右",
     BASE / "知令合伙人计划-校园海报-1080x1920.png"),
]

SCALE = 0.62
GAP = 34
PAD = 34
LABEL_H = 76

frames = []
for label, sub, p in PANELS:
    im = Image.open(p).convert("RGB")
    im = im.resize((round(im.width * SCALE), round(im.height * SCALE)), Image.LANCZOS)
    frames.append((label, sub, im))

w = PAD * 2 + sum(im.width for _, _, im in frames) + GAP * (len(frames) - 1)
h = PAD * 2 + LABEL_H + max(im.height for _, _, im in frames)
canvas = Image.new("RGB", (w, h), "#F2F3F9")
d = ImageDraw.Draw(canvas)
font = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 24)
font2 = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 19)

x = PAD
for label, sub, im in frames:
    d.text((x + 2, PAD + 4), label, fill="#0E1024", font=font)
    d.text((x + 2, PAD + 40), sub, fill="#626A80", font=font2)
    y = PAD + LABEL_H
    d.rectangle([x - 2, y - 2, x + im.width + 1, y + im.height + 1], outline="#D8DCF2")
    canvas.paste(im, (x, y))
    x += im.width + GAP

out = OUT / "v3-vs-v4定稿-对比.png"
canvas.save(out)
print("saved", out, canvas.size)

# -*- coding: utf-8 -*-
"""合成对比图：v2 定稿 vs v3 定稿（等比缩放 + 标签）"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path("D:/work/zhilingdoc/知令合伙人计划-校园海报")
OUT = BASE / "_draft"

PANELS = [
    ("v2 定稿：三色 logo / 横向三步 / 居中二维码 / 网址右上角小灰字",
     BASE / "_archive/v2-定稿/知令合伙人计划-校园海报-v2-1080x1920.png"),
    ("v3 定稿：应用图标 + 官方蓝字标 / 纵向三步 / 右侧网址锁排 + 二维码",
     BASE / "知令合伙人计划-校园海报-1080x1920.png"),
]

SCALE = 0.62
GAP = 34
PAD = 34
LABEL_H = 48

frames = []
for label, p in PANELS:
    im = Image.open(p).convert("RGB")
    im = im.resize((round(im.width * SCALE), round(im.height * SCALE)), Image.LANCZOS)
    frames.append((label, im))

w = PAD * 2 + sum(im.width for _, im in frames) + GAP * (len(frames) - 1)
h = PAD * 2 + LABEL_H + max(im.height for _, im in frames)
canvas = Image.new("RGB", (w, h), "#F2F3F9")
d = ImageDraw.Draw(canvas)
font = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 22)

x = PAD
for label, im in frames:
    d.text((x + 2, PAD + 12), label, fill="#0E1024", font=font)
    y = PAD + LABEL_H
    d.rectangle([x - 2, y - 2, x + im.width + 1, y + im.height + 1], outline="#D8DCF2")
    canvas.paste(im, (x, y))
    x += im.width + GAP

out = OUT / "v2-vs-v3定稿-对比.png"
canvas.save(out)
print("saved", out, canvas.size)

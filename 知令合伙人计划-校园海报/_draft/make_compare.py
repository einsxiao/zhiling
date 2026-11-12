# -*- coding: utf-8 -*-
"""合成对比图：v2 定稿 vs v3-A vs v3-B（等比缩放 + 标签）"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path("D:/work/zhilingdoc/知令合伙人计划-校园海报/_draft")
BASE = Path("D:/work/zhilingdoc/知令合伙人计划-校园海报")

PANELS = [
    ("v2 定稿（旧：三色 logo / 横向三步 / 居中二维码）", BASE / "知令合伙人计划-校园海报-1080x1920.png"),
    ("v3-A：应用图标 logo + 纵向三步 + 右侧网址/二维码", OUT / "v3-a.png"),
    ("v3-B：应用图标 logo + 全宽网址条 + 纵向三步 + 右侧二维码", OUT / "v3-b.png"),
]

SCALE = 0.42
GAP = 26
PAD = 30
LABEL_H = 46

frames = []
for label, p in PANELS:
    im = Image.open(p).convert("RGB")
    im = im.resize((int(im.width * SCALE), int(im.height * SCALE)), Image.LANCZOS)
    frames.append((label, im))

w = PAD * 2 + sum(im.width for _, im in frames) + GAP * (len(frames) - 1)
h = PAD * 2 + LABEL_H + max(im.height for _, im in frames)
canvas = Image.new("RGB", (w, h), "#F2F3F9")
d = ImageDraw.Draw(canvas)
font = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 19)

x = PAD
for label, im in frames:
    d.text((x + 2, PAD + 10), label, fill="#0E1024", font=font)
    y = PAD + LABEL_H
    d.rectangle([x - 2, y - 2, x + im.width + 1, y + im.height + 1], outline="#D8DCF2")
    canvas.paste(im, (x, y))
    x += im.width + GAP

out = OUT / "v2-vs-v3AB-对比.png"
canvas.save(out)
print("saved", out, canvas.size)

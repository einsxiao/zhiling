# -*- coding: utf-8 -*-
"""生成「产品海报 vs 校园海报」并排对比图（便于人工目检）。
不修改任何交付物，仅在 _draft/ 下产出对比图。
"""
import os
from PIL import Image, ImageDraw, ImageFont

DRAFT = r"D:/work/zhilingdoc/知令产品介绍-海报/_draft"
NEW = r"D:/work/zhilingdoc/知令产品介绍-海报/知令产品介绍-海报-1080x1920.png"
OLD = r"D:/work/zhilingdoc/知令合伙人计划-校园海报/知令合伙人计划-校园海报-1080x1920.png"
OUT = os.path.join(DRAFT, "对比-产品海报vs校园海报.png")

TARGET_H = 1400
GAP = 40
MARGIN = 40
LABEL_H = 90

def load_scaled(p):
    im = Image.open(p).convert("RGB")
    w = round(im.width * TARGET_H / im.height)
    return im.resize((w, TARGET_H), Image.LANCZOS)

a = load_scaled(NEW)
b = load_scaled(OLD)

W = MARGIN * 2 + a.width + GAP + b.width
H = LABEL_H + TARGET_H + MARGIN
canvas = Image.new("RGB", (W, H), (255, 255, 255))
d = ImageDraw.Draw(canvas)

# 中文字体
font = None
for fp in [r"C:/Windows/Fonts/msyh.ttc", r"C:/Windows/Fonts/msyhbd.ttc", r"C:/Windows/Fonts/simhei.ttf"]:
    if os.path.exists(fp):
        try:
            font = ImageFont.truetype(fp, 34)
            break
        except Exception:
            pass
label = "左：知令产品介绍（新） / 右：知令合伙人计划·校园海报（母本风格）"
if font is not None:
    try:
        d.text((MARGIN, 26), label, fill=(14, 16, 36), font=font)
    except Exception as e:
        print("文字渲染失败，已省略标注：", e)
else:
    print("未找到中文字体，已省略文字标注")

x1, y1 = MARGIN, LABEL_H
canvas.paste(a, (x1, y1))
canvas.paste(b, (x1 + a.width + GAP, y1))

canvas.save(OUT)
print("saved:", OUT, canvas.size, os.path.getsize(OUT), "bytes")
print("left size:", a.size, "right size:", b.size)

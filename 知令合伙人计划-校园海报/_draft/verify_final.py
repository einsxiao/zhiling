# -*- coding: utf-8 -*-
"""v3 定稿验证：尺寸 / 二维码解码（1x、2x、PDF）/ 合规词 / 自包含 / 溢出余量"""
import re
from pathlib import Path

import cv2
import fitz  # PyMuPDF
from PIL import Image

ROOT = Path("D:/work/zhilingdoc/知令合伙人计划-校园海报")
TARGET_URL = "https://zhiling.plus/profile/partner/"
BANNED = ["投资回报", "稳赚", "保本", "躺赚", "年化", "佣金", "收益率", "零风险", "无风险",
          "暴富", "日入", "月入", "轻松赚钱", "保证收益", "长期", "提现", "支付宝", "银行卡", "¥100"]

html = (ROOT / "知令合伙人计划-校园海报.html").read_text(encoding="utf-8")

print("--- 尺寸 ---")
for n in ["知令合伙人计划-校园海报-1080x1920.png", "知令合伙人计划-校园海报-2160x3840.png"]:
    print(f"  {n}: {Image.open(ROOT / n).size}")

print("--- PDF ---")
doc = fitz.open(ROOT / "知令合伙人计划-校园海报-A3.pdf")
page = doc[0]
print(f"  页数={doc.page_count} 页面尺寸={page.rect.width:.2f}×{page.rect.height:.2f}pt "
      f"({page.rect.width/72*25.4:.2f}×{page.rect.height/72*25.4:.2f}mm)")
pix = page.get_pixmap(dpi=150)
pdf_png = ROOT / "_draft" / "_pdf_check.png"
pix.save(pdf_png)
print(f"  PDF 文本含 'zhiling.plus': {'zhiling.plus' in page.get_text()}")

print("--- 二维码解码 ---")
det = cv2.QRCodeDetector()
for n in ["知令合伙人计划-校园海报-1080x1920.png", "知令合伙人计划-校园海报-2160x3840.png", "_draft/_pdf_check.png"]:
    img = cv2.imread(str(ROOT / n))
    data, pts, _ = det.detectAndDecode(img)
    print(f"  {n}: {'成功' if data else '失败'} 匹配目标URL={data == TARGET_URL} -> {data!r}")

print("--- 合规词扫描 ---")
text = re.sub(r"<[^>]+>", " ", re.sub(r"<style[\s\S]*?</style>", " ", html))
text = re.sub(r"\s+", " ", text).strip()
hits = [w for w in BANNED if w in text]
print(f"  禁用词命中: {hits if hits else '无'}")
print(f"  含 '年满 18 周岁': {'年满 18 周岁' in text} | 含 '以平台结算为准': {'以平台结算为准' in text}")
ext = re.findall(r'(?:src|href)\s*=\s*["\'](?!data:|#)([^"\']+)["\']', html)
print(f"  外部引用: {ext if ext else '无（自包含）'}")
print(f"  logo 源: 应用图标 #3780ff {'✓' if '#3780ff' in html else '✗'} / 官方蓝字标 #1596FF {'✓' if '#1596FF' in html else '✗'}"
      f" / 三色 logo.svg 残留 {'✗ 有' if 'lg-a' in html or '43F218' in html else '✓ 无'}")

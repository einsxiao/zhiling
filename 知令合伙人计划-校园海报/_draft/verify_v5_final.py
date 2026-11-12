# -*- coding: utf-8 -*-
"""v5 定稿验证：字标着色 / 尺寸 / 二维码解码（1x、2x、PDF）/ 合规词 / 自包含 / 溢出余量"""
import re
from collections import Counter
from pathlib import Path

import cv2
import fitz  # PyMuPDF
from PIL import Image

ROOT = Path("D:/work/zhilingdoc/知令合伙人计划-校园海报")
TARGET_URL = "https://zhiling.plus/profile/partner/"
BANNED = ["投资回报", "稳赚", "保本", "躺赚", "年化", "佣金", "收益率", "零风险", "无风险",
          "暴富", "日入", "月入", "轻松赚钱", "保证收益", "长期", "提现", "支付宝", "银行卡", "¥100"]

html = (ROOT / "知令合伙人计划-校园海报.html").read_text(encoding="utf-8")

# 1x 画布下的取样框：品牌行 x92..279 / y92..154（内边距 92 + 图标 62 + 间距 18 = 字标左缘 172）
BOX_WM = (174, 94, 278, 152)      # 「知令」字标字形区
BOX_EYEBROW = (172, 184, 430, 216)  # 眉标「知令合伙人计划」文字区（x92+34+44+18=188 起）


def dominant_box(png, box):
    """返回取样框内非白像素的主色及其占比。"""
    cnt = Counter()
    for px in Image.open(png).convert("RGB").crop(box).getdata():
        if min(px) < 246:            # 排除白底/近白
            cnt[px] += 1
    if not cnt:
        return None, 0.0, 0
    top, n = cnt.most_common(1)[0]
    return top, 100.0 * n / sum(cnt.values()), sum(cnt.values())


print("--- 字标着色（成品像素反推，不读 CSS）---")
p1 = ROOT / "知令合伙人计划-校园海报-1080x1920.png"
wm, share, tot = dominant_box(p1, BOX_WM)
ey, eshare, _ = dominant_box(p1, BOX_EYEBROW)
hx = lambda c: "#%02X%02X%02X" % c if c else "n/a"
print(f"  字标「知令」主色 = {hx(wm)}（占该区非白像素 {share:.1f}% / {tot} px）")
print(f"  眉标主色        = {hx(ey)}")
print(f"  两者是否同色（字标已并入页面主色）: {wm == ey}")

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
    print(f"  {n}: {'成功' if data else '失败'} 匹配目标URL={data == TARGET_URL}")

print("--- 合规词扫描 ---")
text = re.sub(r"<[^>]+>", " ", re.sub(r"<style[\s\S]*?</style>", " ", html))
text = re.sub(r"\s+", " ", text).strip()
hits = [w for w in BANNED if w in text]
print(f"  禁用词命中: {hits if hits else '无'}")
print(f"  含 '年满 18 周岁': {'年满 18 周岁' in text} | 含 '以平台结算为准': {'以平台结算为准' in text}")

print("--- 自包含与素材溯源 ---")
ext = re.findall(r'(?:src|href)\s*=\s*["\'](?!data:|#)([^"\']+)["\']', html)
print(f"  外部引用: {ext if ext else '无（自包含）'}")
print(f"  字标 CSS 令牌规则 .brand .wordmark g{{fill:var(--blue)}}: {'.brand .wordmark g{fill:var(--blue);}' in html}")
print(f"  字标实际着色属性 fill=\"#1596FF\" 残留: {'✗ 仍存在' if 'fill=\"#1596FF\"' in html else '✓ 已清除'}"
      f" / 字标实际着色属性 fill=\"#545BFC\": {'✓ 已就位' if 'fill=\"#545BFC\"' in html else '✗ 缺失'}")
print(f"  （HTML 内 '1596FF' 出现次数 {html.count('1596FF')}，仅允许出现在注释性说明中）")
print(f"  应用图标 #3780ff 保留: {'✓' if '#3780ff' in html else '✗'}"
      f" / 三色 logo 残留: {'✗ 有' if 'lg-a' in html or '43F218' in html else '✓ 无'}")

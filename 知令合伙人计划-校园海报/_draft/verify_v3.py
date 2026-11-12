# -*- coding: utf-8 -*-
"""v3 草稿验证：二维码解码 + 合规词扫描 + URL 呈现检查"""
import re
import sys
from pathlib import Path

import cv2

DRAFT = Path("D:/work/zhilingdoc/知令合伙人计划-校园海报/_draft")
TARGET_URL = "https://zhiling.plus/profile/partner/"

BANNED = ["投资回报", "稳赚", "保本", "躺赚", "年化", "佣金", "收益率", "零风险", "无风险",
          "暴富", "日入", "月入", "轻松赚钱", "保证收益", "长期", "提现", "支付宝", "银行卡", "¥100"]

def decode_qr(png: Path):
    img = cv2.imread(str(png))
    det = cv2.QRCodeDetector()
    data, pts, _ = det.detectAndDecode(img)
    if not data:
        data, pts, _ = det.detectAndDecodeMulti(img)[0:3] if False else (data, pts, None)
    return data, pts

def strip_tags(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>", " ", html)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html).strip()

for name in ["poster-v3a.html", "poster-v3b.html"]:
    p = DRAFT / name
    raw = p.read_text(encoding="utf-8")
    text = strip_tags(raw)
    print(f"=== {name} ===")
    print(f"  可见文本长度: {len(text)}")
    hits = [w for w in BANNED if w in text]
    print(f"  禁用词命中: {hits if hits else '无'}")
    print(f"  含 'https://': {'https://' in text}  |  含 'zhiling.plus': {'zhiling.plus' in text}")
    print(f"  含 '年满 18 周岁': {'年满 18 周岁' in text}  |  含 '以平台结算为准': {'以平台结算为准' in text}")
    ext = re.findall(r'(?:src|href)\s*=\s*["\'](?!data:|#)([^"\']+)["\']', raw)
    print(f"  外部引用: {ext if ext else '无（自包含）'}")

for name in ["v3-a.png", "v3-b.png"]:
    p = DRAFT / name
    data, pts = decode_qr(p)
    ok = (data == TARGET_URL)
    print(f"=== {name} === 解码={'成功' if data else '失败'} 匹配目标URL={ok}")
    print(f"  内容: {data!r}")

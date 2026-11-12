# -*- coding: utf-8 -*-
"""独立（对抗性）校验 · C 尺寸与文件 + D 自包含/合规/二维码 + G 品牌像素
只读交付物，不做任何修改。输出 JSON 报告。

v4 更新要点：二维码断言由「检测 = 无」改为「存在且解码内容 == https://zhiling.plus」，
并追加四路解码（1x/2x PNG、A3 PDF 渲染页、备用光栅 PNG）与静区像素核查。
"""
import json, os, re
from PIL import Image
import fitz  # PyMuPDF
import cv2
import numpy as np

DIR = r"D:/work/zhilingdoc/知令产品介绍-海报"
P1 = os.path.join(DIR, "知令产品介绍-海报-1080x1920.png")
P2 = os.path.join(DIR, "知令产品介绍-海报-2160x3840.png")
PDF = os.path.join(DIR, "知令产品介绍-海报-A3.pdf")
HTML = os.path.join(DIR, "知令产品介绍-海报.html")
SCRIPT = os.path.join(DIR, "_scripts", "export_poster.ps1")
GENQR = os.path.join(DIR, "_scripts", "gen_qr.mjs")
QRSVG = os.path.join(DIR, "_scripts", "qr-site.svg")
QRPNG = os.path.join(DIR, "二维码-知令官网.png")
EXPECT = "https://zhiling.plus"

rep = {}

# ---------- C 尺寸与文件 ----------
def png_size(p):
    with Image.open(p) as im:
        return {"w": im.width, "h": im.height, "mode": im.mode, "bytes": os.path.getsize(p)}

rep["C_png"] = {"png1": png_size(P1), "png2": png_size(P2)}

doc = fitz.open(PDF)
pg = doc[0]
w_pt, h_pt = pg.rect.width, pg.rect.height
pdf_text = "\n".join(p.get_text() for p in doc)
rep["C_pdf"] = {
    "pages": doc.page_count,
    "mediabox_pt": [round(w_pt, 2), round(h_pt, 2)],
    "mediabox_mm": [round(w_pt / 72 * 25.4, 2), round(h_pt / 72 * 25.4, 2)],
    "bytes": os.path.getsize(PDF),
    "text_has_zhiling.plus": "zhiling.plus" in pdf_text,
    "text_has_知令": "知令" in pdf_text,
    "text_len": len(pdf_text),
}

rep["C_files"] = {}
for f in [HTML, P1, P2, PDF, SCRIPT, GENQR, QRSVG, QRPNG]:
    rep["C_files"][os.path.basename(f)] = {"exists": os.path.exists(f), "bytes": os.path.getsize(f) if os.path.exists(f) else None}

# ---------- D1 自包含 ----------
h = open(HTML, encoding="utf-8").read()
ext_refs = re.findall(r'(?:src|href)\s*=\s*"(?!data:|#)[^"]*"', h)
http_literals = re.findall(r'https?://[^\s"\'<>)]+', h)
rep["D_selfcontained"] = {
    "external_refs": ext_refs,
    "external_ref_count": len(ext_refs),
    "http_literals": http_literals,
    "has_img_tag": bool(re.search(r"<img\b", h, re.I)),
    "has_link_stylesheet": bool(re.search(r"<link\b[^>]*stylesheet", h, re.I)),
    "has_script_src": bool(re.search(r"<script\b[^>]*\bsrc\s*=", h, re.I)),
    "has_inline_svg": bool(re.search(r"<svg\b", h, re.I)),
    "qr_is_inline_svg": bool(re.search(r'<svg[^>]*viewBox="0 0 33 33"', h)),
}

# ---------- D2 二维码：存在性 + 四路可解码 + 静区 ----------
qr_words = re.findall(r"qrcode|qrcard|qr-|二维码", h, re.I)
rep["D_qr_html"] = {"hits": qr_words, "count": len(qr_words),
                    "decode_expect": EXPECT}

det = cv2.QRCodeDetector()
def qr_decode(img_bgr):
    data, pts, _ = det.detectAndDecode(img_bgr)
    return {"decoded": data or "", "points_found": pts is not None,
            "ok": (data == EXPECT),
            "points": None if pts is None else np.array(pts).reshape(-1, 2).round(1).tolist()}

def as_bgr(p):
    im = Image.open(p).convert("RGB")
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

img1 = as_bgr(P1)
img2 = as_bgr(P2)
imgq = as_bgr(QRPNG)
rep["D_qr_png1"] = qr_decode(img1)
rep["D_qr_png2"] = qr_decode(img2)
rep["D_qr_qrpng"] = qr_decode(imgq)

# PDF 渲染页（dpi=200 >=150）→ 二维码检测
pix = pg.get_pixmap(dpi=200)
arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
if pix.n == 4:
    arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
elif pix.n == 3:
    arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
rep["D_qr_pdf"] = qr_decode(arr)
rep["D_qr_pdf_render"] = {"w": pix.width, "h": pix.height, "dpi": 200}

# 静区像素核查（1x PNG，已知 svg 盒 x654-874 / y1425-1645）
qr_box = (654, 1425, 874, 1645)
sub = img1[qr_box[1]:qr_box[3], qr_box[0]:qr_box[2]]
gray = cv2.cvtColor(sub, cv2.COLOR_BGR2GRAY)
ys, xs = np.where(gray < 120)
if len(xs):
    bx0, bx1, by0, by1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
    module = (bx1 - bx0 + 1) / 25.0
    m = {"left": bx0, "top": by0, "right": sub.shape[1] - 1 - bx1, "bottom": sub.shape[0] - 1 - by1}
    rep["D_qr_quiet_zone"] = {
        "dark_bbox_local_xyxy": [bx0, by0, bx1, by1],
        "dark_wh": [bx1 - bx0 + 1, by1 - by0 + 1],
        "module_px_est": round(module, 3),
        "white_margin_px": m,
        "white_margin_modules": {k: round(v / module, 2) for k, v in m.items()},
        "PASS_min4mod": all(v >= 4 * module * 0.95 for v in m.values()),
    }
else:
    rep["D_qr_quiet_zone"] = {"error": "未检出深色模块", "PASS_min4mod": False}

rep["D_qr_all_pass"] = all(rep[k]["ok"] for k in ["D_qr_png1", "D_qr_png2", "D_qr_pdf", "D_qr_qrpng"]) \
    and rep["D_qr_quiet_zone"].get("PASS_min4mod", False)

# ---------- D3 禁用词 ----------
banned = ['Token 券', '合伙人', '分红', '返佣', '提现', '收益', '邀请', '18 周岁',
          'Hermes', 'Nous Research', 'OpenClaw', '保本', '稳赚', '投资回报', '年化']
rep["D_banned"] = {"list": banned, "hits": [w for w in banned if w in h]}

# ---------- D4 必备内容 ----------
required = ['科研工作', '世界顶级模型', '日常高频', '图像与视频', 'Office 文档', '工程与计算',
            '多端协同', '数据安全', 'zhiling.plus', '¥10', '1M', '开箱即用', '不掺水', '不降智',
            'GPT-6 Astra Pro', 'Claude Fable 5', 'DeepSeek-V4.1-Flash', 'SLURM', '司诏',
            'Nano Banana Pro', 'Veo 3.1', '本地剪辑与转码', '扫码访问知令官网']
rep["D_required"] = {"missing": [w for w in required if w not in h]}

# ---------- D5 品牌像素抽样（1x PNG） ----------
im = Image.open(P1).convert("RGB")
def dominant(box, skip_white=235):
    crop = im.crop(box)
    cnt = {}
    for (r, g, b) in crop.getdata():
        if r > skip_white and g > skip_white and b > skip_white:
            continue
        cnt[(r, g, b)] = cnt.get((r, g, b), 0) + 1
    top = sorted(cnt.items(), key=lambda kv: -kv[1])[:3]
    return [{"hex": "#%02x%02x%02x" % c, "n": n} for c, n in top]

rep["D_brand_pixels"] = {
    "wordmark_region": dominant((174, 94, 279, 153)),   # 字标字形区
    "eyebrow_region": dominant((188, 174, 988, 204)),   # 眉标文字区（含 --blue 短线）
    "appicon_region": dominant((92, 92, 155, 155)),     # 应用图标区
    "appicon_title_line": dominant((92, 92, 988, 155)), # 品牌整行
}

print(json.dumps(rep, ensure_ascii=False, indent=1))

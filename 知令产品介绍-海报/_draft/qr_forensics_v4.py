# -*- coding: utf-8 -*-
"""v4 独立（对抗性）校验 · 二维码存在性 / 四路可解码 / 静区核查
只读交付物，不做任何修改；失败时把裁剪图落到 _draft/ 取证。
输出 JSON。
"""
import json, os
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
import cv2

DIR = r"D:/work/zhilingdoc/知令产品介绍-海报"
DRAFT = os.path.join(DIR, "_draft")
P1 = os.path.join(DIR, "知令产品介绍-海报-1080x1920.png")
P2 = os.path.join(DIR, "知令产品介绍-海报-2160x3840.png")
PDF = os.path.join(DIR, "知令产品介绍-海报-A3.pdf")
QRPNG = os.path.join(DIR, "二维码-知令官网.png")
EXPECT = "https://zhiling.plus"

rep = {}

def bgr_from_pil(p):
    im = Image.open(p).convert("RGB")
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR), im.size

def decode_full(img_bgr):
    """整图直接 decode（单码），再退化为多码，再退化为右侧行动区裁剪放大。"""
    det = cv2.QRCodeDetector()
    out = {}
    data, pts, _ = det.detectAndDecode(img_bgr)
    out["full_single"] = {"ok": bool(data), "text": data, "points_found": pts is not None,
                          "points": None if pts is None else np.array(pts).reshape(-1, 2).round(1).tolist()}
    if data:
        out["decoded"] = data
        out["route"] = "full_single"
        return out
    ok, datas, ptsm, _ = det.detectAndDecodeMulti(img_bgr)
    out["full_multi"] = {"ok": bool(ok) and any(datas), "texts": list(datas) if datas else [],
                         "n_points": 0 if ptsm is None else len(ptsm)}
    if ok and any(datas):
        out["decoded"] = [d for d in datas if d][0]
        out["route"] = "full_multi"
        return out
    # 右侧行动区裁剪 + 2x 放大
    h, w = img_bgr.shape[:2]
    crop = img_bgr[int(h*0.66):int(h*0.90), int(w*0.55):int(w*0.92)]
    big = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
    data2, pts2, _ = det.detectAndDecode(big)
    out["crop_zoom"] = {"ok": bool(data2), "text": data2, "crop_wh": [crop.shape[1], crop.shape[0]]}
    out["decoded"] = data2 if data2 else ""
    out["route"] = "crop_zoom"
    return out

# 1) 1x PNG
img1, sz1 = bgr_from_pil(P1)
rep["png1"] = {"size": list(sz1), "decode": decode_full(img1)}
rep["png1"]["PASS"] = rep["png1"]["decode"]["decoded"] == EXPECT

# 2) 2x PNG
img2, sz2 = bgr_from_pil(P2)
rep["png2"] = {"size": list(sz2), "decode": decode_full(img2)}
rep["png2"]["PASS"] = rep["png2"]["decode"]["decoded"] == EXPECT

# 3) PDF 第 1 页，dpi=200 (>=150)
doc = fitz.open(PDF)
pg = doc[0]
pix = pg.get_pixmap(dpi=200)
arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
if pix.n == 4:
    arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
elif pix.n == 3:
    arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
rep["pdf"] = {"render_wh": [pix.width, pix.height], "dpi": 200, "decode": decode_full(arr)}
rep["pdf"]["PASS"] = rep["pdf"]["decode"]["decoded"] == EXPECT

# 4) 备用光栅
imgq, szq = bgr_from_pil(QRPNG)
rep["qr_png"] = {"size": list(szq), "bytes": os.path.getsize(QRPNG), "decode": decode_full(imgq)}
rep["qr_png"]["PASS"] = rep["qr_png"]["decode"]["decoded"] == EXPECT

# 5) 静区核查（在 1x PNG 上，像素级）
#    已知几何：qrcard x664->918 y1404->1658；qr svg x681->901 y1421->1641（1rem=1px）
qr_box = (681, 1421, 901, 1641)  # x0,y0,x1,y1
sub = img1[qr_box[1]:qr_box[3], qr_box[0]:qr_box[2]]
gray = cv2.cvtColor(sub, cv2.COLOR_BGR2GRAY)
dark = gray < 120
ys, xs = np.where(dark)
if len(xs):
    bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
    dark_w = bx1 - bx0 + 1
    dark_h = by1 - by0 + 1
    # QR version2 => 25 data modules across the dark bbox (finder to finder)
    module = dark_w / 25.0
    # 向外扩，找到第一个非白像素（白=所有通道>245）
    def margin_from(edge, direction, axis):
        # direction: -1 left/up, +1 right/down
        pos = edge
        cnt = 0
        while 0 <= pos < (sub.shape[axis]) :
            if axis == 1:
                row = sub[pos, :, :]
                line_white = np.all(row > 245)
            else:
                col = sub[:, pos, :]
                line_white = np.all(col > 245)
            # 若整行/整列出现非白像素则停
            if not line_white:
                break
            cnt += 1
            pos += direction
        return cnt
    m_left = bx0  # 到 svg 左边缘
    m_top = by0
    m_right = sub.shape[1] - 1 - bx1
    m_bottom = sub.shape[0] - 1 - by1
    rep["quiet_zone"] = {
        "svg_box_1x": qr_box,
        "dark_bbox_local": [int(bx0), int(by0), int(bx1), int(by1)],
        "dark_wh": [int(dark_w), int(dark_h)],
        "module_px_est": round(module, 3),
        "white_margin_px": {"left": int(m_left), "top": int(m_top), "right": int(m_right), "bottom": int(m_bottom)},
        "white_margin_modules": {
            "left": round(m_left/module, 2), "top": round(m_top/module, 2),
            "right": round(m_right/module, 2), "bottom": round(m_bottom/module, 2)},
        "PASS_min4mod": all(v >= 4*module*0.95 for v in (m_left, m_top, m_right, m_bottom)),
    }
    if not rep["quiet_zone"]["PASS_min4mod"]:
        crop = img1[max(0,qr_box[1]-40):qr_box[3]+40, max(0,qr_box[0]-40):qr_box[2]+40]
        cv2.imwrite(os.path.join(DRAFT, "取证-静区不足.png"), crop)
else:
    rep["quiet_zone"] = {"error": "在预期 svg 区域内未检出深色模块", "PASS_min4mod": False}
    cv2.imwrite(os.path.join(DRAFT, "取证-未检出二维码-1x.png"),
                img1[1380:1680, 640:940])

print(json.dumps(rep, ensure_ascii=False, indent=1))

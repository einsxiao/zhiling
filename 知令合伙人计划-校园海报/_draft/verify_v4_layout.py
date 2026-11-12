# -*- coding: utf-8 -*-
"""v4 版式独立像素复核：不依赖 CSS，直接读成品 PNG 反推版式坐标。
校验点：
  1) 页脚小字贴底靠右（底边距、右缘、左缘起止）
  2) 中间两栏左右留白（三步节点左缘 / 二维码卡片右缘 / 取景角标右缘）
  3) 三步纵向高度（相邻节点圆心间距，与 v3 对比）
  4) 二维码码图尺寸（期望 308rem）
  5) 画布满幅（左右边缘不得出现白边）
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

BASE = Path("D:/work/zhilingdoc/知令合伙人计划-校园海报")
CUR = BASE / "知令合伙人计划-校园海报-1080x1920.png"
OLD = BASE / "_archive/v3-定稿/知令合伙人计划-校园海报-v3-1080x1920.png"

DARK = 720  # sum(RGB) < 720 视为「有墨」，可滤掉 6% 透明度的浅色装饰


def load(p):
    return np.asarray(Image.open(p).convert("RGB")).astype(np.int32)


def ink_bbox(a, y0, y1, x0=0, x1=None):
    x1 = a.shape[1] if x1 is None else x1
    sub = a[y0:y1, x0:x1].sum(axis=2) < DARK
    ys, xs = np.nonzero(sub)
    if len(xs) == 0:
        return None
    return (x0 + xs.min(), y0 + ys.min(), x0 + xs.max(), y0 + ys.max())


def qr_box(p):
    img = cv2.imread(str(p))
    det = cv2.QRCodeDetector()
    data, pts, _ = det.detectAndDecode(img)
    if pts is None:
        return None, None
    pts = pts.reshape(-1, 2)
    return (pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()), data


def step_centers(p, y0, y1, x0, x1):
    """在给定窗口内找蓝色圆环节点的圆心（按连通块聚类，取纵向中心）"""
    a = load(p)
    sub = a[y0:y1, x0:x1]
    # 品牌蓝 #545BFC 附近
    d = np.abs(sub - np.array([84, 91, 252])).sum(axis=2)
    mask = (d < 180).astype(np.uint8)
    n, _, stats, cents = cv2.connectedComponentsWithStats(mask, 8)
    blobs = [(int(stats[i, 1] + y0), int(cents[i][1] + y0), int(stats[i, 4]))
             for i in range(1, n) if stats[i, 4] > 250]
    blobs.sort()
    return blobs


print("=== v4 像素级复核（1080x1920 成品）===")
a = load(CUR)
H, W = a.shape[:2]
print(f"画布: {W}x{H}")

# 1) 页脚：贴底靠右
b = ink_bbox(a, 1640, 1920, 300, W)
print(f"页脚墨迹包围盒: x {b[0]}→{b[2]}, y {b[1]}→{b[3]}"
      f" | 距画布底 {H - b[3]} | 右缘距画布右 {W - b[2]} | 左缘距画布左 {b[0]}")

# 2) 中间两栏左右留白（取三步/二维码所在纵向带）
band = ink_bbox(a, 1180, 1580, 0, 500)
print(f"三步区（y1180-1580, x<500）最左墨迹: {band[0]}  ← 期望 ≈126（画布内边距 92 + 内缩 34）")
band2 = ink_bbox(a, 1150, 1600, 900, W)
print(f"二维码区最右墨迹: {band2[2]}      ← 期望 ≈968（卡片右缘 954 + 角标外扩 14）")

# 3) 二维码码图
qb, data = qr_box(CUR)
print(f"二维码解码: {data!r}")
print(f"码图包围盒: x {qb[0]:.0f}→{qb[2]:.0f} (宽 {qb[2]-qb[0]:.0f}) "
      f"y {qb[1]:.0f}→{qb[3]:.0f} (高 {qb[3]-qb[1]:.0f})  ← 期望 308")

# 4) 三步节点：v4 vs v3
for tag, p in (("v4", CUR), ("v3", OLD)):
    bl = step_centers(p, 1050, 1650, 80, 340)
    cys = [c for _, c, _ in bl]
    gaps = [cys[i + 1] - cys[i] for i in range(len(cys) - 1)]
    print(f"{tag} 三步节点（连通块 y,面积）= {bl} → 圆心 y {cys} → 间距 {gaps}")

# 5) 画布满幅：最左/最右 2 列是否纯白
edge_l = a[:, :2].sum(axis=2).min()
edge_r = a[:, -2:].sum(axis=2).min()
print(f"画布左/右边缘 2 列最小色值和: {edge_l} / {edge_r}（<765 表示有内容贴边，非白边）")

# -*- coding: utf-8 -*-
"""从系统 CJK 字体中提取「知令」字形轮廓，生成可内联的矢量字标 SVG。

背景：主项目提供的 assets_zhiling/slogon.svg（= assets_zhiling/logos.jsx 的
AppTextLogo）经实测渲染为「智灵+」，并非「知令」字标；为保证海报品牌名正确，
且仍满足"单文件自包含矢量"要求，此处从系统字体（默认 微软雅黑 Bold）提取
「知令」两字的矢量轮廓，生成独立的内联 SVG 字标。

兼容性说明：本机 python 的 fontTools 部分模块为 mypyc 编译产物（bezierTools.pyd），
被系统"应用程序控制策略"拦截。此处仅需字形轮廓、无需精确包围盒，
故注入一个纯 Python 空桩绕过该编译模块。

用法（PowerShell，cwd = 交付目录）：
  python _scripts/gen_wordmark.py [字体文件] [输出 SVG 路径]
  · 省略参数时使用默认值；默认输出路径即交付文件 _scripts/wordmark-zhiling.svg，
    重跑会**原地覆盖**该交付文件（脚本会在使用默认值时打印警告）。
产物：
  _scripts/wordmark-zhiling.svg   「知令」矢量字标（fill #1B1F35，可内联进 HTML）
"""
import sys
import types

# --- 绕过被策略拦截的编译模块（仅用于导入，不参与实际计算） ---
try:
    import fontTools.misc  # noqa: F401
    _stub = types.ModuleType("fontTools.misc.bezierTools")
    def _noop(*a, **k):
        return None
    for _n in ("calcCubicBounds", "calcQuadraticBounds",
               "calcCubicArcLength", "calcQuadraticArcLength",
               "splitCubic", "splitQuadratic", "solveCubic", "solveQuadratic"):
        setattr(_stub, _n, _noop)
    sys.modules.setdefault("fontTools.misc.bezierTools", _stub)
except Exception:
    pass

from fontTools.ttLib import TTFont, TTCollection
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

FONT = sys.argv[1] if len(sys.argv) > 1 else r"C:/Windows/Fonts/msyhbd.ttc"
CHARS = "知令"
FILL = "#1B1F35"
# 输出路径：可用第 2 个命令行参数覆盖；默认值即正式交付文件，重跑会原地覆盖，故打印警告。
DEFAULT_OUT = r"D:/work/zhilingdoc/知令合伙人计划-校园海报/_scripts/wordmark-zhiling.svg"
OUT = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT
if len(sys.argv) > 2:
    print("[信息] 输出路径由命令行指定：", OUT)
else:
    print("[警告] 未指定输出路径，将写入默认交付路径（会原地覆盖交付文件）：", OUT)
    print("[警告] 如需避免覆盖交付文件，请改用：")
    print('       python _scripts/gen_wordmark.py "<字体文件>" "<输出SVG路径>"')


class BBoxPen:
    """极简包围盒笔：记录所有控制点，回避 bezierTools 依赖。"""

    def __init__(self):
        self.xmin = self.ymin = float("inf")
        self.xmax = self.ymax = float("-inf")

    def _upd(self, pt):
        if pt is None:
            return
        x, y = pt
        self.xmin = min(self.xmin, x)
        self.xmax = max(self.xmax, x)
        self.ymin = min(self.ymin, y)
        self.ymax = max(self.ymax, y)

    def moveTo(self, pt):
        self._upd(pt)

    def lineTo(self, pt):
        self._upd(pt)

    def curveTo(self, *pts):
        for p in pts:
            self._upd(p)

    def qCurveTo(self, *pts):
        for p in pts:
            self._upd(p)

    def closePath(self):
        pass

    def endPath(self):
        pass

    def addComponent(self, glyphName, transform):
        pass


# 打开字体（支持 ttc 集合）
try:
    font = TTCollection(FONT).fonts[0]
except Exception:
    font = TTFont(FONT, fontNumber=0)

upm = font["head"].unitsPerEm
cmap = font.getBestCmap()
glyphset = font.getGlyphSet()
hmtx = font["hmtx"]

x = 0
d_parts = []
bbox = BBoxPen()
for ch in CHARS:
    gname = cmap[ord(ch)]
    t = Transform(1, 0, 0, -1, x, 0)  # 翻转 y 轴 + 按 advance 平移

    spen = SVGPathPen(glyphset)
    glyphset[gname].draw(TransformPen(spen, t))
    d_parts.append(spen.getCommands())

    glyphset[gname].draw(TransformPen(bbox, t))
    x += hmtx[gname][0]

d = "".join(d_parts)
pad_x = upm * 0.02
pad_y = upm * 0.03
minx = bbox.xmin - pad_x
maxx = bbox.xmax + pad_x
miny = bbox.ymin - pad_y
maxy = bbox.ymax + pad_y
w = maxx - minx
h = maxy - miny

svg = (
    '<svg xmlns="http://www.w3.org/2000/svg" '
    f'viewBox="{minx:.1f} {miny:.1f} {w:.1f} {h:.1f}" '
    'preserveAspectRatio="xMidYMid meet" role="img" aria-label="知令">'
    f'<path fill="{FILL}" d="{d}"/></svg>'
)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)

print("OK:", OUT)
print("viewBox:", f"{minx:.1f} {miny:.1f} {w:.1f} {h:.1f}", "chars:", CHARS)
print("svg-len:", len(svg))

"""裁切「知令产品介绍-海报」1x PNG 的行动区，便于目检对称性。
用法: python crop_action.py <in.png> <out.png> [top] [bottom]
"""
import sys
from PIL import Image

src = sys.argv[1]
dst = sys.argv[2]
top = int(sys.argv[3]) if len(sys.argv) > 3 else 1370
bottom = int(sys.argv[4]) if len(sys.argv) > 4 else 1735

im = Image.open(src)
im.crop((0, top, im.width, bottom)).save(dst)
print("saved", dst, im.size, "->", (im.width, bottom - top))
